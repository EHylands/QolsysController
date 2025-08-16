
import asyncio
import logging
import sys
import os

from qolsys_controller.controller import QolsysController
from qolsys_controller.partition import QolsysPartition
from qolsys_controller.zone import QolsysZone

logging.basicConfig(level=logging.DEBUG,format='%(levelname)s - %(module)s: %(message)s')
LOGGER = logging.getLogger(__name__)

async def main():

    # Change to your plugin ip
    plugin_ip = '192.168.10.226'

    remote = QolsysController(config_directory='./config/')
    
    # Select plugin
    remote.select_plugin('remote')

    remote.plugin.settings.panel_ip =  '192.168.10.220'
    remote.plugin.settings.random_mac = '' # Example: F2:16:3E:33:ED:20

    # Additionnal remote plugin config
    remote.plugin.check_user_code_on_disarm = True # Check user code in user.conf file
    remote.plugin.log_mqtt_mesages = False # Enable for MQTT debug purposes
    remote.plugin._auto_discover_pki = True

    # Configure remote plugin
    if not await remote.plugin.config(plugin_ip=plugin_ip):
        LOGGER.debug(f'Error Configuring remote plugin')
        return
         
    # Start panel operation
    ready: asyncio.Future[bool] = asyncio.get_running_loop().create_future()

    def panel_ready_callback(self,panel_ready:bool):
        ready.set_result(panel_ready)
        remote.plugin.panel_ready_observer.unregister(panel_ready_callback)

    remote.plugin.panel_ready_observer.register(panel_ready_callback)
    remote.plugin.start_operation()

    if not await ready:
        LOGGER.error('Error loading iq2meid database')

    LOGGER.debug('Qolsys Panel Ready for operation')

    # Change Z-Wave dimmer 
    # node_id: z-wane device id
    # level: 0-99, -1 to switch from off to previous on dimmer level
    # await asyncio.sleep(3)
    # await remote.plugin.command_zwave_switch_multi_level(node_id=6,level=99)

    # ARM_STAY
    #await asyncio.sleep(3)
    #await remote.plugin.command_arm(partition_id=0,
    #                                arming_type='ARM-STAY',
    #                                user_code='1111', 
    #                                exit_sounds=False,
    #                                instant_arm=True)
   
    # DISARM
    #await asyncio.sleep(3)
    #await remote.plugin.command_disarm(partition_id=0,
    #                                   user_code='1111')

    # ARM_AWAY
    #await asyncio.sleep(3)
    #await remote.plugin.command_arm(partition_id=0,
    ##                                arming_type='ARM-AWAY',
    #                                user_code='1111', 
    #                                exit_sounds=True,
    #                                instant_arm=False)

    while True:
        await asyncio.sleep(1)

# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())

asyncio.run(main())


