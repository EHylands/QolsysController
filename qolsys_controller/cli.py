#!/usr/bin/env python3
import argparse
import asyncio
import contextlib
import json
import logging
import os
import signal
import socket
import ssl
import sys
from dataclasses import dataclass, field
from typing import Any

from qolsys_controller.controller import QolsysController as qolsys_controller
from qolsys_controller.errors import QolsysConfigError, QolsysMqttError, QolsysSqlError, QolsysSslError


@dataclass
class ControllerConfig:
    panel_ip: str
    panel_mac: str
    random_mac: str
    config_dir: str
    plugin_ip: str | None

    auto_discover_pki: bool
    pairing_resume: bool
    start_pairing: bool
    check_user_code_on_arm: bool
    check_user_code_on_disarm: bool
    mqtt_bridge_hostname: str
    mqtt_bridge_client_username: str
    mqtt_bridge_client_password: str
    mqtt_bridge_enabled: bool
    mqtt_bridge_tls_enabled: bool
    mqtt_bridge_broker_enabled: bool
    mqtt_bridge_broker_allowed_users: dict[str, str] = field(default_factory=dict)
    mqtt_bridge_max_connections: int = 5
    mqtt_bridge_root_topic: str = "qolsys"
    mqtt_bridge_friendly_name: str = "iq_panel"
    mqtt_bridge_port: int = 8883
    log_mqtt_messages: bool = False


def _detect_local_ip() -> Any:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except Exception:
        return "127.0.0.1"


def load_config(path: str) -> ControllerConfig:
    with open(path, "r", encoding="utf-8") as handle:
        raw = json.load(handle)

        return ControllerConfig(

            panel_ip=raw["panel_ip"],
            panel_mac=raw.get("panel_mac", ""),
            random_mac=raw.get("random_mac", ""),
            config_dir=raw.get("config_dir", "/var/lib/qolsys-bridge"),
            plugin_ip=raw.get("plugin_ip", ""),
            auto_discover_pki=bool(raw.get("auto_discover_pki", True)),
            pairing_resume=bool(raw.get("resume_pairing", True)),
            start_pairing=bool(raw.get("start_pairing", True)),
            check_user_code_on_arm=bool(raw.get("check_user_code_on_arm", False)),
            check_user_code_on_disarm=bool(raw.get("check_user_code_on_disarm", False)),
            mqtt_bridge_enabled=bool(raw.get("mqtt_bridge_enabled", False)),
            mqtt_bridge_hostname=raw.get("mqtt_bridge_hostname", ""),
            mqtt_bridge_client_username=raw.get("mqtt_bridge_client_username", ""),
            mqtt_bridge_client_password=raw.get("mqtt_bridge_client_password", ""),
            mqtt_bridge_tls_enabled=bool(raw.get("mqtt_bridge_tls_enabled", True)),
            mqtt_bridge_broker_enabled=bool(raw.get("mqtt_bridge_broker_enabled", False)),
            mqtt_bridge_broker_allowed_users=raw.get("mqtt_bridge_broker_allowed_users", {}),
            mqtt_bridge_max_connections=int(raw.get("mqtt_bridge_max_connections", 5)),
            mqtt_bridge_root_topic=raw.get("mqtt_bridge_root_topic", "qolsys"),
            mqtt_bridge_friendly_name=raw.get("mqtt_bridge_friendly_name", "iq_panel"),
            mqtt_bridge_port=int(raw.get("mqtt_bridge_port", 8883)),
            log_mqtt_messages=bool(raw.get("log_mqtt_messages", False)),
        )


class QolsysController:
    def __init__(self, config: ControllerConfig, log: logging.Logger) -> None:
        self.config = config
        self.log = log
        self.controller = qolsys_controller()

    async def start(self) -> None:
        os.makedirs(self.config.config_dir, exist_ok=True)

        settings = self.controller.settings
        settings.config_directory = self.config.config_dir
        settings.plugin_ip = self.config.plugin_ip or _detect_local_ip()
        settings.panel_ip = self.config.panel_ip
        settings.panel_mac = self.config.panel_mac
        settings.random_mac = self.config.random_mac
        settings.log_mqtt_messages = self.config.log_mqtt_messages
        settings.auto_discover_pki = self.config.auto_discover_pki
        settings.check_user_code_on_arm = self.config.check_user_code_on_arm
        settings.check_user_code_on_disarm = self.config.check_user_code_on_disarm
        settings.pairing_resume = self.config.pairing_resume
        settings.mqtt_bridge_enabled = self.config.mqtt_bridge_enabled
        settings.mqtt_bridge_hostname = self.config.mqtt_bridge_hostname
        settings.mqtt_bridge_client_username = self.config.mqtt_bridge_client_username
        settings.mqtt_bridge_client_password = self.config.mqtt_bridge_client_password
        settings.mqtt_bridge_tls_enabled = self.config.mqtt_bridge_tls_enabled
        settings.mqtt_bridge_broker_enabled = self.config.mqtt_bridge_broker_enabled
        settings.mqtt_bridge_broker_allowed_users = self.config.mqtt_bridge_broker_allowed_users
        settings.mqtt_bridge_max_connections = self.config.mqtt_bridge_max_connections
        settings.mqtt_bridge_root_topic = self.config.mqtt_bridge_root_topic
        settings.mqtt_bridge_friendly_name = self.config.mqtt_bridge_friendly_name
        settings.mqtt_bridge_port = self.config.mqtt_bridge_port

        try:
            await self.controller.start_operation(reconnect=False, run_once=False, start_pairing=self.config.start_pairing)

        except QolsysMqttError:
            raise RuntimeError("Failed to start qolsys-controller due to MQTT error. Check logs for details.")

        except (QolsysSslError, ssl.SSLError):
            raise RuntimeError("Failed to start qolsys-controller due to SSL error. Check logs for details.")

        except QolsysSqlError:
            raise RuntimeError("Failed to start qolsys-controller due to SQL error. Check logs for details.")

        except QolsysConfigError as err:
            raise RuntimeError(err)

        except asyncio.CancelledError:
            self.log.info("Controller start cancelled")
            raise

        if not self.controller.connected:
            self.log.error("qolsys-controller not ready for operation")

    async def stop(self) -> None:
        await self.controller.stop_operation()


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(message)s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="qolsys-controller")
    parser.add_argument("--config", default="config.json", help="Path to qolsys-controller config.json")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args()


async def _main_async() -> None:
    args = parse_args()
    configure_logging(args.verbose)
    log = logging.getLogger("qolsys-controller")

    try:
        config = load_config(args.config)
        bridge = QolsysController(config, log)

        stop_event = asyncio.Event()

        def _handle_signal() -> None:
            stop_event.set()

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            with contextlib.suppress(NotImplementedError):
                loop.add_signal_handler(sig, _handle_signal)

        task = asyncio.create_task(bridge.start())

        try:
            await stop_event.wait()
        finally:
            await bridge.stop()
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    except Exception as e:
        log.error("Fatal error: %s", e)
        sys.exit(1)


# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import (  # type: ignore[attr-defined]
        WindowsSelectorEventLoopPolicy,
        set_event_loop_policy,
    )

    set_event_loop_policy(WindowsSelectorEventLoopPolicy())


def main() -> None:
    asyncio.run(_main_async())


if __name__ == "__main__":
    main()
