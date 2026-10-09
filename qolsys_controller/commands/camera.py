"""Opt-in local panel-camera snapshots, verified on IQ Panel 2+ firmware 2.8.1."""

from __future__ import annotations

import asyncio
import base64
import binascii
import json
import logging
import re
import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any

from qolsys_controller.errors import QolsysOperationError, QolsysSnapshotError
from qolsys_controller.mqtt_command import MQTTCommand, MQTTCommand_IpcCall

if TYPE_CHECKING:
    from qolsys_controller.controller import QolsysController

_CAMERA_URI = "content://com.qolsys.qolsysprovider.CameraRequestContentProvider/camerarequest"
_MAX_ENCODED_SIZE = 8_000_000
_SNAPSHOT_DESCRIPTION = "Local snapshot"

LOGGER = logging.getLogger(__name__)


class PhotoDirectory(StrEnum):
    DISARM = "DisarmPhotos"
    ALARM = "Alarmphotos"
    PEEK_IN = "PeekInPhotos"


@dataclass(frozen=True)
class CameraSnapshot:
    """Downloaded JPEG and its panel request's identity."""

    jpeg: bytes
    request_id: str
    filename: str
    retained_on_panel: bool


class CameraCommands:
    """Request-driven still images; this does not enable continuous recording."""

    def __init__(self, controller: QolsysController) -> None:
        self._controller = controller
        self._capture_lock = asyncio.Lock()

    async def _request(self, event: str, fields: dict[str, Any]) -> dict[str, Any]:
        command = MQTTCommand(self._controller, event)
        for key, value in fields.items():
            command.append(key, value)
        return await command.send_command()

    async def _verify(self, condition: Callable[[], Awaitable[bool]], attempts: int = 5, delay: float = 0.4) -> bool:
        """Poll an eventually-consistent panel read until it confirms, bounded.

        The panel's content provider is not read-after-write consistent, so a
        delete can still read back briefly. Retry the verification before failing.
        """
        for attempt in range(attempts):
            if await condition():
                return True
            if attempt + 1 < attempts:
                await asyncio.sleep(delay)
        return False

    async def download_photo(self, directory: PhotoDirectory, filename: str) -> bytes:
        """Download one known JPEG, with no directory enumeration or traversal."""
        directory = PhotoDirectory(directory)
        if (
            not filename
            or PurePosixPath(filename).name != filename
            or "\\" in filename
            or not filename.lower().endswith(".jpg")
        ):
            raise ValueError("A single existing JPEG filename is required")
        response = await self._request(
            "photoFrameImageDownloadRequest", {"directory": directory.value, "photoFrameImageName": filename}
        )
        encoded = response.get("photoFrameImageString")
        if not isinstance(encoded, str) or not encoded or len(encoded) > _MAX_ENCODED_SIZE:
            raise QolsysOperationError("Panel returned no bounded photo")
        try:
            jpeg = base64.b64decode("".join(encoded.split()), validate=True)
        except (ValueError, binascii.Error) as error:
            raise QolsysOperationError("Panel returned invalid photo encoding") from error
        # IQ2 downloads include the camera buffer's zero padding after JPEG EOI.
        jpeg = jpeg.rstrip(b"\x00")
        if not jpeg.startswith(b"\xff\xd8") or not jpeg.endswith(b"\xff\xd9"):
            raise QolsysOperationError("Panel returned data other than a complete JPEG")
        return jpeg

    async def _cleanup_capture(self, request_id: str, filename: str) -> None:
        """Remove only the generated photo and its own local-only metadata."""
        if not re.fullmatch(re.escape(request_id) + r"_[0-9]+\.jpg", filename):
            raise QolsysOperationError("Unexpected snapshot filename; cleanup stopped")
        # IQ2 transaction 7 only exposes Alarmphotos and AlarmVideos roots.
        # Its named-file remove can reach the adjacent PeekInPhotos directory.
        # This fixed relative prefix is never supplied by an API caller.
        command = MQTTCommand_IpcCall(self._controller, "qcamservice", "qcamservice", 7)
        command.append_ipc_request(
            [{"dataType": "int", "dataValue": 1}, {"dataType": "string", "dataValue": "../PeekInPhotos/" + filename}]
        )
        response = await command.send_command()
        if response.get("responseStatus") != "success":
            raise QolsysOperationError("Panel refused snapshot file cleanup")

        async def file_absent() -> bool:
            check = await self._request(
                "photoFrameImageDownloadRequest",
                {"directory": PhotoDirectory.PEEK_IN.value, "photoFrameImageName": filename},
            )
            return not (
                check.get("photoFrameImageString")
                or check.get("directory") != PhotoDirectory.PEEK_IN.value
                # IQ2 clears the echoed filename when the named file is absent.
                or check.get("photoFrameImageName") not in (filename, "")
                or check.get("eventName") != "photoFrameImageDownloadRequest"
            )

        if not await self._verify(file_absent):
            raise QolsysOperationError("Snapshot file cleanup could not be verified; metadata retained")
        await self._request(
            "database",
            {
                "dbOperation": "delete",
                "uri": _CAMERA_URI,
                "selection": f"request_id='{request_id}' AND user_id=-2 AND description='{_SNAPSHOT_DESCRIPTION}'",
            },
        )

        async def row_absent() -> bool:
            check = await self._request(
                "database",
                {"dbOperation": "read", "uri": _CAMERA_URI, "projection": "[name]", "selection": f"request_id='{request_id}'"},
            )
            return check.get("responseStatus") == "success" and check.get("resultSet") == []

        if not await self._verify(row_absent):
            raise QolsysOperationError("Snapshot metadata cleanup could not be verified")

    async def _wait_for_capture(self, request_id: str) -> str:
        """Follow the panel's callback filename instead of guessing from clocks."""
        while True:
            response = await self._request(
                "database",
                {"dbOperation": "read", "uri": _CAMERA_URI, "projection": "[name]", "selection": f"request_id='{request_id}'"},
            )
            records = response.get("resultSet") or []
            filename = (
                records[0].get("name") if isinstance(records, list) and records and isinstance(records[0], dict) else None
            )
            if filename:
                if not isinstance(filename, str) or not re.fullmatch(re.escape(request_id) + r"_[0-9]+\.jpg", filename):
                    raise QolsysOperationError("Panel returned an unrelated capture filename")
                return filename
            await asyncio.sleep(0.5)

    async def capture_snapshot(self, *, timeout: float = 20, retain_on_panel: bool = False) -> CameraSnapshot:
        """Capture and retrieve a new Peek-In image, then clean up its panel copy.

        Each call creates one camera-request record and saved image. No background
        polling or live stream is started. Firmware 2.8.1's user_id=-2 sentinel
        suppresses ADC upload. Set retain_on_panel=True to keep the panel copy.
        The timeout bounds capture and download, not cleanup. If cleanup fails,
        the downloaded image is still returned with retained_on_panel=True; pass
        its request_id to cleanup_snapshot to retry. A failed or interrupted
        capture raises QolsysSnapshotError carrying the request ID.
        """
        if timeout <= 0:
            raise ValueError("Snapshot timeout must be positive")
        async with self._capture_lock:
            request_id = str(uuid.uuid4())
            now = int(time.time() * 1000)
            metadata = {
                "request_id": request_id,
                "type": "PEEK_IN",
                "file_type": "IMAGE",
                "description": _SNAPSHOT_DESCRIPTION,
                "create_time": now,
                "update_time": now,
                "partition_id": 0,
                "user_id": -2,
                "zone_id": 0,
                "camera_source": 129,
                "imageId": 0,
            }
            try:
                async with asyncio.timeout(timeout):
                    inserted = await self._request(
                        "database", {"dbOperation": "insert", "uri": _CAMERA_URI, "contentValues": json.dumps(metadata)}
                    )
                    if str(inserted.get("longValue")) != "1":
                        raise QolsysOperationError("Panel refused snapshot request metadata")
                    command = MQTTCommand_IpcCall(self._controller, "qcamservice", "qcamservice", 3)
                    command.append_ipc_request(
                        [
                            {"dataType": "string", "dataValue": request_id},
                            {"dataType": "string", "dataValue": "/sdcard/PeekInPhotos"},
                        ]
                    )
                    response = await command.send_command()
                    if response.get("responseStatus") != "success":
                        raise QolsysOperationError("Panel refused still capture")
                    filename = await self._wait_for_capture(request_id)
                    jpeg = await self.download_photo(PhotoDirectory.PEEK_IN, filename)
            except TimeoutError as error:
                raise QolsysSnapshotError("Snapshot timed out", request_id) from error
            except QolsysOperationError as error:
                raise QolsysSnapshotError(str(error), request_id) from error
            if retain_on_panel:
                return CameraSnapshot(jpeg, request_id, filename, retained_on_panel=True)
            try:
                await self._cleanup_capture(request_id, filename)
            except QolsysOperationError:
                LOGGER.warning("Snapshot %s was downloaded, but its panel copy remains", request_id, exc_info=True)
                return CameraSnapshot(jpeg, request_id, filename, retained_on_panel=True)
            return CameraSnapshot(jpeg, request_id, filename, retained_on_panel=False)

    async def cleanup_snapshot(self, request_id: str) -> None:
        """Remove a snapshot this API created, using the request ID it reported.

        Records not created by capture_snapshot are never matched. A capture the
        panel has not completed yet is left in place; retry after it finishes.
        """
        if str(uuid.UUID(request_id)) != request_id:
            raise ValueError("A snapshot request ID is required")
        async with self._capture_lock:
            response = await self._request(
                "database",
                {
                    "dbOperation": "read",
                    "uri": _CAMERA_URI,
                    "projection": "[name]",
                    "selection": f"request_id='{request_id}' AND user_id=-2 AND description='{_SNAPSHOT_DESCRIPTION}'",
                },
            )
            records = response.get("resultSet")
            if response.get("responseStatus") != "success" or not isinstance(records, list):
                raise QolsysOperationError("Snapshot metadata could not be read")
            if not records:
                return
            filename = records[0].get("name") if isinstance(records[0], dict) else None
            if not filename:
                raise QolsysOperationError("Snapshot capture has not completed; retry cleanup later")
            await self._cleanup_capture(request_id, filename)
