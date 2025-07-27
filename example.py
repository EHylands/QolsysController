
import asyncio
import logging

from qolsys_controller.controller import QolsysController
from qolsys_controller.partition import QolsysPartition
from qolsys_controller.zone import QolsysSensor

logging.basicConfig(level=logging.DEBUG,format='%(levelname)s - %(module)s: %(message)s')
LOGGER = logging.getLogger(__name__)

async def main():

    loop = asyncio.get_running_loop()
    background_tasks = set()

    # Change to your plugin ip
    plugin_ip = '192.168.10.222'

    remote = QolsysController(config_directory='./config/')
    
    # Select plugin
    remote.select_plugin('remote')

    remote.plugin.settings.panel_ip = "192.168.10.220"
    remote.plugin.settings.panel_mac = "3c:31:78:a0:fb:9f"
    remote.plugin.settings.plugin_paired = True
    remote.plugin.settings.random_mac = "f2:16:3e:08:81:a7"

    # Configure remote plugin
    if not await remote.plugin.config(plugin_ip=plugin_ip):
        LOGGER.debug(f'Error Configuring remote plugin')
        return
    
    # Additionnal remote plugin config
    remote.plugin.check_user_code_on_disarm = True # Check user code in user.conf file
    remote.plugin.log_mqtt_mesages = False # Enable for MQTT debug purposes

    # Settings_panel observer
    def settings_panel_observer(self):
        print('Panel Setting Update')

    # state zone observer
    def state_zone_observer(self,change:str,zone:QolsysSensor):
        match change:
             case remote.state.NOTIFY_ZONE_ADD:
                zone = remote.state.zone(zone.zone_id)
                if zone != None:
                    print(f'Main - Zone Added - Zone{zone.zone_id} ({zone.sensorname})')
                    zone.register(zones_observer)

    # state partition observer
    def state_partition_observer(self,change:str,partition:QolsysPartition):
        match change:
            case remote.state.NOTIFY_PARTITION_ADD:
                if partition != None:
                    print(f'Main - Partition Added - Partition{partition.id} ({partition.name})')
                    partition.register(partitions_observer)

            case remote.state.NOTIFY_PARTITION_DELETE:
                if partition != None:
                    print(f'Main - Partition Deleted - Partition{partition.id} ({partition.name})')
                    partition.unregister(state_partition_observer)
    
    # Partitions observers
    def partitions_observer(self):
        pass
        #print(f'Partition{partition_id} - {change} - {new_value}')

    # Zones observers
    def zones_observer(self):
        print('Zone Update')

    # Register observers
    remote.panel.settings_panel_observer.register(settings_panel_observer)
    remote.state.state_partition_observer.register(state_partition_observer)
    remote.state.state_zone_observer.register(state_zone_observer)
     
    # Start panel operation
    ready: asyncio.Future[bool] = asyncio.get_running_loop().create_future()

    def panel_ready_callback(self,panel_ready:bool):
        ready.set_result(panel_ready)

    remote.plugin.panel_ready_observer.register(panel_ready_callback)
    remote.plugin.start_operation()

    if not await ready:
        LOGGER.error('Error loading iq2meid database')

    LOGGER.debug('Qolsys Panel Ready for operation')

    # Close Dimmer
    await asyncio.sleep(3)
    await remote.plugin.command_zwave_switch_multi_level(node_id=6,level=99)

    # Open Dimmer
    #await remote.plugin.command_zwave_switch_multi_level(node_id=6,level=99)

    # ARM_STAY
    #await asyncio.sleep(3)
    #await remote.plugin.command_arm(partition_id=0,arming_type='ARM-STAY',user_code='1111', exit_sounds=False)
   
    # DISARM
    #await asyncio.sleep(3)
    #await remote.plugin.command_disarm(partition_id=0,user_code='1111')

    # ARM_AWAY
    #await asyncio.sleep(3)
    #await remote.plugin.command_arm(partition_id=0,arming_type='ARM_AWAY',user_code='1111', exit_sounds=False)

    # DISARM
    #await asyncio.sleep(65)
    #await remote.plugin.command_disarm(partition_id=0,user_code='1111')

    while True:
        await asyncio.sleep(1)

asyncio.run(main())


