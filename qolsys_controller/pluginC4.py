import logging

from qolsys_controller.plugin import QolsysPlugin

LOGGER = logging.getLogger(__name__)

class QolsysPluginC4(QolsysPlugin):
        def __init__(self):
                
                # C4 Integration
                self._token = ''
        
        def config(self,panel_ip:str,token:str)->bool:
                LOGGER.warning(f'C4Plugin: Configuring Plugin')
                super().config()

                self._panel_ip = panel_ip
                self._token = token

                return True


