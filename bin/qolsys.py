#!/usr/bin/env python3

import argparse
import asyncio
import logging
import os
import sys

from qolsys_controller import qolsys_controller
from qolsys_controller.errors import QolsysMqttError, QolsysSqlError, QolsysSslError


async def main() -> None:  # noqa: D103

    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--panel-ip", help="Qolsys Panel IP", default="")
    cli_parser.add_argument("--plugin-ip", help="Plugin IP", default="")
    cli_parser.add_argument("--config-dir", help="Configuration Directory", default="./config/")
    cli_parser.add_argument("--pki-autodiscovery", help="Enable PKI Autodiscovery", action="store_true")
    cli_parser.add_argument("--debug", help="Verbose MQTT Traffic", action="store_true")

    args = cli_parser.parse_args()

    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(module)s: %(message)s")
    LOGGER = logging.getLogger(__name__)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    Panel = qolsys_controller()

    # Select plugin
    Panel.select_plugin("remote")
    Panel.settings.config_directory = args.config_dir
    Panel.plugin.settings.panel_ip = args.panel_ip
    Panel.plugin.settings.plugin_ip = args.plugin_ip
    Panel.plugin.settings.random_mac = ""

    # Additionnal remote plugin config
    Panel.plugin.check_user_code_on_disarm = False
    Panel.plugin.log_mqtt_mesages = args.debug
    Panel.plugin.auto_discover_pki = args.pki_autodiscovery

    # Configure remote plugin
    if not await Panel.plugin.config(start_pairing=True):
        LOGGER.debug("Error Configuring remote plugin")
        return

    try:
        await Panel.plugin.start_operation()

    except QolsysMqttError:
        LOGGER.debug("QolsysMqttError")

    except QolsysSslError:
        LOGGER.debug("QolsysSslError")

    except QolsysSqlError:
        LOGGER.debug("QolsysSqlError")

    if not Panel.plugin.connected:
        LOGGER.error("Panel not ready for operation")
        return

    LOGGER.debug("Qolsys Panel Ready for operation")

    stop_event = asyncio.Event()
    await stop_event.wait()

# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import WindowsSelectorEventLoopPolicy, set_event_loop_policy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())

asyncio.run(main())
