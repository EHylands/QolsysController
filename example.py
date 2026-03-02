#!/usr/bin/env python3

import asyncio
import logging
import os
import ssl
import sys

from qolsys_controller.controller import QolsysController
from qolsys_controller.errors import QolsysMqttError, QolsysSqlError, QolsysSslError

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(module)s: %(message)s")
LOGGER = logging.getLogger(__name__)


async def main() -> None:  # noqa: D103
    remote = QolsysController()
    remote.settings.config_directory = "./config/"
    remote.settings.panel_ip = "192.168.10.220" # Qolsys Panel IP
    remote.settings.plugin_ip = "192.168.10.73" # Controller Plugin IP
    remote.settings.random_mac = ""  # Example: F2:16:3E:33:ED:20

    # Additionnal remote plugin config
    remote.settings.check_user_code_on_arm = True
    remote.settings.check_user_code_on_disarm = False  # Check user code in user.conf file
    remote.settings.log_mqtt_messages = False  # Enable for MQTT debug purposes
    remote.settings.auto_discover_pki = True

    # Configure remote plugin
    if not await remote.config(start_pairing=True):
        LOGGER.debug("Error Configuring remote plugin")
        return

    try:
        await remote.start_operation()

    except QolsysMqttError:
        LOGGER.debug("QolsysMqttError")

    except (QolsysSslError, ssl.SSLError):
        LOGGER.debug("QolsysSslError")

    except QolsysSqlError:
        LOGGER.debug("QolsysSqlError")

    if not remote.connected:
        LOGGER.error("Panel not ready for operation")
        return

    LOGGER.debug("Qolsys Panel Ready for operation")

    # Use an asyncio.Event to keep the program running efficiently
    stop_event = asyncio.Event()
    await stop_event.wait()


# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import (  # type: ignore[attr-defined]
        WindowsSelectorEventLoopPolicy,
        set_event_loop_policy,
    )

    set_event_loop_policy(WindowsSelectorEventLoopPolicy())

asyncio.run(main())
