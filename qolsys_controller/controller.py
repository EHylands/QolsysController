#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import random
import ssl
import time
from datetime import datetime, timezone
from typing import Any

import aiofiles
import aiomqtt
from zeroconf._exceptions import NonUniqueNameException

from qolsys_controller.automation.service_siren import SirenService
from qolsys_controller.automation.service_valve import ValveService
from qolsys_controller.automation_adc.device import QolsysAutomationDeviceADC
from qolsys_controller.automation_adc.service_cover import CoverServiceADC
from qolsys_controller.automation_adc.service_light import LightServiceADC
from qolsys_controller.automation_adc.service_status import StatusServiceADC
from qolsys_controller.automation_zwave.device import QolsysAutomationDeviceZwave
from qolsys_controller.automation_zwave.service_cover import CoverServiceZwave
from qolsys_controller.automation_zwave.service_light import LightServiceZwave
from qolsys_controller.automation_zwave.service_lock import LockServiceZwave
from qolsys_controller.automation_zwave.service_meter import MeterServiceZwave
from qolsys_controller.automation_zwave.service_thermostat import ThermostatServiceZwave
from qolsys_controller.enum_adc import vdFuncState
from qolsys_controller.mqtt_command import (
    MQTTCommand,
    MQTTCommand_Automation,
    MQTTCommand_Panel,
    MQTTCommand_ZWave,
    MQTTCommand_ZWave_Old,
)
from qolsys_controller.observable import Event

from .enum_qolsys import (
    BypassCapableZoneSensorType,
    PartitionAlarmState,
    PartitionArmingType,
    PartitionSystemStatus,
    QolsysNotification,
    QolsysPanelType,
    QolsysTemperatureUnit,
    SafetyZoneSensorGroup,
    TroubleZoneStatus,
)
from .enum_zwave import ThermostatFanMode, ThermostatMode, ThermostatSetpointMode, ZwaveCommandClass
from .errors import InvalidVirtualNodeError, QolsysMqttError, QolsysSslError, QolsysUserCodeError, ServiceNotFoundError
from .mdns import QolsysMDNS
from .mqtt_bridge.bridge import MqttBridge
from .mqtt_command_queue import QolsysMqttCommandQueue
from .panel import QolsysPanel
from .pki import QolsysPKI
from .settings import QolsysSettings
from .state import QolsysState
from .task_manager import QolsysTaskManager
from .utils_mqtt import generate_random_mac

LOGGER = logging.getLogger(__name__)


class QolsysController:
    def __init__(self) -> None:
        # QolsysController
        self._state = QolsysState(self)
        self._settings = QolsysSettings(self)
        self._panel = QolsysPanel(self)
        self._initial_run: bool = True

        self.connected = False

        # PKI
        self._pki = QolsysPKI(settings=self.settings)

        # Plugin
        self.certificate_exchange_server: asyncio.Server | None = None
        self._task_manager = QolsysTaskManager()
        self._mqtt_command_queue = QolsysMqttCommandQueue()
        self._zone_id: str = "1"

        # MQTT Client
        self.aiomqtt: aiomqtt.Client | None = None
        self._mqtt_task_config_label: str = "mqtt_task_config"
        self._mqtt_task_listen_label: str = "mqtt_task_listen"
        self._mqtt_task_connect_label: str = "mqtt_task_connect"
        self._mqtt_task_ping_label: str = "mqtt_task_ping"
        self._mqtt_task_zwave_meter_update_label: str = "mqtt_task_zwave_meter_update"

        # MQTT Bridge
        self._mqtt_bridge: MqttBridge | None = None

    @property
    def state(self) -> QolsysState:
        return self._state

    @property
    def panel(self) -> QolsysPanel:
        return self._panel

    @property
    def settings(self) -> QolsysSettings:
        return self._settings

    @property
    def mqtt_command_queue(self) -> QolsysMqttCommandQueue:
        return self._mqtt_command_queue

    async def is_paired(self) -> bool:
        return (
            self._pki.id != ""
            and await self._pki.check_key_file()
            and await self._pki.check_cer_file()
            and await self._pki.check_qolsys_cer_file()
            and await self._pki.check_secure_file()
            and self.settings.check_panel_ip()
            and self.settings.check_plugin_ip()
        )

    async def config(self, start_pairing: bool) -> Any:
        return await self._task_manager.run(self.config_task(start_pairing), self._mqtt_task_config_label)

    async def config_task(self, start_pairing: bool) -> bool:
        LOGGER.debug("Configuring Plugin")

        # Check and created config_directory
        if not self.settings.check_config_directory(create=start_pairing):
            return False

        # Read user file for access code
        loop = asyncio.get_running_loop()
        if not loop.run_in_executor(None, self.panel.read_users_file):
            return False

        # Config PKI
        if self.settings.auto_discover_pki:
            if self._pki.auto_discover_pki():
                self.settings.random_mac = self._pki.formatted_id()
        else:
            self._pki.set_id(self.settings.random_mac)

        # Check if plugin is paired
        if await self.is_paired():
            LOGGER.debug("Panel is Paired")

        else:
            LOGGER.debug("Panel not paired")

            if not start_pairing:
                LOGGER.debug("Aborting pairing.")
                return False

            if not await self.start_initial_pairing():
                LOGGER.debug("Error Pairing with Panel")
                return False

        LOGGER.debug("Starting Plugin Operation")

        # Everything is configured
        return True

    async def start_mqtt_bridge(self) -> None:
        # Start MQTT Bridge if enabled
        LOGGER.debug("MQTT Bridge Enabled: %s", self.settings.mqtt_bridge_enabled)
        if self.settings.mqtt_bridge_enabled:
            # Create MQTT Bridge if not already created
            if not self._mqtt_bridge:
                self._mqtt_bridge = MqttBridge(self)

            # Start MQTT Bridge
            if not await self._mqtt_bridge.start():
                LOGGER.error("MQTT Bridge failed to start")
                await self.stop_operation()
                return

    async def start_operation(self) -> None:
        # Connect to Qolsys Panel MQTT and start listening for messages
        await self._task_manager.run(self.mqtt_connect_task(reconnect=True, run_forever=True), self._mqtt_task_connect_label)

        # Start MQTT Bridge Broker
        await self.start_mqtt_bridge()

        LOGGER.info("Qolsys Controller Ready for operation")

    async def stop_operation(self) -> None:
        LOGGER.debug("Stopping Plugin Operation")

        if self.certificate_exchange_server is not None:
            self.certificate_exchange_server.close()

        if self.aiomqtt is not None:
            await self.aiomqtt.__aexit__(None, None, None)
            self.aiomqtt = None

        self._task_manager.cancel(self._mqtt_task_connect_label)
        self._task_manager.cancel(self._mqtt_task_listen_label)
        self._task_manager.cancel(self._mqtt_task_ping_label)
        self._task_manager.cancel(self._mqtt_task_config_label)
        self._task_manager.cancel(self._mqtt_task_zwave_meter_update_label)

        if self._mqtt_bridge is not None:
            await self._mqtt_bridge.shutdown()

        self.connected = False
        self.notify_panel_status_update()

    def _to_event_dict(self) -> dict[str, Any]:
        return {
            "connected": self.connected,
            "panel_ip": self.settings.panel_ip,
            "unique_id": self.panel.unique_id,
            "plugin_ip": self.settings.plugin_ip,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

    def notify_panel_status_update(self) -> None:
        self.state.notify(Event(QolsysNotification.PANEL_STATUS_UPDATE, self.panel, self._to_event_dict()))

    async def mqtt_connect_task(self, reconnect: bool, run_forever: bool) -> None:
        # Set mqtt_remote_client_id
        self.settings.mqtt_remote_client_id = "qolsys-controller-" + self._pki.formatted_id()
        LOGGER.debug("Using MQTT remoteClientID: %s", self.settings.mqtt_remote_client_id)

        # Configure TLS context for MQTT connection
        def create_tls_context(self: QolsysController) -> ssl.SSLContext:
            ctx = ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH,
                cafile=str(self._pki.qolsys_cer_file_path),
            )
            ctx.set_ciphers("DEFAULT:@SECLEVEL=0")
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ctx.load_cert_chain(
                certfile=str(self._pki.secure_file_path),
                keyfile=str(self._pki.key_file_path),
            )
            return ctx

        loop = asyncio.get_running_loop()
        ctx = await loop.run_in_executor(None, create_tls_context, self)

        LOGGER.info("MQTT Panel: Connecting ...")

        self._task_manager.cancel(self._mqtt_task_listen_label)
        self._task_manager.cancel(self._mqtt_task_ping_label)
        self._task_manager.cancel(self._mqtt_task_zwave_meter_update_label)

        while True:
            try:
                self.aiomqtt = aiomqtt.Client(
                    hostname=self.settings.panel_ip,
                    port=8883,
                    tls_context=ctx,
                    tls_insecure=True,
                    clean_session=True,
                    timeout=self.settings.mqtt_timeout,
                    identifier=self.settings.mqtt_remote_client_id,
                )

                await self.aiomqtt.__aenter__()

                LOGGER.info("MQTT Panel: Connected")

                # Subscribe to panel internal database updates
                await self.aiomqtt.subscribe("iq2meid")

                # Subscribte to MQTT private response
                await self.aiomqtt.subscribe("response_" + self.settings.random_mac, qos=self.settings.mqtt_qos)

                # Subscribe to Z-Wave response
                await self.aiomqtt.subscribe("ZWAVE_RESPONSE", qos=self.settings.mqtt_qos)

                # Only log all traffic for debug purposes
                if self.settings.log_mqtt_messages:
                    # Subscribe to MQTT commands send to panel by other devices
                    await self.aiomqtt.subscribe("mastermeid", qos=self.settings.mqtt_qos)

                self._task_manager.run(self.mqtt_listen_task(), self._mqtt_task_listen_label)
                self._task_manager.run(self.mqtt_ping_task(), self._mqtt_task_ping_label)

                response_connect = await self.command_connect()
                self.panel.imei = response_connect.get("master_imei", "")
                self.panel.product_type = response_connect.get("primary_product_type", "")

                await self.command_pingevent()
                await self.command_pair_status_request()

                response_database = await self.command_sync_database()
                LOGGER.debug("MQTT: Updating State from syncdatabase")
                await self.panel.load_database(response_database.get("fulldbdata"))

                # Print Panel Info once
                if self._initial_run:
                    self._initial_run = False
                    self.panel.dump()
                    self.state.dump()

                self.connected = True
                self.notify_panel_status_update()
                self._task_manager.run(self.mqtt_zwave_meter_update(), self._mqtt_task_zwave_meter_update_label)

                if not run_forever:
                    self.connected = False
                    self.notify_panel_status_update()
                    self._task_manager.cancel(self._mqtt_task_listen_label)
                    self._task_manager.cancel(self._mqtt_task_ping_label)
                    await self.aiomqtt.__aexit__(None, None, None)

                break

            except aiomqtt.MqttError as err:
                # Receive pannel network error
                self.connected = False
                self.notify_panel_status_update()
                self.aiomqtt = None

                if reconnect:
                    LOGGER.debug("MQTT Error - %s: Connect - Reconnecting in %s seconds ...", err, self.settings.mqtt_timeout)
                    await asyncio.sleep(self.settings.mqtt_timeout)
                else:
                    raise QolsysMqttError from err

            except ssl.SSLError as err:
                # SSL error is and authentication error with invalid certificates en pki
                # We cannot recover from this error automaticly
                # Pannels need to be re-paired
                self.connected = False
                self.notify_panel_status_update()
                self.aiomqtt = None
                raise QolsysSslError from err

    async def mqtt_ping_task(self) -> None:
        while True:
            if self.aiomqtt is not None and self.connected:
                with contextlib.suppress(aiomqtt.MqttError):
                    await self.command_pingevent()

            await asyncio.sleep(self.settings.mqtt_ping)

    async def mqtt_zwave_meter_update(self) -> None:
        while True:
            if self.aiomqtt is not None and self.connected:
                for autdev in self.state.automation_devices:
                    if not isinstance(autdev, QolsysAutomationDeviceZwave):
                        continue

                    if not autdev._FIX_MULTICHANNEL_METER_ENDPOINT:
                        continue

                    for service in autdev.service_get_protocol(MeterServiceZwave):
                        if isinstance(service, MeterServiceZwave):
                            await service.refresh_meter_zwave()
                            await asyncio.sleep(5)

            await asyncio.sleep(300)

    async def mqtt_listen_task(self) -> None:
        try:
            async for message in self.aiomqtt.messages:  # type: ignore[union-attr]
                if self.settings.log_mqtt_messages:  # noqa: SIM102
                    if isinstance(message.payload, bytes):
                        LOGGER.debug("MQTT TOPIC: %s\n%s", message.topic, message.payload.decode())

                # Panel response to MQTT Commands
                if message.topic.matches("response_" + self.settings.random_mac):  # noqa: SIM102
                    if isinstance(message.payload, bytes):
                        data = json.loads(message.payload.decode())
                        await self._mqtt_command_queue.handle_response(data)

                # Panel updates to IQ2MEID database
                if message.topic.matches("iq2meid"):  # noqa: SIM102
                    if isinstance(message.payload, bytes):
                        data = json.loads(message.payload.decode())
                        self.panel.parse_iq2meid_message(data)

                # Panel Z-Wave response
                if message.topic.matches("ZWAVE_RESPONSE"):  # noqa: SIM102
                    if isinstance(message.payload, bytes):
                        data = json.loads(message.payload.decode())
                        self.panel.parse_zwave_message(data)

        except aiomqtt.MqttError as err:
            self.connected = False
            self.notify_panel_status_update()

            LOGGER.debug("%s: Listen - Reconnecting in %s seconds ...", err, self.settings.mqtt_timeout)
            await asyncio.sleep(self.settings.mqtt_timeout)
            self._task_manager.run(self.mqtt_connect_task(reconnect=True, run_forever=True), self._mqtt_task_connect_label)

    async def start_initial_pairing(self) -> bool:
        # check if random_mac has been configured
        if self.settings.random_mac == "":
            # If pairing_resume is enabled, look for existing PKI folders to resume pairing process with previous random_mac
            resume_pki_id = await self._pki.pairing_resume_get_in_progress_pki()
            if self.settings.pairing_resume and resume_pki_id:
                self.settings.random_mac = resume_pki_id

            else:
                LOGGER.debug("Creating random_mac")
                self.settings.random_mac = generate_random_mac()
                await self._pki.create(self.settings.random_mac, key_size=self.settings.key_size)
                await self._pki.pairing_resume_pki_set(True)

        # Check if PKI is valid
        self._pki.set_id(self.settings.random_mac)
        LOGGER.debug("Checking PKI")
        if not (await self._pki.check_key_file() and await self._pki.check_cer_file() and await self._pki.check_csr_file()):
            LOGGER.error("PKI Error")
            return False

        LOGGER.debug("Starting Pairing Process")

        if not self.settings.check_plugin_ip():
            LOGGER.error("Plugin IP Address not configured")
            return False

        # If we dont allready have client signed certificate, start the pairing server
        if (
            not await self._pki.check_secure_file()
            or not await self._pki.check_qolsys_cer_file()
            or not self.settings.check_panel_ip()
        ):
            # High Level Random Pairing Port
            pairing_port = random.randint(50000, 55000)

            # Start Pairing mDNS Brodcast
            LOGGER.debug("Starting mDNS Service Discovery: %s:%s", self.settings.plugin_ip, str(pairing_port))
            mdns_server = QolsysMDNS(self.settings.plugin_ip, pairing_port)

            try:
                await mdns_server.start_mdns()
            except NonUniqueNameException:
                LOGGER.error("Error starting mDNS Service Discovery: NonUniqueNameException")
                return False

            # Start Key Exchange Server
            LOGGER.debug("Starting Certificate Exchange Server")

            def create_ssl_context() -> ssl.SSLContext:
                context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                context.load_cert_chain(certfile=self._pki.cer_file_path, keyfile=self._pki.key_file_path)
                return context

            context = await asyncio.to_thread(create_ssl_context)
            self.certificate_exchange_server = await asyncio.start_server(
                self.handle_key_exchange_client, self.settings.plugin_ip, pairing_port, ssl=context
            )
            LOGGER.debug("Certificate Exchange Server Waiting for Panel")
            LOGGER.debug("Press Pair Button in IQ Remote Config Page ...")

            async with self.certificate_exchange_server:
                try:
                    await self.certificate_exchange_server.serve_forever()

                except asyncio.CancelledError:
                    LOGGER.debug("Stoping Certificate Exchange Server")
                    await self.certificate_exchange_server.wait_closed()
                    LOGGER.debug("Stoping mDNS Service Discovery")
                    await mdns_server.stop_mdns()

        LOGGER.debug("Sending MQTT Pairing Request to Panel")

        # We have client sgined certificate at this point
        # Connect to Panel MQTT to send pairing command
        await self._task_manager.run(self.mqtt_connect_task(reconnect=False, run_forever=False), self._mqtt_task_connect_label)
        LOGGER.debug("Plugin Pairing Completed ")

        await self._pki.pairing_resume_pki_set(False)

        return True

    async def handle_key_exchange_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:  # noqa: PLR0915
        received_panel_mac = False
        received_signed_client_certificate = False
        received_qolsys_cer = False

        try:
            continue_pairing = True
            while continue_pairing:
                # Plugin is receiving panel_mac from panel
                if not received_panel_mac and not received_signed_client_certificate and not received_qolsys_cer:
                    request = await reader.read(2048)
                    mac = request.decode()

                    address, port = writer.get_extra_info("peername")
                    LOGGER.debug("Panel Connected from: %s:%s", address, port)
                    LOGGER.debug("Receiving from Panel: %s", mac)

                    # Remove \x00 and \x01 from received string
                    self.settings.panel_mac = "".join(char for char in mac if char.isprintable())
                    self.settings.panel_ip = address
                    received_panel_mac = True

                    # Sending random_mac to panel
                    message = b"\x00\x11" + self.settings.random_mac.encode()
                    LOGGER.debug("Sending to Panel: %s", message.decode())
                    writer.write(message)
                    await writer.drain()

                    # Sending CSR File to panel
                    async with aiofiles.open(self._pki.csr_file_path, mode="rb") as f:
                        content = await f.read()
                        LOGGER.debug("Sending to Panel: [CSR File Content]")
                        writer.write(content)
                        writer.write(b"sent")
                        await writer.drain()

                    continue

                # Read signed certificate data
                if received_panel_mac and not received_signed_client_certificate and not received_qolsys_cer:
                    request = await reader.readuntil(b"sent")
                    if request.endswith(b"sent"):
                        request = request[:-4]

                    LOGGER.debug("Saving [Signed Client Certificate]")
                    async with aiofiles.open(self._pki.secure_file_path, mode="wb") as f:
                        await f.write(request)
                        received_signed_client_certificate = True

                # Read qolsys certificate data
                if received_panel_mac and received_signed_client_certificate and not received_qolsys_cer:
                    request = await reader.readuntil(b"sent")
                    if request.endswith(b"sent"):
                        request = request[:-4]

                    LOGGER.debug("Saving [Qolsys Certificate]")
                    async with aiofiles.open(self._pki.qolsys_cer_file_path, mode="wb") as f:
                        await f.write(request)
                        received_qolsys_cer = True
                        continue_pairing = False

                    continue

        except asyncio.CancelledError:
            LOGGER.exception("Key Exchange Server asyncio CancelledError")

        except Exception:
            LOGGER.exception("Key Exchange Server error")

        finally:
            writer.close()
            await writer.wait_closed()
            if self.certificate_exchange_server:
                self.certificate_exchange_server.close()

    async def command_connect(self) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending connect command")

        dhcpInfo = {
            "ipaddress": "",
            "gateway": "",
            "netmask": "",
            "dns1": "",
            "dns2": "",
            "dhcpServer": "",
            "leaseDuration": "",
        }

        command = MQTTCommand(self, "connect_v204")
        command.append("ipAddress", self.settings.plugin_ip)
        command.append("pairing_request", True)
        command.append("macAddress", self.settings.random_mac)
        command.append("remoteClientID", self.settings.mqtt_remote_client_id)
        command.append("softwareVersion", "4.4.1")
        command.append("productType", "tab07_rk68")
        command.append("bssid", "")
        command.append("lastUpdateChecksum", "2132501716")
        command.append("dealerIconsCheckSum", "")
        command.append("remote_feature_support_version", "1")
        command.append("current_battery_status", "Normal")
        command.append("remote_panel_battery_percentage", 100)
        command.append("remote_panel_battery_temperature", 430)
        command.append("remote_panel_battery_status", 3)
        command.append("remote_panel_battery_scale", 100)
        command.append("remote_panel_battery_voltage", 4102)
        command.append("remote_panel_battery_present", True)
        command.append("remote_panel_battery_technology", "")
        command.append("remote_panel_battery_level", 100)
        command.append("remote_panel_battery_health", 2)
        command.append("remote_panel_plugged", 1)
        command.append("dhcpInfo", json.dumps(dhcpInfo))

        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving connect command")
        return response

    async def command_pairing_request(self) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending pairing_request command")
        command = MQTTCommand(self, "connect_v204")

        dhcpInfo = {
            "ipaddress": "",
            "gateway": "",
            "netmask": "",
            "dns1": "",
            "dns2": "",
            "dhcpServer": "",
            "leaseDuration": "",
        }

        command.append("pairing_request", True)
        command.append("ipAddress", self.settings.plugin_ip)
        command.append("macAddress", self.settings.random_mac)
        command.append("remoteClientID", self.settings.mqtt_remote_client_id)
        command.append("softwareVersion", "4.4.1")
        command.append("productType", "tab07_rk68")
        command.append("bssid", "")
        command.append("lastUpdateChecksum", "2132501716")
        command.append("dealerIconsCheckSum", "")
        command.append("remote_feature_support_version", "1")
        command.append("dhcpInfo", json.dumps(dhcpInfo))

        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving pairing_request command")
        return response

    async def command_pingevent(self) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending pingevent command")
        command = MQTTCommand(self, "pingevent")
        command.append("remote_panel_status", "Active")
        command.append("macAddress", self.settings.random_mac)
        command.append("ipAddress", self.settings.plugin_ip)
        command.append("current_battery_status", "Normal")
        command.append("remote_panel_battery_percentage", 100)
        command.append("remote_panel_battery_temperature", 430)
        command.append("remote_panel_battery_status", 3)
        command.append("remote_panel_battery_scale", 100)
        command.append("remote_panel_battery_voltage", 4102)
        command.append("remote_panel_battery_present", True)
        command.append("remote_panel_battery_technology", "")
        command.append("remote_panel_battery_level", 100)
        command.append("remote_panel_battery_health", 2)
        command.append("remote_panel_plugged", 1)

        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving pingevent command")
        return response

    async def command_timesync(self) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending timeSync command")
        command = MQTTCommand(self, "timeSync")
        command.append("startTimestamp", int(time.time()))
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving timeSync command")
        return response

    async def command_sync_database(self) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending syncdatabase command")
        command = MQTTCommand(self, "syncdatabase")
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving syncdatabase command")
        return response

    async def command_acstatus(self) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending acStatus command")
        command = MQTTCommand(self, "acStatus")
        command.append("acStatus", "Connected")
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving acStatus command")
        return response

    async def command_dealer_logo(self) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending dealerLogo command")
        command = MQTTCommand(self, "dealerLogo")
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving dealerLogo command")
        return response

    async def command_pair_status_request(self) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending pair_status_request command")
        command = MQTTCommand(self, "pair_status_request")
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving pair_status_request command")
        return response

    async def command_disconnect(self) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending disconnect command")
        command = MQTTCommand(self, "disconnect")
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving disconnect command")
        return response

    async def command_ui_delay(self, partition_id: str, silent_disarming: bool = False) -> dict[str, Any] | None:
        LOGGER.debug("MQTT: Sending ui_delay command")
        command = MQTTCommand_Panel(self)

        # partition state needs to be sent for ui_delay to work
        partition = self.state.partition(partition_id)
        if not partition:
            LOGGER.error("command_ui_delay error: invalid partition %s", partition_id)
            return None

        arming_command = {
            "operation_name": "ui_delay",
            "panel_status": partition.system_status,
            "userID": 0,
            "partitionID": partition_id,  # STR EXPECTED
            "silentDisarming": silent_disarming,
            "operation_source": 1,
            "macAddress": self.settings.random_mac,
        }

        ipcRequest = [
            {
                "dataType": "string",
                "dataValue": json.dumps(arming_command),
            }
        ]

        command.append("ipcRequest", ipcRequest)
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving ui_delay command")
        return response

    async def command_disarm(
        self, partition_id: str, user_code: str = "", silent_disarming: bool = False
    ) -> dict[str, Any] | None:
        partition = self.state.partition(partition_id)
        if not partition:
            LOGGER.error("MQTT: disarm command error - Unknow Partition")
            return None

        # Do local user code verification
        user_id = 1
        if self.settings.check_user_code_on_disarm:
            user_id = self.panel.check_user(user_code)
            if user_id == -1:
                LOGGER.debug("MQTT: disarm command error - user_code error")
                raise QolsysUserCodeError()

        async def get_mqtt_disarm_command(silent_disarming: bool) -> str:
            if partition.alarm_state == PartitionAlarmState.ALARM:
                return "disarm_from_emergency"
            if partition.system_status in {
                PartitionSystemStatus.ARM_AWAY_EXIT_DELAY,
                PartitionSystemStatus.ARM_STAY_EXIT_DELAY,
                PartitionSystemStatus.ARM_NIGHT_EXIT_DELAY,
            }:
                return "disarm_from_openlearn_sensor"
            if partition.system_status in {
                PartitionSystemStatus.ARM_AWAY,
                PartitionSystemStatus.ARM_STAY,
                PartitionSystemStatus.ARM_NIGHT,
            }:
                await self.command_ui_delay(partition_id, silent_disarming)
                return "disarm_the_panel_from_entry_delay"

            return "disarm_from_openlearn_sensor"

        mqtt_disarm_command = await get_mqtt_disarm_command(silent_disarming)
        LOGGER.debug("MQTT: Sending disarm command - check_user_code:%s", self.settings.check_user_code_on_disarm)

        disarm_command = {
            "operation_name": mqtt_disarm_command,
            "userID": user_id,
            "partitionID": int(partition_id),  # INT EXPECTED
            "operation_source": 1,
            "macAddress": self.settings.random_mac,
        }

        ipc_request = [
            {
                "dataType": "string",
                "dataValue": json.dumps(disarm_command),
            }
        ]

        command = MQTTCommand_Panel(self)
        command.append_ipc_request(ipc_request)
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving disarm command")
        return response

    async def command_arm(
        self,
        partition_id: str,
        arming_type: PartitionArmingType,
        user_code: str = "",
        exit_sounds: bool = False,
        instant_arm: bool = False,
        entry_delay: bool = True,
    ) -> dict[str, str] | None:
        LOGGER.debug(
            "MQTT: Sending arm command: partition%s, arming_type:%s, exit_sounds:%s, instant_arm: %s, entry_delay:%s",
            partition_id,
            arming_type,
            exit_sounds,
            instant_arm,
            entry_delay,
        )

        user_id = 0

        partition = self.state.partition(partition_id)
        if not partition:
            LOGGER.debug("MQTT: arm command error - Unknow Partition")
            return None

        if self.settings.check_user_code_on_arm:
            # Do local user code verification to arm
            user_id = self.panel.check_user(user_code)
            if user_id == -1:
                LOGGER.debug("MQTT: arm command error - user_code error")
                raise QolsysUserCodeError()

        exitSoundValue = "ON"
        if not exit_sounds:
            exitSoundValue = "OFF"

        entryDelay = "ON"
        if not entry_delay:
            entryDelay = "OFF"

        bypass_zone_list: list[int] = []
        # Bypass Zone if AutoBypass is enabled

        if self.panel.AUTO_BYPASS == "true":
            for zone in self.state.zones:
                if zone.partition_id == partition_id:
                    # Skip safety zones
                    if zone.sensorgroup in SafetyZoneSensorGroup:
                        continue

                    # Add bypass capable zones in trouble status
                    if zone.sensortype in BypassCapableZoneSensorType and zone.sensorstatus in TroubleZoneStatus:
                        LOGGER.debug("Bypassing Zone%s - %s: %s", zone.zone_id, zone.sensortype, zone.sensorstatus)
                        bypass_zone_list.append(int(zone.zone_id))

        bypass_zone_str = "[" + ",".join(map(str, bypass_zone_list)) + "]"
        LOGGER.debug("Bypass Zone List: %s", bypass_zone_str)

        arming_command = {
            "operation_name": arming_type,
            "bypass_zoneid_set": bypass_zone_str,
            "userID": user_id,
            "partitionID": int(partition_id),  # Expect Int
            "exitSoundValue": exitSoundValue,
            "entryDelayValue": entryDelay,
            "multiplePartitionsSelected": False,
            "instant_arming": instant_arm,
            "final_exit_arming_selected": False,
            "manually_selected_zones": "[]",
            "operation_source": 1,
            "macAddress": self.settings.random_mac,
        }

        ipc_request = [
            {
                "dataType": "string",
                "dataValue": json.dumps(arming_command),
            }
        ]

        command = MQTTCommand_Panel(self)
        command.append_ipc_request(ipc_request)
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving arm command: partition%s", partition_id)
        return response

    async def command_panel_execute_scene(self, scene_id: str) -> dict[str, Any] | None:
        LOGGER.debug("MQTT: Sending execute_scene command")
        scene = self.state.scene(scene_id)
        if not scene:
            LOGGER.debug("MQTT: command_execute_scene Erro - Unknow Scene: %s", scene_id)
            return None

        scene_command = {
            "operation_name": "execute_scene",
            "scene_id": int(scene.scene_id),
            "operation_source": 1,
            "macAddress": self.settings.random_mac,
        }

        ipc_request = [
            {
                "dataType": "string",
                "dataValue": json.dumps(scene_command),
            }
        ]

        command = MQTTCommand_Panel(self)
        command.append_ipc_request(ipc_request)
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving execute_scene command")
        return response

    async def command_panel_virtual_device_action(
        self, device_id: str, service_id: int, state: vdFuncState
    ) -> dict[str, Any] | None:
        LOGGER.debug(
            "MQTT: Sending virtual_device_action device: %s, service: %s state: %s", device_id, service_id, state.name
        )

        device = self.state.automation_device(device_id)
        if not isinstance(device, QolsysAutomationDeviceADC):
            raise InvalidVirtualNodeError(device_id)

        service = device.service_get_adc(service_id)
        if not isinstance(service, (LightServiceADC, CoverServiceADC, StatusServiceADC)):
            raise ServiceNotFoundError(device_id, str(service_id), "LightServiceADC, CoverServiceADC or StatusServiceADC")

        device_list = {
            "virtualDeviceList": [
                {
                    "virtualDeviceId": int(device_id),
                    "virtualDeviceFunctionList": [
                        {
                            "vdFuncId": service_id,
                            "vdFuncState": state,
                            "vdFuncBackendTimestamp": int(time.time() * 1000),
                            "vdFuncType": service.func_type,
                        }
                    ],
                }
            ]
        }

        virtual_command = {
            "operation_name": "send_virtual_device_description",
            "virtual_device_operation": 4,
            "virtual_device_description": json.dumps(device_list),
        }

        ipc_request = [
            {
                "dataType": "string",
                "dataValue": json.dumps(virtual_command),
            }
        ]

        LOGGER.debug("virtual command: %s", virtual_command)
        command = MQTTCommand_Panel(self)
        command.append_ipc_request(ipc_request)
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving virtual_device command: %s", response)
        return response

    async def command_panel_trigger_police(self, partition_id: str, silent: bool) -> dict[str, Any] | None:
        LOGGER.debug("MQTT: Sending panel_trigger_police command")

        partition = self.state.partition(partition_id)
        if not partition:
            LOGGER.debug("MQTT: command_panel_trigger_police Error - Unknow Partition: %s", partition_id)
            return None

        trigger_command = {
            "operation_name": "generate_emergency",
            "partitionID": int(partition_id),
            "zoneID": int(self._zone_id),
            "emergencyType": "Silent Police Emergency" if silent else "Police Emergency",
            "operation_source": 1,
            "macAddress": self.settings.random_mac,
        }

        ipc_request = [
            {
                "dataType": "string",
                "dataValue": json.dumps(trigger_command),
            }
        ]

        command = MQTTCommand_Panel(self)
        command.append_ipc_request(ipc_request)
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving panel_trigger_police command")
        return response

    async def command_panel_trigger_auxilliary(self, partition_id: str, silent: bool) -> dict[str, Any] | None:
        LOGGER.debug("MQTT: Sending panel_trigger_auxilliary command")

        partition = self.state.partition(partition_id)
        if not partition:
            LOGGER.debug("MQTT: command_panel_trigger_auxilliary Error - Unknow Partition: %s", partition_id)
            return None

        trigger_command = {
            "operation_name": "generate_emergency",
            "partitionID": int(partition_id),
            "zoneID": int(self._zone_id),
            "emergencyType": "Silent Auxiliary Emergency" if silent else "Auxiliary Emergency",
            "operation_source": 1,
            "macAddress": self.settings.random_mac,
        }

        ipc_request = [
            {
                "dataType": "string",
                "dataValue": json.dumps(trigger_command),
            }
        ]

        command = MQTTCommand_Panel(self)
        command.append_ipc_request(ipc_request)
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving panel_trigger_auxilliary command")
        return response

    async def command_panel_trigger_fire(self, partition_id: str) -> dict[str, Any] | None:
        LOGGER.debug("MQTT: Sending panel_trigger_fire command")

        partition = self.state.partition(partition_id)
        if not partition:
            LOGGER.debug("MQTT: command_panel_trigger_fire Error - Unknow Partition: %s", partition_id)
            return None

        trigger_command = {
            "operation_name": "generate_emergency",
            "partitionID": int(partition_id),
            "zoneID": int(self._zone_id),
            "emergencyType": "Fire Emergency",
            "operation_source": 1,
            "macAddress": self.settings.random_mac,
        }

        ipc_request = [
            {
                "dataType": "string",
                "dataValue": json.dumps(trigger_command),
            }
        ]

        command = MQTTCommand_Panel(self)
        command.append_ipc_request(ipc_request)
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving panel_trigger_fire command")
        return response

    async def command_panel_speak(self, text: str) -> dict[str, Any] | None:
        LOGGER.debug("MQTT: Sending panel_speak command")

        speak_command = {
            "operation_name": "speak_text",
            "tts_text": text,
            "operation_source": 1,
            "macAddress": self.settings.random_mac,
        }

        ipc_request = [
            {
                "dataType": "string",
                "dataValue": json.dumps(speak_command),
            }
        ]

        command = MQTTCommand_Panel(self)
        command.append_ipc_request(ipc_request)
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving panel_speak command")
        return response

    async def command_zwave_switch_binary_set(self, node_id: str, endpoint: str, status: bool) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending zwave_switch_binary_set command  - Node(%s) - Status(%s)", node_id, status)
        node = self.state.automation_device(node_id)

        if not isinstance(node, QolsysAutomationDeviceZwave):
            raise InvalidVirtualNodeError(node_id)

        service = node.service_get(LightServiceZwave, int(endpoint))
        if not isinstance(service, (LightServiceZwave, ValveService, SirenService)):
            raise ServiceNotFoundError(node_id, endpoint, "LightServiceZwave, ValveService or SirenService")

        level = 0
        if status:
            level = 255

        switch_set = [ZwaveCommandClass.SwitchBinary.value, 1, level]
        command: MQTTCommand_ZWave | MQTTCommand_ZWave_Old
        if self.panel.product_type == QolsysPanelType.IQ_PANEL_2_PLUS:
            secure_level = 1
            command = MQTTCommand_ZWave_Old(self, node_id, int(endpoint), secure_level, [switch_set])
        else:
            command = MQTTCommand_ZWave(self, node_id, endpoint, switch_set)

        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving set_zwave_switch_binary command")
        return response

    async def command_zwave_switch_multilevel_set(self, node_id: str, endpoint: str, level: int) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending switch_multilevel_set command  - Node(%s) - Level(%s)", node_id, level)

        node = self.state.automation_device(node_id)
        if not isinstance(node, QolsysAutomationDeviceZwave):
            raise InvalidVirtualNodeError(node_id)

        service = node.service_get(LightServiceZwave, int(endpoint))
        if not isinstance(service, LightServiceZwave):
            raise ServiceNotFoundError(node_id, endpoint, "LightServiceZwave")

        switch_set = [ZwaveCommandClass.SwitchMultilevel.value, 1, level]
        command: MQTTCommand_ZWave | MQTTCommand_ZWave_Old
        if self.panel.product_type == QolsysPanelType.IQ_PANEL_2_PLUS:
            secure_level = 1
            command = MQTTCommand_ZWave_Old(self, node_id, int(endpoint), secure_level, [switch_set])
        else:
            command = MQTTCommand_ZWave(self, node_id, endpoint, switch_set)

        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving switch_multilevel_set command")
        return response

    async def command_zwave_barrier_operator_set(self, node_id: str, endpoint: str, status: int) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending barrier_operator_set command  - Node(%s) - Status(%s)", node_id, status)

        node = self.state.automation_device(node_id)
        if not isinstance(node, QolsysAutomationDeviceZwave):
            raise InvalidVirtualNodeError(node_id)

        service = node.service_get(CoverServiceZwave, int(endpoint))
        if not isinstance(service, CoverServiceZwave):
            raise ServiceNotFoundError(node_id, endpoint, "CoverServiceZwave")

        barrier_operator_set = [ZwaveCommandClass.BarrierOperator.value, 1, status]
        command: MQTTCommand_ZWave | MQTTCommand_ZWave_Old
        if self.panel.product_type == QolsysPanelType.IQ_PANEL_2_PLUS:
            secure_level = 1
            command = MQTTCommand_ZWave_Old(self, node_id, int(endpoint), secure_level, [barrier_operator_set])
        else:
            command = MQTTCommand_ZWave(self, node_id, endpoint, barrier_operator_set)

        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving barrier_operator_set command")
        return response

    async def command_zwave_doorlock_set(self, node_id: str, endpoint: str, locked: bool) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending zwave_doorlock_set command - Node(%s) - Locked(%s)", node_id, locked)

        node = self.state.automation_device(node_id)
        if not isinstance(node, QolsysAutomationDeviceZwave):
            raise InvalidVirtualNodeError(node_id)

        service = node.service_get(LockServiceZwave, int(endpoint))
        if not isinstance(service, LockServiceZwave):
            raise ServiceNotFoundError(node_id, endpoint, "LockServiceZwave")

        # 0 unlocked, 255 locked
        lock_mode = 0
        if locked:
            lock_mode = 255

        doorlock_set = [ZwaveCommandClass.DoorLock.value, 1, lock_mode]
        command: MQTTCommand_ZWave | MQTTCommand_ZWave_Old
        if self.panel.product_type == QolsysPanelType.IQ_PANEL_2_PLUS:
            secure_level = 1
            command = MQTTCommand_ZWave_Old(self, node_id, int(endpoint), secure_level, [doorlock_set])
        else:
            command = MQTTCommand_ZWave(self, node_id, endpoint, doorlock_set)

        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving zwave_doorlock_set command")
        return response

    async def command_zwave_thermostat_setpoint_set(
        self, node_id: str, endpoint: str, mode: ThermostatSetpointMode, setpoint: int
    ) -> dict[str, Any]:
        node = self.state.automation_device(node_id)
        if not isinstance(node, QolsysAutomationDeviceZwave):
            raise InvalidVirtualNodeError(node_id)

        service = node.service_get(ThermostatServiceZwave, int(endpoint))
        if not isinstance(service, ThermostatServiceZwave):
            raise ServiceNotFoundError(node_id, endpoint, "ThermostatServiceZwave")

        scale: int = 0
        if service.device_temperature_unit == QolsysTemperatureUnit.FAHRENHEIT:
            scale = 1

        precision: int = 1
        size: int = 2
        pss = (precision << 5) | (scale << 3) | size
        temp_int = int(round(setpoint * (10**precision)))
        temp_bytes = temp_int.to_bytes(size, byteorder="big", signed=True)

        setpointmode = ThermostatSetpointMode.HEATING
        if mode == ThermostatSetpointMode.COOLING:
            setpointmode = mode

        zwave_bytes: list[int] = [
            0x43,  # Thermostat Setpoint
            0x01,  # SET
            setpointmode.value,
            pss,
        ] + list(temp_bytes)

        LOGGER.debug(
            "MQTT: Sending zwave_thermostat_setpoint_set - Node(%s) - Mode(%s) - Setpoint(%s): %s",
            node_id,
            mode.value,
            setpoint,
            zwave_bytes,
        )

        command: MQTTCommand_ZWave | MQTTCommand_ZWave_Old
        if self.panel.product_type == QolsysPanelType.IQ_PANEL_2_PLUS:
            secure_level = 1
            command = MQTTCommand_ZWave_Old(self, node_id, int(endpoint), secure_level, [zwave_bytes])
        else:
            command = MQTTCommand_ZWave(self, node_id, endpoint, zwave_bytes)

        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving zwave_thermostat_mode_set command:%s", response)
        return response

    async def command_zwave_thermostat_mode_set(self, node_id: str, endpoint: str, mode: ThermostatMode) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending zwave_thermostat_mode_set command - Node(%s) - Mode(%s)", node_id, mode.name)
        node = self.state.automation_device(node_id)

        if not isinstance(node, QolsysAutomationDeviceZwave):
            raise InvalidVirtualNodeError(node_id)

        service = node.service_get(ThermostatServiceZwave, int(endpoint))
        if not isinstance(service, ThermostatServiceZwave):
            raise ServiceNotFoundError(node_id, endpoint, "ThermostatServiceZwave")

        mode_command = [ZwaveCommandClass.ThermostatMode.value, 1, int(mode)]
        command: MQTTCommand_ZWave | MQTTCommand_ZWave_Old
        if self.panel.product_type == QolsysPanelType.IQ_PANEL_2_PLUS:
            secure_level = 1
            command = MQTTCommand_ZWave_Old(self, node_id, int(endpoint), secure_level, [mode_command])
        else:
            command = MQTTCommand_ZWave(self, node_id, endpoint, mode_command)

        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving zwave_thermostat_mode_set command")
        return response

    async def command_zwave_thermostat_fan_mode_set(
        self, node_id: str, endpoint: str, fan_mode: ThermostatFanMode
    ) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending zwave_thermostat_fan_mode_set command - Node(%s) - FanMode(%s)", node_id, fan_mode.name)

        node = self.state.automation_device(node_id)
        if not isinstance(node, QolsysAutomationDeviceZwave):
            raise InvalidVirtualNodeError(node_id)

        service = node.service_get(ThermostatServiceZwave, int(endpoint))
        if not isinstance(service, ThermostatServiceZwave):
            raise ServiceNotFoundError(node_id, endpoint, "ThermostatServiceZwave")

        fan_command = [ZwaveCommandClass.ThermostatFanMode.value, 1, fan_mode]
        command: MQTTCommand_ZWave | MQTTCommand_ZWave_Old
        if self.panel.product_type == QolsysPanelType.IQ_PANEL_2_PLUS:
            secure_level = 1
            command = MQTTCommand_ZWave_Old(self, node_id, int(endpoint), secure_level, [fan_command])
        else:
            command = MQTTCommand_ZWave(self, node_id, endpoint, fan_command)

        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving zwave_thermostat_fan_mode_set command")
        return response

    async def command_automation_door_lock(self, virtual_node_id: int, endpoint: int) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending automation_door_lock command - Node(%s)(%s)", virtual_node_id, endpoint)

        # Check if virtual_node_id exist
        virtual_node = self.state.automation_device(str(virtual_node_id))
        if not virtual_node:
            raise InvalidVirtualNodeError(virtual_node_id)

        command = MQTTCommand_Automation(self, virtual_node_id, endpoint, operation_type=5, result="status_Locked")
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving automation_door_lock command: %s", response)
        return response

    async def command_automation_door_unlock(self, virtual_node_id: int, endpoint: int) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending automation_door_unlock command - Node(%s)(%s)", virtual_node_id, endpoint)

        # Check if virtual_node_id exist
        virtual_node = self.state.automation_device(str(virtual_node_id))
        if not virtual_node:
            raise InvalidVirtualNodeError(virtual_node_id)

        command = MQTTCommand_Automation(self, virtual_node_id, endpoint, operation_type=6, result="status_Unlocked")
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving  automation_door_unlock command: %s", response)
        return response

    async def command_automation_light_on(self, virtual_node_id: int, endpoint: int) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending automation_light_on command - Node(%s)(%s)", virtual_node_id, endpoint)

        # Check if virtual_node_id exist
        virtual_node = self.state.automation_device(str(virtual_node_id))
        if not virtual_node:
            raise InvalidVirtualNodeError(virtual_node_id)

        command = MQTTCommand_Automation(self, virtual_node_id, endpoint, operation_type=1, result="status_On")
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving automation_light_on command")
        return response

    async def command_automation_light_off(self, virtual_node_id: int, endpoint: int) -> dict[str, Any]:
        LOGGER.debug("MQTT: Sending automation_light_off command - Node(%s)(%s)", virtual_node_id, endpoint)

        # Check if virtual_node_id exist
        virtual_node = self.state.automation_device(str(virtual_node_id))
        if not virtual_node:
            raise InvalidVirtualNodeError(virtual_node_id)

        command = MQTTCommand_Automation(self, virtual_node_id, endpoint, operation_type=0, result="status_Off")
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving automation_light_off command")
        return response
