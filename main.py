
import asyncio
import logging

from qolsys.controller import QolsysController

logging.basicConfig(level=logging.DEBUG,format='%(levelname)s - %(module)s: %(message)s')
LOGGER = logging.getLogger(__name__)

async def main():

    loop = asyncio.get_running_loop()
    background_tasks = set()

    # Change to your plugin and panel ip
    qolsys_panel_ip = 'qolsys_panel_ip'
    plugin_ip = 'plugin_ip'

    remote = QolsysController()
    
    # Select plugin
    remote.select_plugin('remote')

    # Configure remote plugin
    if not await remote.plugin.config(plugin_ip=plugin_ip,panel_ip=qolsys_panel_ip):
        LOGGER.debug(f'Error Configuring remote plugin')
        return
    
    # Additionnal remote plugin config
    remote.plugin.check_user_code_on_disarm = True # Check user code in user.conf file
    remote.plugin.log_mqtt_mesages = False # Enable for MQTT debug purposes
        
    # Start panel operation
    task = loop.create_task(remote.plugin.start_operation())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.remove)

    # ARM_STAY
    await asyncio.sleep(3)
    await remote.plugin.command_arm(partition_id=0,arming_type='ARM_STAY',user_code='1111', exit_sounds=False)

    # DISARM
    await asyncio.sleep(3)
    await remote.plugin.command_disarm(partition_id=0,user_code='1111')

    # ARM_AWAY
    await asyncio.sleep(3)
    await remote.plugin.command_arm(partition_id=0,arming_type='ARM_AWAY',user_code='1111', exit_sounds=False)

    # DISARM
    await asyncio.sleep(65)
    await remote.plugin.command_disarm(partition_id=0,user_code='1111')

    while True:
        await asyncio.sleep(1)

asyncio.run(main())


