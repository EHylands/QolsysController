import logging

from .plugin import QolsysPlugin

LOGGER = logging.getLogger(__name__)


class QolsysPluginC4(QolsysPlugin):
    def __init__(self) -> None:

        # C4 Integration
        raise NotImplementedError("C4 Plugin Not Yet Implemented") # noqa: EM101

    def config(self, panel_ip: str, token: str) -> bool:  # noqa: ARG002
        LOGGER.warning("C4Plugin: Configuring Plugin")
        super().config()
        return True
