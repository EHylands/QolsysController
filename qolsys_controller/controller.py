#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import base64
import contextlib
import json
import logging
import random
import ssl
import time
from typing import Any

import aiofiles
import aiomqtt

from qolsys_controller.mqtt_command import (
    MQTTCommand,
    MQTTCommand_Panel,
    MQTTCommand_ZWave,
)

from .enum import PartitionAlarmState, PartitionArmingType, PartitionSystemStatus
from .enum_zwave import ThermostatFanMode, ThermostatMode, ZwaveCommand, ZwaveDeviceClass
from .errors import QolsysMqttError, QolsysSslError, QolsysUserCodeError
from .mdns import QolsysMDNS
from .mqtt_command_queue import QolsysMqttCommandQueue
from .observable import QolsysObservable
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

        self.connected = False
        self.connected_observer = QolsysObservable()

        # PKI
        self._pki = QolsysPKI(settings=self.settings)

        # Plugin
        self.certificate_exchange_server: asyncio.Server | None = None
        self._task_manager = QolsysTaskManager()
        self._mqtt_command_queue = QolsysMqttCommandQueue()

        # MQTT Client
        self.aiomqtt: aiomqtt.Client | None = None
        self._mqtt_task_config_label: str = "mqtt_task_config"
        self._mqtt_task_listen_label: str = "mqtt_task_listen"
        self._mqtt_task_connect_label: str = "mqtt_task_connect"
        self._mqtt_task_ping_label: str = "mqtt_task_ping"

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

    def is_paired(self) -> bool:
        return (
            self._pki.id != ""
            and self._pki.check_key_file()
            and self._pki.check_cer_file()
            and self._pki.check_qolsys_cer_file()
            and self._pki.check_secure_file()
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

        # Set mqtt_remote_client_id
        self.settings.mqtt_remote_client_id = "qolsys-controller-" + self._pki.formatted_id()
        LOGGER.debug("Using MQTT remoteClientID: %s", self.settings.mqtt_remote_client_id)

        # Check if plugin is paired
        if self.is_paired():
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

    async def start_operation(self) -> None:
        await self._task_manager.run(self.mqtt_connect_task(reconnect=True, run_forever=True), self._mqtt_task_connect_label)

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

        self.connected = False
        self.connected_observer.notify()

    async def mqtt_connect_task(self, reconnect: bool, run_forever: bool) -> None:
        # Configure TLS parameters for MQTT connection
        tls_params = aiomqtt.TLSParameters(
            ca_certs=str(self._pki.qolsys_cer_file_path),
            certfile=str(self._pki.secure_file_path),
            keyfile=str(self._pki.key_file_path),
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
            ciphers="ALL:@SECLEVEL=0",
        )

        LOGGER.debug("MQTT: Connecting ...")

        self._task_manager.cancel(self._mqtt_task_listen_label)
        self._task_manager.cancel(self._mqtt_task_ping_label)

        while True:
            try:
                self.aiomqtt = aiomqtt.Client(
                    hostname=self.settings.panel_ip,
                    port=8883,
                    tls_params=tls_params,
                    tls_insecure=True,
                    clean_session=True,
                    timeout=self.settings.mqtt_timeout,
                    identifier=self.settings.mqtt_remote_client_id,
                )

                await self.aiomqtt.__aenter__()

                LOGGER.info("MQTT: Client Connected")

                # Subscribe to panel internal database updates
                await self.aiomqtt.subscribe("iq2meid")

                # Subscribte to MQTT private response
                await self.aiomqtt.subscribe("response_" + self.settings.random_mac, qos=self.settings.mqtt_qos)

                # Subscribe to Z-Wave response
                await self.aiomqtt.subscribe("ZWAVE_RESPONSE", qos=self.settings.mqtt_qos)

                # Only log all traffic for debug purposes
                if self.settings.log_mqtt_mesages:
                    # Subscribe to MQTT commands send to panel by other devices
                    await self.aiomqtt.subscribe("mastermeid", qos=self.settings.mqtt_qos)

                    # Subscribe to all topics
                    # await self.aiomqtt.subscribe("#", qos=self.settings.mqtt_qos)

                self._task_manager.run(self.mqtt_listen_task(), self._mqtt_task_listen_label)
                self._task_manager.run(self.mqtt_ping_task(), self._mqtt_task_ping_label)

                response_connect = await self.command_connect()

                self.panel.imei = response_connect.get("master_imei", "")
                self.panel.product_type = response_connect.get("primary_product_type", "")

                await self.command_pingevent()
                await self.command_pair_status_request()

                response_database = await self.command_sync_database()
                LOGGER.debug("MQTT: Updating State from syncdatabase")
                self.panel.load_database(response_database.get("fulldbdata"))  # type: ignore[arg-type]
                self.panel.dump()
                self.state.dump()

                self.connected = True
                self.connected_observer.notify()

                if not run_forever:
                    self.connected = False
                    self.connected_observer.notify()
                    self._task_manager.cancel(self._mqtt_task_listen_label)
                    self._task_manager.cancel(self._mqtt_task_ping_label)
                    await self.aiomqtt.__aexit__(None, None, None)

                break

            except aiomqtt.MqttError as err:
                # Receive pannel network error
                self.connected = False
                self.connected_observer.notify()
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
                self.connected_observer.notify()
                self.aiomqtt = None
                raise QolsysSslError from err

    async def mqtt_ping_task(self) -> None:
        while True:
            if self.aiomqtt is not None and self.connected:
                with contextlib.suppress(aiomqtt.MqttError):
                    await self.command_pingevent()

            await asyncio.sleep(self.settings.mqtt_ping)

    async def mqtt_listen_task(self) -> None:
        try:
            async for message in self.aiomqtt.messages:  # type: ignore[union-attr]
                if self.settings.log_mqtt_mesages:  # noqa: SIM102
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
                        zwave = data.get("ZWAVE_RESPONSE", "")
                        decoded_payload = base64.b64decode(zwave.get("ZWAVE_PAYLOAD", "")).hex()
                        LOGGER.debug(
                            "Z-Wave Response: Node(%s) - Status(%s) - Payload(%s)",
                            zwave.get("NODE_ID", ""),
                            zwave.get("ZWAVE_COMMAND_STATUS", ""),
                            decoded_payload,
                        )

        except aiomqtt.MqttError as err:
            self.connected = False
            self.connected_observer.notify()

            LOGGER.debug("%s: Listen - Reconnecting in %s seconds ...", err, self.settings.mqtt_timeout)
            await asyncio.sleep(self.settings.mqtt_timeout)
            self._task_manager.run(self.mqtt_connect_task(reconnect=True, run_forever=True), self._mqtt_task_connect_label)

    async def start_initial_pairing(self) -> bool:
        # check if random_mac exist
        if self.settings.random_mac == "":
            LOGGER.debug("Creating random_mac")
            self.settings.random_mac = generate_random_mac()
            self._pki.create(self.settings.random_mac, key_size=self.settings.key_size)

        # Check if PKI is valid
        self._pki.set_id(self.settings.random_mac)
        LOGGER.debug("Checking PKI")
        if not (self._pki.check_key_file() and self._pki.check_cer_file() and self._pki.check_csr_file()):
            LOGGER.error("PKI Error")
            return False

        LOGGER.debug("Starting Pairing Process")

        if not self.settings.check_plugin_ip():
            LOGGER.error("Plugin IP Address not configured")
            return False

        # If we dont allready have client signed certificate, start the pairing server
        if not self._pki.check_secure_file() or not self._pki.check_qolsys_cer_file() or not self.settings.check_panel_ip():
            # High Level Random Pairing Port
            pairing_port = random.randint(50000, 55000)

            # Start Pairing mDNS Brodcast
            LOGGER.debug("Starting mDNS Service Discovery: %s:%s", self.settings.plugin_ip, str(pairing_port))
            mdns_server = QolsysMDNS(self.settings.plugin_ip, pairing_port)
            await mdns_server.start_mdns()

            # Start Key Exchange Server
            LOGGER.debug("Starting Certificate Exchange Server")
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=self._pki.cer_file_path, keyfile=self._pki.key_file_path)
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
        LOGGER.debug("Determined MQTT disarm command: %s", mqtt_disarm_command)
        LOGGER.debug("MQTT: Sending disarm command - check_user_code:%s", self.settings.check_user_code_on_disarm)

        disarm_command = {
            "operation_name": mqtt_disarm_command,
            "userID": user_id,
            "partitionID": int(partition_id),  # INT EXPECTED
            "operation_source": 1,
            "macAddress": self.settings.random_mac,
        }

        LOGGER.debug("Disarm Command Payload: %s", disarm_command)

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

        arming_command = {
            "operation_name": arming_type,
            "bypass_zoneid_set": "[]",
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
            "scene_id": scene.scene_id,
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

    async def command_panel_trigger_police(self, partition_id: str, silent: bool) -> dict[str, Any] | None:
        LOGGER.debug("MQTT: Sending panel_trigger_police command")

        partition = self.state.partition(partition_id)
        if not partition:
            LOGGER.debug("MQTT: command_panel_trigger_police Error - Unknow Partition: %s", partition_id)
            return None

        trigger_command = {
            "operation_name": "generate_emergency",
            "partitionID": int(partition_id),
            "zoneID": 1,
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
            "zoneID": 1,
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
            "zoneID": 1,
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

    async def command_zwave_switch_binary_set(self, node_id: str, status: bool) -> dict[str, Any] | None:
        LOGGER.debug("MQTT: Sending set_zwave_switch_binary command  - Node(%s) - Status(%s)", node_id, status)
        zwave_node = self.state.zwave_device(node_id)

        if not zwave_node:
            LOGGER.error("switch_binary_set - Invalid node_id %s", node_id)
            return None

        if zwave_node.generic_device_type not in (ZwaveDeviceClass.SwitchBinary, ZwaveDeviceClass.RemoteSwitchBinary):
            LOGGER.error("switch_binary_set used on invalid %s", zwave_node.generic_device_type)
            return None

        level = 0
        if status:
            level = 255

        command = MQTTCommand_ZWave(self, node_id, [ZwaveCommand.SwitchBinary, 1, level])
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving set_zwave_switch_binary command")
        return response

    async def command_zwave_switch_multilevel_set(self, node_id: str, level: int) -> dict[str, Any] | None:
        LOGGER.debug("MQTT: Sending switch_multilevel_set command  - Node(%s) - Level(%s)", node_id, level)

        zwave_node = self.state.zwave_device(node_id)
        if not zwave_node:
            LOGGER.error("switch_multilevel_set - Invalid node_id %s", node_id)
            return None

        if zwave_node.generic_device_type not in (ZwaveDeviceClass.SwitchMultilevel, ZwaveDeviceClass.RemoteSwitchMultilevel):
            LOGGER.error("switch_multilevel_set used on invalid %s", zwave_node.generic_device_type)
            return None

        command = MQTTCommand_ZWave(self, node_id, [ZwaveCommand.SwitchMultilevel, 1, level])
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving set_zwave_multilevel_switch command")
        return response

    async def command_zwave_doorlock_set(self, node_id: str, locked: bool) -> dict[str, Any] | None:
        LOGGER.debug("MQTT: Sending zwave_doorlock_set command - Node(%s) - Locked(%s)", node_id, locked)

        zwave_node = self.state.zwave_device(node_id)
        if not zwave_node:
            LOGGER.error("doorlock_set - Invalid node_id %s", node_id)
            return None

        # 0 unlocked, 255 locked
        lock_mode = 0
        if locked:
            lock_mode = 255

        command = MQTTCommand_ZWave(self, node_id, [ZwaveCommand.DoorLock, 1, lock_mode])
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving zwave_doorlock_set command")
        return response

    async def command_zwave_thermostat_setpoint_set(
        self, node_id: str, mode: ThermostatMode, setpoint: float
    ) -> dict[str, Any] | None:
        LOGGER.debug(
            "MQTT: Sending zwave_thermostat_setpoint_set - Node(%s) - Mode(%s) - Setpoint(%s)", node_id, mode, setpoint
        )

        zwave_node = self.state.zwave_device(node_id)
        if not zwave_node:
            LOGGER.error("thermostat_setpoint_set - Invalid node_id %s", node_id)
            return None

        command = MQTTCommand_ZWave(self, node_id, [ZwaveCommand.ThermostatSetPoint, 1, mode, int(setpoint)])
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving zwave_thermostat_mode_set command")
        return response

    async def command_zwave_thermostat_mode_set(self, node_id: str, mode: ThermostatMode) -> dict[str, Any] | None:
        LOGGER.debug("MQTT: Sending zwave_thermostat_mode_set command - Node(%s) - Mode(%s)", node_id, mode)

        zwave_node = self.state.zwave_device(node_id)
        if not zwave_node:
            LOGGER.error("thermostat_mode_set - Invalid node_id %s", node_id)
            return None

        command = MQTTCommand_ZWave(self, node_id, [ZwaveCommand.ThermostatMode, 1, mode])
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving zwave_thermostat_mode_set command")
        return response

    async def command_zwave_thermostat_fan_mode_set(self, node_id: str, fan_mode: ThermostatFanMode) -> dict[str, Any] | None:
        LOGGER.debug("MQTT: Sending zwave_thermostat_fan_mode_set command - Node(%s) - FanMode(%s)", node_id, fan_mode)

        zwave_node = self.state.zwave_device(node_id)
        if not zwave_node:
            LOGGER.error("thermostat_fan_mode_set - Invalid node_id %s", node_id)
            return None

        command = MQTTCommand_ZWave(self, node_id, [ZwaveCommand.ThermostatFanMode, 1, fan_mode])
        response = await command.send_command()
        LOGGER.debug("MQTT: Receiving zwave_thermostat_fan_mode_set command")
        return response
