#!/usr/bin/env python3

import asyncio
import logging
import os
import sys

from qolsys_controller.controller import QolsysController
from qolsys_controller.errors import QolsysMqttError, QolsysSqlError, QolsysSslError

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(module)s: %(message)s")
LOGGER = logging.getLogger(__name__)


async def main() -> None:  # noqa: D103

    remote = QolsysController()

    # Select plugin
    remote.select_plugin("remote")

    remote.plugin.settings.config_directory = "./config/"
    remote.plugin.settings.panel_ip = "192.168.10.220"
    remote.plugin.settings.plugin_ip = "192.168.10.73"
    remote.plugin.settings.random_mac = ""  # Example: F2:16:3E:33:ED:20

    # Additionnal remote plugin config
    remote.plugin.check_user_code_on_disarm = False  # Check user code in user.conf file
    remote.plugin.log_mqtt_mesages = False  # Enable for MQTT debug purposes
    remote.plugin.auto_discover_pki = True

    # Configure remote plugin
    if not await remote.plugin.config(start_pairing=True):
        LOGGER.debug("Error Configuring remote plugin")
        return

    try:
        await remote.plugin.start_operation()

    except QolsysMqttError:
        LOGGER.debug("QolsysMqttError")

    except QolsysSslError:
        LOGGER.debug("QolsysSslError")

    except QolsysSqlError:
        LOGGER.debug("QolsysSqlError")

    if not remote.plugin.connected:
        LOGGER.error("Panel not ready for operation")
        return

    LOGGER.debug("Qolsys Panel Ready for operation")

    #await asyncio.sleep(5)

    #await remote.plugin.stop_operation()
    #LOGGER.debug("Qolsys Panel - Stopped")

    # Change Z-Wave dimmer
    # node_id: z-wane device id
    # level: 0-99, -1 to switch from off to previous on dimmer level
    # await asyncio.sleep(3)
    # await remote.plugin.command_zwave_switch_multi_level(node_id=6,level=99)

    # DISARM
    #await asyncio.sleep(3)
    #await remote.plugin.command_disarm(partition_id="0",
    #                                   user_code="1111")

    # ARM_STAY
    #await asyncio.sleep(3)
    #await remote.plugin.command_arm(partition_id="0",
    #                                arming_type="ARM-STAY",
    #                               user_code="1111",
    #                                exit_sounds=False,
    #                                instant_arm=True,
    #                                entry_delay=False)


    # ARM_AWAY
    #await asyncio.sleep(3)
    #await remote.plugin.command_arm(partition_id='0',
    #                               arming_type="ARM-STAY",
    #                               user_code="1111",
    #                                exit_sounds=False,
    #                               instant_arm=True)

    # DISARM
    #await asyncio.sleep(5)
    #await remote.plugin.command_disarm(partition_id="0", user_code="1111", silent_disarming=True)

    #await asyncio.sleep(5)
    #await remote.plugin.command_execute_scene(scene_id="3")

    #await asyncio.sleep(5)
    #await remote.plugin.command_zwave_switch_multi_level(6,80)
    #await remote.plugin.command_zwave_doorlock_set(node_id="7",locked=True)

    # Use an asyncio.Event to keep the program running efficiently
    stop_event = asyncio.Event()
    await stop_event.wait()

# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import WindowsSelectorEventLoopPolicy, set_event_loop_policy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())

asyncio.run(main())
