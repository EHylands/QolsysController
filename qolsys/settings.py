import json
import logging

LOGGER = logging.getLogger(__name__)

class QolsysSettings:

    def __init__(self,settings_directory:str,settings_file:str):
        self._settings_file = settings_file
        self._settings_directory = settings_directory
        self._plugin_ip = ''
        self._plugin_paired = False
        self._random_mac = ''
        self._panel_mac = ''
    
    @property 
    def plugin_paired(self):
        return self._plugin_paired
    
    @plugin_paired.setter
    def plugin_paired(self, plugin_paired:bool):
        self._plugin_paired = plugin_paired

    @property
    def random_mac(self):
        return self._random_mac
    
    @random_mac.setter
    def random_mac(self,random_mac:str):
        self._random_mac = random_mac
    
    @property
    def plugin_ip(self):
        return self._plugin_ip
    
    @property
    def panel_mac(self):
        return self._panel_mac
    
    @panel_mac.setter
    def panel_mac(self,panel_mac:str):
        self._panel_mac = panel_mac

    def read_settings(self)->bool:
        try:
            with open(self._settings_directory + self._settings_file) as fd:
                try:
                    json_data = json.load(fd)
                    self._plugin_paired = json_data['plugin_paired']
                    self._panel_mac = json_data['panel_mac']
                    self._random_mac = json_data['random_mac']

                    LOGGER.debug(f'Found Pairing Data')

                    if self._random_mac == '':
                        LOGGER.debug(f'No random_mac')
                    else:
                        LOGGER.debug(f'Using random_mac ' + self.random_mac)

                    if self._plugin_paired:
                        LOGGER.debug(f'Plugin is Paired')
                    else:
                        LOGGER.debug(f'Plugin is Not Paired')

                except json.JSONDecodeError as e:
                    LOGGER.error(f'Pairing Status file json error: {e}"')
                    return False
            return True
        
        except FileNotFoundError:
            LOGGER.error(f'Pairing Status file not found')
            return False

    def save_settings(self):

        data = {
            "plugin_paired": self.plugin_paired,
            "random_mac": self.random_mac,
            "panel_mac": self._panel_mac
        }

        try:
            with open(self._settings_directory + self._settings_file, "w") as file:
                json.dump(data, file, indent=4)   

        except IOError as e:
                LOGGER.error(f'IO Error Saving Settings File: {e}')
        
        except Exception as e:
                LOGGER.error(f'Error Saving Settings File: {e}')