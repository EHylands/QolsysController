import base64
import logging

from qolsys_controller.enum_qolsys import PhotoDirectory

LOGGER = logging.getLogger(__name__)


class QolsysPicture:
    def __init__(
        self,
        image_type: str = "image/jpeg",
        data: bytes | None = None,
        request_id: str = "",
        filename: str = "",
        directory: PhotoDirectory = PhotoDirectory.PEEK_IN,
        retained_on_panel: bool = False,
    ) -> None:

        self._data: bytes | None = data
        self._image_type: str = image_type
        self._request_id: str = request_id
        self._filename: str = filename
        self._directory: PhotoDirectory = directory
        self._retained_on_panel: bool = retained_on_panel

    def write_to_current_directory(self) -> None:
        """Write the picture to the current working directory."""
        if self._data is not None and self._filename:
            with open(self._filename, "wb") as f:
                f.write(self._data)

    def write_to_directory(self, path: str) -> None:
        """Write the picture to the specified directory."""
        if self._data is not None:
            with open(path, "wb") as f:
                f.write(self._data)

    def to_dict(self) -> dict[str, str]:
        return {
            "image_type": self.image_type,
            "request_id": self.request_id,
            "filename": self.filename,
            "directory": self.directory.value,
            "retained_on_panel": str(self.retained_on_panel),
            "data": base64.b64encode(self._data).decode("ascii") if self._data is not None else "",
        }

    # -----------------------------
    # properties + setters
    # -----------------------------

    @property
    def data(self) -> bytes | None:
        return self._data

    @data.setter
    def data(self, value: bytes) -> None:
        self._data = value

    @property
    def image_type(self) -> str:
        return self._image_type

    @property
    def request_id(self) -> str:
        return self._request_id

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def directory(self) -> PhotoDirectory:
        return self._directory

    @property
    def retained_on_panel(self) -> bool:
        return self._retained_on_panel
