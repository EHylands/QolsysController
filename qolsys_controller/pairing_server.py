from __future__ import annotations

import asyncio
import logging
import random
import ssl

import aiofiles
from zeroconf._exceptions import NonUniqueNameException

from .errors import QolsysConfigError
from .mdns import QolsysMDNS
from .pki import QolsysPKI
from .settings import QolsysSettings

LOGGER = logging.getLogger(__name__)


class QolsysPairingServer:
    def __init__(
        self,
        settings: QolsysSettings,
        pki: QolsysPKI,
    ) -> None:
        self._settings = settings
        self._pki = pki
        self._mdns_server: QolsysMDNS | None = None
        self._server: asyncio.Server | None = None
        self._server_task: asyncio.Task[None] | None = None
        self._pairing_done = asyncio.Event()
        self._pairing_port: int = 0
        self._closed = False

    @property
    def pairing_port(self) -> int | None:
        return self._pairing_port

    async def start(self) -> None:
        if self._server is not None:
            return

        if not self._settings.check_plugin_ip():
            raise QolsysConfigError("Plugin IP Address not configured")

        self._pairing_port = random.randint(50000, 55000)

        await self._start_mdns()
        await self._start_server()

    async def wait_until_paired(self) -> None:
        await self._pairing_done.wait()

    async def stop(self) -> None:
        if self._closed:
            return

        self._closed = True

        if self._server_task is not None:
            self._server_task.cancel()

            try:
                await self._server_task
            except asyncio.CancelledError:
                pass

            self._server_task = None

        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        if self._mdns_server is not None:
            await self._mdns_server.stop_mdns()
            self._mdns_server = None

        LOGGER.debug("Pairing Server - Stopped")

    async def _start_mdns(self) -> None:
        LOGGER.debug("Pairing Server - Starting mDNS Service Discovery: %s:%s", self._settings.plugin_ip, self._pairing_port)

        self._mdns_server = QolsysMDNS(
            self._settings.plugin_ip,
            self._pairing_port,
            self._settings.shared_zeroconf_instance,
        )

        try:
            await self._mdns_server.start_mdns()

        except NonUniqueNameException as err:
            raise QolsysConfigError(
                "mDNS Service Discovery Error: NonUniqueNameException - Another device on the network is using the same IP address or mDNS name"
            ) from err

        except Exception as err:
            LOGGER.exception("mDNS Service Discovery Error")
            raise QolsysConfigError(f"mDNS Service Discovery Error: {err}") from err

    async def _start_server(self) -> None:
        LOGGER.debug("Pairing Server - Starting HTTP Server: %s:%s", self._settings.plugin_ip, self._pairing_port)

        context = await asyncio.to_thread(self._create_ssl_context)

        self._server = await asyncio.start_server(
            self.handle_client,
            self._settings.plugin_ip,
            self._pairing_port,
            ssl=context,
        )

        LOGGER.debug("Pairing Server - Press Pair Button in IQ Remote Config Page ...")

        self._server_task = asyncio.create_task(
            self._server.serve_forever(),
            name="Qolsys Pairing Server",
        )

    def _create_ssl_context(self) -> ssl.SSLContext:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

        context.load_cert_chain(
            certfile=self._pki.cer_file_path,
            keyfile=self._pki.key_file_path,
        )

        return context

    async def handle_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        received_panel_mac = False
        received_signed_client_certificate = False
        received_qolsys_cer = False

        start_token = b"-----BEGIN CERTIFICATE-----\n"
        end_token = b"-----END CERTIFICATE-----\n"

        try:
            continue_pairing = True

            while continue_pairing:
                # Receive panel MAC
                if not received_panel_mac and not received_signed_client_certificate and not received_qolsys_cer:
                    request = await reader.read(2048)
                    mac = request.decode()
                    address, port = writer.get_extra_info("peername")

                    LOGGER.debug("Panel Connected from: %s:%s", address, port)
                    LOGGER.debug("Receiving from Panel: %s", mac)

                    self._settings.panel_mac = "".join(char for char in mac if char.isprintable())
                    self._settings.panel_ip = address
                    received_panel_mac = True

                    # Send random MAC
                    message = b"\x00\x11" + self._settings.random_mac.encode()
                    LOGGER.debug("Sending to Panel: %s", message.decode(errors="ignore"))

                    writer.write(message)
                    await writer.drain()

                    # Send CSR
                    async with aiofiles.open(self._pki.csr_file_path, mode="rb") as f:
                        content = await f.read()

                    LOGGER.debug("Sending to Panel: [CSR File Content]")
                    writer.write(content)
                    writer.write(b"sent")
                    await writer.drain()
                    continue

                # Receive signed client certificate
                if received_panel_mac and not received_signed_client_certificate and not received_qolsys_cer:
                    await reader.readuntil(start_token)

                    request = start_token + await reader.readuntil(end_token)
                    LOGGER.debug("Saving [Signed Client Certificate]")

                    async with aiofiles.open(self._pki.secure_file_path, mode="wb") as f:
                        await f.write(request)

                    received_signed_client_certificate = True

                # Receive Qolsys certificate
                if received_panel_mac and received_signed_client_certificate and not received_qolsys_cer:
                    await reader.readuntil(start_token)

                    request = start_token + await reader.readuntil(end_token)
                    LOGGER.debug("Saving [Qolsys Certificate]")

                    async with aiofiles.open(self._pki.qolsys_cer_file_path, mode="wb") as f:
                        await f.write(request)

                    received_qolsys_cer = True
                    continue_pairing = False

                    self._pairing_done.set()

        except asyncio.CancelledError:
            LOGGER.exception("Key Exchange Server asyncio CancelledError")
            raise

        except Exception:
            LOGGER.exception("Key Exchange Server error")
            raise

        finally:
            writer.close()
            await writer.wait_closed()
