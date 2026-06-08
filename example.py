#!/usr/bin/env python3

import asyncio
import logging
import os
import ssl
import sys

from zeroconf.asyncio import AsyncZeroconf

from qolsys_controller.controller import QolsysController
from qolsys_controller.errors import QolsysConfigError, QolsysMqttError, QolsysSqlError, QolsysSslError

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(module)s: %(message)s")
logging.getLogger("aiomqtt").setLevel(logging.DEBUG)

LOGGER = logging.getLogger(__name__)


async def main() -> None:  # noqa: D103
    remote = QolsysController()
    remote.settings.config_directory = "./config/"
    remote.settings.panel_ip = "192.168.10.220"  # Qolsys Panel IP
    remote.settings.plugin_ip = "192.168.10.228"  # Controller Plugin IP
    remote.settings.random_mac = ""  # Example: F2:16:3E:33:ED:20

    # Additionnal remote plugin config
    remote.settings.check_user_code_on_arm = False
    remote.settings.check_user_code_on_disarm = False  # Check user code in user.conf file
    remote.settings.log_mqtt_messages = False  # Enable for MQTT debug purposes
    remote.settings.auto_discover_pki = True
    remote.settings.pairing_resume = True  # Enable to resume pairing process if it was interrupted before completion

    remote.settings.mqtt_bridge_enabled = False
    remote.settings._mqtt_bridge_broker_enabled = True
    remote.settings.mqtt_bridge_port = 1883
    remote.settings.mqtt_bridge_tls_enabled = False

    aiozc = AsyncZeroconf()
    remote.settings.shared_zeroconf_instance = aiozc

    try:
        await remote.run_forever(reconnect=True, run_once=False, start_pairing=True)
        LOGGER.debug("Main task completed")

    except* QolsysConfigError:
        LOGGER.debug("QolsysConfigError")

    except* QolsysMqttError:
        LOGGER.debug("QolsysMqttError")

    except* (QolsysSslError, ssl.SSLError):
        LOGGER.debug("QolsysSslError")

    except* QolsysSqlError:
        LOGGER.debug("QolsysSqlError")

    except* asyncio.CancelledError:
        LOGGER.debug("Main task cancelled")

    finally:
        try:
            await remote.stop()
            await asyncio.shield(aiozc.async_close())
        except asyncio.CancelledError:
            LOGGER.debug("Ignoring cancellation during shutdown")


# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":  #
    from asyncio import (  # type: ignore[attr-defined]
        WindowsSelectorEventLoopPolicy,
        set_event_loop_policy,
    )

    set_event_loop_policy(WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
