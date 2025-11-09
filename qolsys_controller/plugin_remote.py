from __future__ import annotations

import asyncio
import base64
import contextlib
import datetime
import json
import logging
import random
import ssl
import uuid
from typing import TYPE_CHECKING

import aiofiles
import aiomqtt

from .enum import PartitionAlarmState, PartitionSystemStatus
from .errors import QolsysMqttError, QolsysSslError
from .mdns import QolsysMDNS
from .mqtt_command_queue import QolsysMqttCommandQueue
from .pki import QolsysPKI
from .plugin import QolsysPlugin
from .task_manager import QolsysTaskManager
from .utils_mqtt import generate_random_mac

LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .controller import QolsysController
    from .enum_zwave import ThermostatFanMode, ThermostatMode


class QolsysPluginRemote(QolsysPlugin):

    def __init__(self, controller: QolsysController) -> None:
        super().__init__(controller=controller)

        # PKI
        self._pki = QolsysPKI(settings=controller.settings)
        self._auto_discover_pki = True

        # Plugin
        self.certificate_exchange_server = None
        self._check_user_code_on_arm = False
        self._check_user_code_on_disarm = True
        self._log_mqtt_messages = False
        self._task_manager = QolsysTaskManager()
        self._mqtt_command_queue = QolsysMqttCommandQueue()

        # MQTT Client
        self.aiomqtt = None
        self._mqtt_task_config_label = "mqtt_task_config"
        self._mqtt_task_listen_label = "mqtt_task_listen"
        self._mqtt_task_connect_label = "mqtt_task_connect"
        self._mqtt_task_ping_label = "mqtt_task_ping"

    @property
    def log_mqtt_mesages(self) -> bool:
        return self._log_mqtt_messages

    @log_mqtt_mesages.setter
    def log_mqtt_mesages(self, log_mqtt_mesages: bool) -> None:
        self._log_mqtt_messages = log_mqtt_mesages

    @property
    def check_user_code_on_disarm(self) -> bool:
        return self._check_user_code_on_disarm

    @check_user_code_on_disarm.setter
    def check_user_code_on_disarm(self, check_user_code_on_disarm: bool) -> None:
        self._check_user_code_on_disarm = check_user_code_on_disarm

    @property
    def check_user_code_on_arm(self) -> bool:
        return self._check_user_code_on_arm

    @check_user_code_on_arm.setter
    def check_user_code_on_arm(self, check_user_code_on_arm: bool) -> None:
        self._check_user_code_on_arm = check_user_code_on_arm

    @property
    def auto_discover_pki(self) -> bool:
        return self._auto_discover_pki

    @auto_discover_pki.setter
    def auto_discover_pki(self, value: bool) -> None:
        self._auto_discover_pki = value

    def is_paired(self) -> bool:
        return (
            self._pki.id != "" and
            self._pki.check_key_file() and
            self._pki.check_cer_file() and
            self._pki.check_qolsys_cer_file() and
            self._pki.check_secure_file() and
            self._controller.settings.check_panel_ip() and
            self._controller.settings.check_plugin_ip()
        )

    async def config(self, start_pairing: bool) -> bool:
        return await self._task_manager.run(self.config_task(start_pairing), self._mqtt_task_config_label)

    async def config_task(self, start_pairing: bool) -> bool:
        LOGGER.debug("Configuring Plugin")
        super().config()

        # Check and created config_directory
        if not self._controller.settings.check_config_directory(create=start_pairing):
            return False

        # Read user file for access code
        loop = asyncio.get_running_loop()
        if not loop.run_in_executor(None, self._controller.panel.read_users_file):
            return False

        # Config PKI
        if self._auto_discover_pki:
            if self._pki.auto_discover_pki():
                self._controller.settings.random_mac = self._pki.formatted_id()
        else:
            self._pki.set_id(self._controller.settings.random_mac)

        # Set mqtt_remote_client_id
        self._controller.settings.mqtt_remote_client_id = "qolsys-controller-" + self._pki.formatted_id()
        LOGGER.debug("Using MQTT remoteClientID: %s", self._controller.settings.mqtt_remote_client_id)

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
            ca_certs=self._pki.qolsys_cer_file_path,
            certfile=self._pki.secure_file_path,
            keyfile=self._pki.key_file_path,
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
                    hostname=self._controller.settings.panel_ip,
                    port=8883,
                    tls_params=tls_params,
                    tls_insecure=True,
                    clean_session=True,
                    timeout=self._controller.settings.mqtt_timeout,
                    identifier= self._controller.settings.mqtt_remote_client_id,
                )

                await self.aiomqtt.__aenter__()

                LOGGER.info("MQTT: Client Connected")

                # Subscribe to panel internal database updates
                await self.aiomqtt.subscribe("iq2meid")

                # Subscribte to MQTT private response
                await self.aiomqtt.subscribe("response_" + self._controller.settings.random_mac, qos=self._controller.settings.mqtt_qos)

                # Subscribe to Z-Wave response
                await self.aiomqtt.subscribe("ZWAVE_RESPONSE", qos=self._controller.settings.mqtt_qos)

                # Only log all traffic for debug purposes
                if self.log_mqtt_mesages:
                    # Subscribe to MQTT commands send to panel by other devices
                    await self.aiomqtt.subscribe("mastermeid", qos=self._controller.settings.mqtt_qos)

                    # Subscribe to all topics
                    # await self.aiomqtt.subscribe("#", qos=self._controller.settings.mqtt_qos)

                self._task_manager.run(self.mqtt_listen_task(), self._mqtt_task_listen_label)
                self._task_manager.run(self.mqtt_ping_task(), self._mqtt_task_ping_label)

                response_connect = await self.command_connect()
                self._controller.panel.imei = response_connect.get("master_imei", "")
                self._controller.panel.product_type = response_connect.get("primary_product_type", "")

                await self.command_pingevent()
                await self.command_pair_status_request()

                response_database = await self.command_sync_database()
                LOGGER.debug("MQTT: Updating State from syncdatabase")
                self._controller.panel.load_database(response_database.get("fulldbdata"))
                self._controller.panel.dump()
                self._controller.state.dump()

                self.connected = True
                self.connected_observer.notify()

                if not run_forever:
                    self.connected = False
                    self.connected_observer.notify()
                    self._task_manager.cancel(self._mqtt_task_listen_label)
                    self._task_manager.cancel(self._mqtt_task_ping_label)
                    await self.aiomqtt.__aexit__(None,None,None)

                break

            except aiomqtt.MqttError as err:
                # Receive pannel network error
                self.connected = False
                self.connected_observer.notify()
                self.aiomqtt = None

                if reconnect:
                    LOGGER.debug("MQTT Error - %s: Connect - Reconnecting in %s seconds ...", err, self._controller.settings.mqtt_timeout)
                    await asyncio.sleep(self._controller.settings.mqtt_timeout)
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

            await asyncio.sleep(self._controller.settings.mqtt_ping)

    async def mqtt_listen_task(self) -> None:
        try:
            async for message in self.aiomqtt.messages:

                if self.log_mqtt_mesages:
                    LOGGER.debug("MQTT TOPIC: %s\n%s", message.topic, message.payload.decode())

                # Panel response to MQTT Commands
                if message.topic.matches("response_" + self._controller.settings.random_mac):
                    data = message.payload.decode()
                    data = json.loads(data)
                    await self._mqtt_command_queue.handle_response(data)

                # Panel updates to IQ2MEID database
                if message.topic.matches("iq2meid"):
                    data = json.loads(message.payload.decode())
                    self._controller.panel.parse_iq2meid_message(data)

                # Panel Z-Wave response
                if message.topic.matches("ZWAVE_RESPONSE"):
                    data = json.loads(message.payload.decode())
                    zwave = data.get("ZWAVE_RESPONSE","")
                    decoded_payload = base64.b64decode(zwave.get("ZWAVE_PAYLOAD","")).hex()
                    LOGGER.debug("Z-Wave Response: Node(%s) - Status(%s) - Payload(%s)",zwave.get("NODE_ID",""),zwave.get("ZWAVE_COMMAND_STATUS",""),decoded_payload)

        except aiomqtt.MqttError as err:
            self.connected = False
            self.connected_observer.notify()

            LOGGER.debug("%s: Listen - Reconnecting in %s seconds ...", err, self._controller.settings.mqtt_timeout)
            await asyncio.sleep(self._controller.settings.mqtt_timeout)
            self._task_manager.run(self.mqtt_connect_task(reconnect=True, run_forever=True), self._mqtt_task_connect_label)

    async def start_initial_pairing(self) -> bool:
        # check if random_mac exist
        if self._controller.settings.random_mac == "":
            LOGGER.debug("Creating random_mac")
            self._controller.settings.random_mac = generate_random_mac()
            self._pki.create(self._controller.settings.random_mac, key_size=self._controller.settings.key_size)

        # Check if PKI is valid
        self._pki.set_id(self._controller.settings.random_mac)
        LOGGER.debug("Checking PKI")
        if not (
            self._pki.check_key_file() and
            self._pki.check_cer_file() and
            self._pki.check_csr_file()
        ):
            LOGGER.error("PKI Error")
            return False

        LOGGER.debug("Starting Pairing Process")

        if not self._controller.settings.check_plugin_ip():
            LOGGER.error("Plugin IP Address not configured")
            return False

        # If we dont allready have client signed certificate, start the pairing server
        if not self._pki.check_secure_file() or not self._pki.check_qolsys_cer_file() or not self._controller.settings.check_panel_ip():

            # High Level Random Pairing Port
            pairing_port = random.randint(50000, 55000)

            # Start Pairing mDNS Brodcast
            LOGGER.debug("Starting mDNS Service Discovery: %s:%s", self._controller.settings.plugin_ip, str(pairing_port))
            mdns_server = QolsysMDNS(self._controller.settings.plugin_ip, pairing_port)
            await mdns_server.start_mdns()

            # Start Key Exchange Server
            LOGGER.debug("Starting Certificate Exchange Server")
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=self._pki.cer_file_path, keyfile=self._pki.key_file_path)
            self.certificate_exchange_server = await asyncio.start_server(self.handle_key_exchange_client,
                                                                          self._controller.settings.plugin_ip, pairing_port, ssl=context)
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
                if (not received_panel_mac and not received_signed_client_certificate and not received_qolsys_cer):

                    request = (await reader.read(2048))
                    mac = request.decode()

                    address, port = writer.get_extra_info("peername")
                    LOGGER.debug("Panel Connected from: %s:%s", address, port)
                    LOGGER.debug("Receiving from Panel: %s", mac)

                    # Remove \x00 and \x01 from received string
                    self._controller.settings.panel_mac = "".join(char for char in mac if char.isprintable())
                    self._controller.settings.panel_ip = address
                    received_panel_mac = True

                    # Sending random_mac to panel
                    message = b"\x00\x11" + self._controller.settings.random_mac.encode()
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
                if (received_panel_mac and not received_signed_client_certificate and not received_qolsys_cer):
                    request = await reader.readuntil(b"sent")
                    if request.endswith(b"sent"):
                        request = request[:-4]

                    LOGGER.debug("Saving [Signed Client Certificate]")
                    async with aiofiles.open(self._pki.secure_file_path, mode="wb") as f:
                        await f.write(request)
                        received_signed_client_certificate = True

                # Read qolsys certificate data
                if (received_panel_mac and received_signed_client_certificate and not received_qolsys_cer):
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
            self.certificate_exchange_server.close()

    async def send_command(self, topic: str, json_payload: str, request_id: str) -> dict:
        if self.aiomqtt is None:
            LOGGER.error("MQTT Client not configured")
            raise QolsysMqttError

        await self.aiomqtt.publish(topic=topic, payload=json.dumps(json_payload), qos=self._controller.settings.mqtt_qos)
        return await self._mqtt_command_queue.wait_for_response(request_id)

    async def command_connect(self) -> dict:
        LOGGER.debug("MQTT: Sending connect command")

        topic = "mastermeid"
        ipAddress = self._controller.settings.plugin_ip
        eventName = "connect_v204"
        macAddress = self._controller.settings.random_mac
        remoteClientID = self._controller.settings.mqtt_remote_client_id
        softwareVersion = "4.4.1"
        producType = "tab07_rk68"
        bssid = ""
        lastUpdateChecksum = "2132501716"
        dealerIconsCheckSum = ""
        remote_feature_support_version = "1"
        current_battery_status = "Normal"
        remote_panel_battery_status = 3
        remote_panel_battery_health = 2
        remote_panel_battery_level = 100
        remote_panel_battery_present = True
        remote_panel_battery_percentage = 100
        remote_panel_battery_scale = 100
        remote_panel_battery_voltage = 4082
        remote_panel_battery_technology = ""
        remote_panel_plugged = 1
        remote_panel_battery_temperature = 430
        requestID = str(uuid.uuid4())
        responseTopic = "response_" + self._controller.settings.random_mac
        remoteMacAddress = self._controller.settings.random_mac

        dhcpInfo = {
            "ipaddress": "",
            "gateway": "",
            "netmask": "",
            "dns1": "",
            "dns2": "",
            "dhcpServer": "",
            "leaseDuration": "",
        }

        payload = {
            "eventName": eventName,
            "pairing_request": True,
            "ipAddress": ipAddress,
            "macAddress": macAddress,
            "remoteClientID": remoteClientID,
            "softwareVersion": softwareVersion,
            "productType": producType,
            "bssid": bssid,
            "dhcpInfo": json.dumps(dhcpInfo),
            "lastUpdateChecksum": lastUpdateChecksum,
            "dealerIconsCheckSum": dealerIconsCheckSum,
            "remote_feature_support_version": remote_feature_support_version,
            "current_battery_status": current_battery_status,
            "remote_panel_battery_status": remote_panel_battery_status,
            "remote_panel_battery_health": remote_panel_battery_health,
            "remote_panel_battery_level": remote_panel_battery_level,
            "remote_panel_battery_present": remote_panel_battery_present,
            "remote_panel_battery_percentage": remote_panel_battery_percentage,
            "remote_panel_battery_scale": remote_panel_battery_scale,
            "remote_panel_battery_voltage": remote_panel_battery_voltage,
            "remote_panel_battery_technology": remote_panel_battery_technology,
            "remote_panel_plugged": remote_panel_plugged,
            "remote_panel_battery_temperature": remote_panel_battery_temperature,
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddess": remoteMacAddress,
        }

        response = await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT: Receiving connect command")
        return response

    async def command_pingevent(self) -> None:
        LOGGER.debug("MQTT: Sending pingevent command")

        topic = "mastermeid"
        eventName = "pingevent"
        macAddress = self._controller.settings.random_mac
        remote_panel_status = "Active"
        ipAddress = self._controller.settings.plugin_ip
        current_battery_status = "Normal"
        remote_panel_battery_percentage = 100
        remote_panel_battery_temperature = 430
        remote_panel_battery_status = 3
        remote_panel_battery_scale = 100
        remote_panel_battery_voltage = 4102
        remote_panel_battery_present = True
        remote_panel_battery_technology = ""
        remote_panel_battery_level = 100
        remote_panel_battery_health = 2
        remote_panel_plugged = 1
        requestID = str(uuid.uuid4())
        remoteMacAddress = self._controller.settings.random_mac
        responseTopic = "response_" + self._controller.settings.random_mac

        payload = {
            "eventName": eventName,
            "macAddress": macAddress,
            "remote_panel_status": remote_panel_status,
            "ipAddress": ipAddress,
            "current_battery_status": current_battery_status,
            "remote_panel_battery_percentage": remote_panel_battery_percentage,
            "remote_panel_battery_temperature": remote_panel_battery_temperature,
            "remote_panel_battery_status": remote_panel_battery_status,
            "remote_panel_battery_scale": remote_panel_battery_scale,
            "remote_panel_battery_voltage": remote_panel_battery_voltage,
            "remote_panel_battery_present": remote_panel_battery_present,
            "remote_panel_battery_technology": remote_panel_battery_technology,
            "remote_panel_battery_level": remote_panel_battery_level,
            "remote_panel_battery_health": remote_panel_battery_health,
            "remote_panel_plugged": remote_panel_plugged,
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddess": remoteMacAddress,
        }

        await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT: Receiving pingevent command")

    async def command_timesync(self) -> None:
        LOGGER.debug("MQTT: Sending timeSync command")

        topic = "mastermeid"
        eventName = "timeSync"
        startTimestamp = datetime.datetime.now().timestamp()
        requestID = str(uuid.uuid4())
        responseTopic = "response_" + self._controller.settings.random_mac
        remoteMacAddress = self._controller.settings.random_mac

        payload = {
            "eventName": eventName,
            "startTimestamp": startTimestamp,
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddess": remoteMacAddress,
        }

        await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT: Receiving timeSync command")

    async def command_sync_database(self) -> dict:
        LOGGER.debug("MQTT: Sending syncdatabase command")

        topic = "mastermeid"
        eventName = "syncdatabase"
        requestID = str(uuid.uuid4())
        responseTopic = "response_" + self._controller.settings.random_mac
        remoteMacAddress = self._controller.settings.random_mac

        payload = {
            "eventName": eventName,
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddess": remoteMacAddress,
        }

        response = await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT: Receiving syncdatabase command")
        return response

    async def command_acstatus(self) -> None:
        LOGGER.debug("MQTT: Sending acStatus command")

        topic = "mastermeid"
        eventName = "acStatus"
        requestID = str(uuid.uuid4())
        responseTopic = "response_" + self._controller.settings.random_mac
        remoteMacAddress = self._controller.settings.random_mac
        acStatus = "Connected"

        payload = {"eventName": eventName,
                   "acStatus": acStatus,
                   "requestID": requestID,
                   "responseTopic": responseTopic,
                   "remoteMacAddess": remoteMacAddress}

        await self.send_command(topic, payload, requestID)

    async def command_dealer_logo(self) -> None:
        LOGGER.debug("MQTT: Sending dealerLogo command")

        topic = "mastermeid"
        eventName = "dealerLogo"
        requestID = str(uuid.uuid4())
        responseTopic = "response_" + self._controller.settings.random_mac
        remoteMacAddress = self._controller.settings.random_mac

        payload = {
            "eventName": eventName,
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddess": remoteMacAddress,
        }

        await self.send_command(topic, payload, requestID)

    async def command_pair_status_request(self) -> None:
        LOGGER.debug("MQTT: Sending pair_status_request command")

        topic = "mastermeid"
        eventName = "pair_status_request"
        remoteMacAddress = self._controller.settings.random_mac
        requestID = str(uuid.uuid4())
        responseTopic = "response_" + self._controller.settings.random_mac

        payload = {
            "eventName": eventName,
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddess": remoteMacAddress,
        }

        await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT: Receiving pair_status_request command")

    async def command_disconnect(self) -> None:
        LOGGER.debug("MQTT: Sending disconnect command")

        topic = "mastermeid"
        eventName = "disconnect"
        remoteClientID = self._controller.settings.mqtt_remote_client_id
        requestID = str(uuid.uuid4())
        remoteMacAddress = self._controller.settings.random_mac

        payload = {
            "eventName": eventName,
            "remoteClientID": remoteClientID,
            "requestID": requestID,
            "remoteMacAddess": remoteMacAddress,
        }

        await self.send_command(topic, payload, requestID)

    async def command_pairing_request(self) -> dict:
        LOGGER.debug("MQTT: Sending pairing_request command")

        topic = "mastermeid"
        eventName = "connect_v204"
        pairing_request = True
        ipAddress = self._controller.settings.plugin_ip
        macAddress = self._controller.settings.random_mac
        remoteClientID = self._controller.settings.mqtt_remote_client_id
        softwareVersion = "4.4.1"
        productType = "tab07_rk68"
        bssid = ""
        lastUpdateChecksum = "2132501716"
        dealerIconsCheckSum = ""
        remote_feature_support_version = "1"
        requestID = str(uuid.uuid4())
        responseTopic = "response_" + self._controller.settings.random_mac
        remoteMacAddress = self._controller.settings.random_mac

        dhcpInfo = {
            "ipaddress": "",
            "gateway": "",
            "netmask": "",
            "dns1": "",
            "dns2": "",
            "dhcpServer": "",
            "leaseDuration": "",
        }

        payload = {
            "eventName": eventName,
            "pairing_request": pairing_request,
            "ipAddress": ipAddress,
            "macAddress": macAddress,
            "remoteClientID": remoteClientID,
            "softwareVersion": softwareVersion,
            "producType": productType,
            "bssid": bssid,
            "dhcpInfo": json.dumps(dhcpInfo),
            "lastUpdateChecksum": lastUpdateChecksum,
            "dealerIconsCheckSum": dealerIconsCheckSum,
            "remote_feature_support_version": remote_feature_support_version,
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddess": remoteMacAddress,
        }

        response = await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT: Receiving pairing_request command")
        return response

    async def command_ui_delay(self, partition_id: str,silent_disarming:bool = False) -> None:
        LOGGER.debug("MQTT: Sending ui_delay command")

        # partition state needs to be sent for ui_delay to work
        partition = self._controller.state.partition(partition_id)

        arming_command = {
            "operation_name": "ui_delay",
            "panel_status": partition.system_status,
            "userID": 0,
            "partitionID": partition_id,  # STR EXPECTED
            "silentDisarming":silent_disarming,
            "operation_source": 1,
            "macAddress": self._controller.settings.random_mac,
        }

        topic = "mastermeid"
        eventName = "ipcCall"
        ipcServiceName = "qinternalservice"
        ipcInterfaceName = "android.os.IQInternalService"
        ipcTransactionID = 7
        requestID = str(uuid.uuid4())
        remoteMacAddress = self._controller.settings.random_mac
        responseTopic = "response_" + self._controller.settings.random_mac

        payload = {
            "eventName": eventName,
            "ipcServiceName": ipcServiceName,
            "ipcInterfaceName": ipcInterfaceName,
            "ipcTransactionID": ipcTransactionID,
            "ipcRequest": [{
                "dataType": "string",
                "dataValue":  json.dumps(arming_command),
            }],
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddress": remoteMacAddress,
        }

        await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT: Receiving ui_delay command")

    async def command_disarm(self, partition_id: str, user_code: str = "", silent_disarming: bool = False) -> bool:
        partition = self._controller.state.partition(partition_id)
        if not partition:
            LOGGER.debug("MQTT: disarm command error - Unknow Partition")
            return False

        # Do local user code verification
        user_id = 1
        if self.check_user_code_on_disarm:
            user_id = self._controller.panel.check_user(user_code)
            if user_id == -1:
                LOGGER.debug("MQTT: disarm command error - user_code error")
                return False

        async def get_mqtt_disarm_command(silent_disarming:bool) -> str:
            if partition.alarm_state == PartitionAlarmState.ALARM:
                return "disarm_from_emergency"
            if partition.system_status in {PartitionSystemStatus.ARM_AWAY_EXIT_DELAY,
                                           PartitionSystemStatus.ARM_STAY_EXIT_DELAY,
                                           PartitionSystemStatus.ARM_NIGHT_EXIT_DELAY}:
                return "disarm_from_openlearn_sensor"
            if partition.system_status in {PartitionSystemStatus.ARM_AWAY,
                                           PartitionSystemStatus.ARM_STAY,
                                           PartitionSystemStatus.ARM_NIGHT}:
                await self.command_ui_delay(partition_id,silent_disarming)
                return "disarm_the_panel_from_entry_delay"

            return "disarm_from_openlearn_sensor"

        mqtt_disarm_command = await get_mqtt_disarm_command(silent_disarming)
        LOGGER.debug("MQTT: Sending disarm command - check_user_code:%s", self.check_user_code_on_disarm)

        disarm_command = {
            "operation_name": mqtt_disarm_command,
            "userID": user_id,
            "partitionID": int(partition_id),  # INT EXPECTED
            "operation_source": 1,
            "macAddress": self._controller.settings.random_mac,
        }

        topic = "mastermeid"
        eventName = "ipcCall"
        ipcServiceName = "qinternalservice"
        ipcInterfaceName = "android.os.IQInternalService"
        ipcTransactionID = 7
        requestID = str(uuid.uuid4())
        remoteMacAddress = self._controller.settings.random_mac
        responseTopic = "response_" + self._controller.settings.random_mac

        payload = {"eventName": eventName,
                   "ipcServiceName": ipcServiceName,
                   "ipcInterfaceName": ipcInterfaceName,
                   "ipcTransactionID": ipcTransactionID,
                   "ipcRequest": [{
                       "dataType": "string",
                       "dataValue":  json.dumps(disarm_command),
                   }],
                   "requestID": requestID,
                   "responseTopic": responseTopic,
                   "remoteMacAddress": remoteMacAddress}

        await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT: Receiving disarm command")

        return True

    async def command_zwave_doorlock_set(self, node_id: int, locked:bool) -> None:
        LOGGER.debug("MQTT: Sending zwave_doorlock_set command: EXPERIMENTAL")
        LOGGER.debug("MQTT: Sending zwave_doorlock_set command - Node(%s) - Locked(%s)",node_id,locked)

        command = 98

        # 0 unlocked
        # 255 locked
        lock_mode = 0
        if locked:
            lock_mode = 255

        ipcRequest = [{
                "dataType": "int",
                "dataValue": node_id,
            },
            {
                "dataType": "int",
                "dataValue": 0,
            },
            {
                "dataType": "byteArray",
                "dataValue": [command,1,lock_mode],
            },
            {
                "dataType": "int",
                "dataValue": 0,
            },
            {
                "dataType": "int",
                "dataValue": 106,
            },
            {
                "dataType": "byteArray",
                "dataValue": [0],
            },
        ]

        topic = "mastermeid"
        eventName = "ipcCall"
        ipcServiceName = "qzwaveservice"
        ipcInterfaceName = "android.os.IQZwaveService"
        ipcTransactionID = 47
        requestID = str(uuid.uuid4())
        remoteMacAddress = self._controller.settings.random_mac
        responseTopic = "response_" + self._controller.settings.random_mac

        payload = {
            "eventName": eventName,
            "ipcServiceName": ipcServiceName,
            "ipcInterfaceName": ipcInterfaceName,
            "ipcTransactionID": ipcTransactionID,
            "ipcRequest": ipcRequest,
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddress": remoteMacAddress,
        }

        await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT: Receiving zwave_doorlock_set command")

    async def command_zwave_thermostat_setpoint_set(self, node_id: int, mode:ThermostatMode, setpoint:float) -> None:
        # Command 67
        LOGGER.debug("MQTT: Sending zwave_thermostat_setpoint_set command: EXPERIMENTAL")
        LOGGER.debug("MQTT: Sending zwave_thermostat_setpoint_set - Node(%s) - Mode(%s) - Setpoint(%s)",node_id,mode,setpoint)
        ipcRequest = [{
                "dataType": "int",
                "dataValue": node_id,
            },
            {
                "dataType": "int",
                "dataValue": 0,
            },
            {
                "dataType": "byteArray",
                "dataValue": [67,1,mode,setpoint],
            },
            {
                "dataType": "int",
                "dataValue": 0,
            },
            {
                "dataType": "int",
                "dataValue": 106,
            },
            {
                "dataType": "byteArray",
                "dataValue": [0],
            },
        ]

        topic = "mastermeid"
        eventName = "ipcCall"
        ipcServiceName = "qzwaveservice"
        ipcInterfaceName = "android.os.IQZwaveService"
        ipcTransactionID = 47
        requestID = str(uuid.uuid4())
        remoteMacAddress = self._controller.settings.random_mac
        responseTopic = "response_" + self._controller.settings.random_mac

        payload = {"eventName": eventName,
                   "ipcServiceName": ipcServiceName,
                   "ipcInterfaceName": ipcInterfaceName,
                   "ipcTransactionID": ipcTransactionID,
                   "ipcRequest": ipcRequest,
                   "requestID": requestID,
                   "responseTopic": responseTopic,
                   "remoteMacAddress": remoteMacAddress}

        await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT: Receiving zwave_thermostat_mode_set command")

    async def command_zwave_thermostat_mode_set(self, node_id: int, mode:ThermostatMode) -> None:
        # Command 64
        LOGGER.debug("MQTT: Sending zwave_thermostat_mode_set command: EXPERIMENTAL")
        LOGGER.debug("MQTT: Sending zwave_thermostat_mode_set command - Node(%s) - Mode(%s)",node_id,mode)
        ipcRequest = [{
                "dataType": "int",
                "dataValue": node_id,
            },
            {
                "dataType": "int",
                "dataValue": 0,
            },
            {
                "dataType": "byteArray",
                "dataValue": [64,1,mode],
            },
            {
                "dataType": "int",
                "dataValue": 0,
            },
            {
                "dataType": "int",
                "dataValue": 106,
            },
            {
                "dataType": "byteArray",
                "dataValue": [0],
            },
        ]

        topic = "mastermeid"
        eventName = "ipcCall"
        ipcServiceName = "qzwaveservice"
        ipcInterfaceName = "android.os.IQZwaveService"
        ipcTransactionID = 47
        requestID = str(uuid.uuid4())
        remoteMacAddress = self._controller.settings.random_mac
        responseTopic = "response_" + self._controller.settings.random_mac

        payload = {
            "eventName": eventName,
            "ipcServiceName": ipcServiceName,
            "ipcInterfaceName": ipcInterfaceName,
            "ipcTransactionID": ipcTransactionID,
            "ipcRequest": ipcRequest,
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddress": remoteMacAddress,
        }

        await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT: Receiving zwave_thermostat_mode_set command")

    async def command_zwave_thermostat_fan_mode_set(self, node_id: int, fan_mode:ThermostatFanMode) -> None:
        # Command 68
        LOGGER.debug("MQTT: Sending zwave_thermostat_fan_mode_set command: EXPERIMENTAL")
        LOGGER.debug("MQTT: Sending zwave_thermostat_fan_mode_set command - Node(%s) - FanMode(%s)",node_id,fan_mode)
        ipcRequest = [{
                "dataType": "int",
                "dataValue": node_id,
            },
            {
                "dataType": "int",
                "dataValue": 0,
            },
            {
                "dataType": "byteArray",
                "dataValue": [68,1,fan_mode],
            },
            {
                "dataType": "int",
                "dataValue": 0,
            },
            {
                "dataType": "int",
                "dataValue": 106,
            },
            {
                "dataType": "byteArray",
                "dataValue": [0],
            },
        ]

        topic = "mastermeid"
        eventName = "ipcCall"
        ipcServiceName = "qzwaveservice"
        ipcInterfaceName = "android.os.IQZwaveService"
        ipcTransactionID = 47
        requestID = str(uuid.uuid4())
        remoteMacAddress = self._controller.settings.random_mac
        responseTopic = "response_" + self._controller.settings.random_mac

        payload = {"eventName": eventName,
                   "ipcServiceName": ipcServiceName,
                   "ipcInterfaceName": ipcInterfaceName,
                   "ipcTransactionID": ipcTransactionID,
                   "ipcRequest": ipcRequest,
                   "requestID": requestID,
                   "responseTopic": responseTopic,
                   "remoteMacAddress": remoteMacAddress}

        await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT: Receiving zwave_thermostat_fan_mode_set command")

    async def command_zwave_switch_multi_level(self, node_id: int, level: int) -> None:
        LOGGER.debug("MQTT: Sending zwave_switch_multi_level command  - Node(%s) - Level(%s)",node_id,level)
        ipcRequest = [{
                "dataType": "int",  # Node ID
                "dataValue": node_id,
            },
            {
                "dataType": "int",  # ?
                "dataValue": 0,
            },
            {
                # [38,1,level] ZWAVE MULTILEVELSWITCH SET (level 255 to set to previous state)
                "dataType": "byteArray",
                "dataValue": [38,1,level],
            },
            {
                "dataType": "int",  # ?
                "dataValue": 0,
            },
            {
                "dataType": "int",  # ?
                "dataValue": 106,
            },
            {
                "dataType": "byteArray",
                "dataValue": [0],
            },
        ]

        topic = "mastermeid"
        eventName = "ipcCall"
        ipcServiceName = "qzwaveservice"
        ipcInterfaceName = "android.os.IQZwaveService"
        ipcTransactionID = 47
        requestID = str(uuid.uuid4())
        remoteMacAddress = self._controller.settings.random_mac
        responseTopic = "response_" + self._controller.settings.random_mac

        payload = {"eventName": eventName,
                   "ipcServiceName": ipcServiceName,
                   "ipcInterfaceName": ipcInterfaceName,
                   "ipcTransactionID": ipcTransactionID,
                   "ipcRequest": ipcRequest,
                   "requestID": requestID,
                   "responseTopic": responseTopic,
                   "remoteMacAddress": remoteMacAddress}

        await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT: Receiving zwave_switch_multi_level command")

    async def command_zwave_switch_binary(self, node_id: int, status:bool) -> None:
        LOGGER.debug("MQTT:Sending zwave_switch_binary command")

        level = 0
        if status:
            level = 99

        ipcRequest = [{
                "dataType": "int",
                "dataValue": node_id,
            },
            {
                "dataType": "int",
                "dataValue": 0,
            },
            {
                "dataType": "byteArray",
                "dataValue": [37,1,level],
            },
            {
                "dataType": "int",
                "dataValue": 0,
            },
            {
                "dataType": "int",
                "dataValue": 106,
            },
            {
                "dataType": "byteArray",
                "dataValue": [0],
            },
        ]

        topic = "mastermeid"
        eventName = "ipcCall"
        ipcServiceName = "qzwaveservice"
        ipcInterfaceName = "android.os.IQZwaveService"
        ipcTransactionID = 47
        requestID = str(uuid.uuid4())
        remoteMacAddress = self._controller.settings.random_mac
        responseTopic = "response_" + self._controller.settings.random_mac

        payload = {"eventName": eventName,
                   "ipcServiceName": ipcServiceName,
                   "ipcInterfaceName": ipcInterfaceName,
                   "ipcTransactionID": ipcTransactionID,
                   "ipcRequest": ipcRequest,
                   "requestID": requestID,
                   "responseTopic": responseTopic,
                   "remoteMacAddress": remoteMacAddress}

        await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT:Receiving zwave_switch_binary command")


    async def command_arm(self, partition_id: str, arming_type: str, user_code: str = "", exit_sounds: bool = False,  # noqa: PLR0913
                          instant_arm: bool = False, entry_delay: bool = True) -> bool:

        LOGGER.debug("MQTT: Sending arm command: partition%s, arming_type:%s, exit_sounds:%s, instant_arm: %s, entry_delay:%s",
                     partition_id, arming_type,exit_sounds,instant_arm,entry_delay)

        user_id = 0

        partition = self._controller.state.partition(partition_id)
        if not partition:
            LOGGER.debug("MQTT: arm command error - Unknow Partition")
            return False

        if self._controller.panel.SECURE_ARMING == "true" and self.check_user_code_on_arm:
            # Do local user code verification to arm if secure arming is enabled
            user_id = self._controller.panel.check_user(user_code)
            if user_id == -1:
                LOGGER.debug("MQTT: arm command error - user_code error")
                return False

        mqtt_arming_type = ""
        match arming_type:
            case "ARM-STAY":
                mqtt_arming_type = "ui_armstay"

            case "ARM-AWAY":
                mqtt_arming_type = "ui_armaway"

            case "ARM-NIGHT":
                mqtt_arming_type = "ui_armnight"

            case _:
                LOGGER.debug("MQTT: Sending arm command: Unknow arming_type:%s", arming_type)
                return False

        exitSoundValue = "ON"
        if not exit_sounds:
            exitSoundValue = "OFF"

        entryDelay = "ON"
        if not entry_delay:
            entryDelay = "OFF"

        arming_command = {
            "operation_name": mqtt_arming_type,
            "bypass_zoneid_set": "[]",
            "userID": user_id,
            "partitionID": int(partition_id),
            "exitSoundValue":  exitSoundValue,
            "entryDelayValue": entryDelay,
            "multiplePartitionsSelected": False,
            "instant_arming": instant_arm,
            "final_exit_arming_selected": False,
            "manually_selected_zones": "[]",
            "operation_source": 1,
            "macAddress": self._controller.settings.random_mac,
        }

        topic = "mastermeid"
        eventName = "ipcCall"
        ipcServiceName = "qinternalservice"
        ipcInterfaceName = "android.os.IQInternalService"
        ipcTransactionID = 7
        requestID = str(uuid.uuid4())
        remoteMacAddress = self._controller.settings.random_mac
        responseTopic = "response_" + self._controller.settings.random_mac

        payload = {
            "eventName": eventName,
            "ipcServiceName": ipcServiceName,
            "ipcInterfaceName": ipcInterfaceName,
            "ipcTransactionID": ipcTransactionID,
            "ipcRequest": [{
                "dataType": "string",
                "dataValue":  json.dumps(arming_command),
            }],
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddress": remoteMacAddress,
        }

        await self.send_command(topic, payload, requestID)

        return True

    async def command_execute_scene(self,scene_id:str) -> bool:
        LOGGER.debug("MQTT: Sending execute_scene command")

        scene = self._controller.state.scene(scene_id)
        if not scene:
            LOGGER.debug("MQTT: command_execute_scene Erro - Unknow Scene: %s", scene_id)
            return False

        scene_command = {
            "operation_name": "execute_scene",
            "scene_id": scene.scene_id,
            "operation_source": 1,
            "macAddress": self._controller.settings.random_mac,
        }

        topic = "mastermeid"
        eventName = "ipcCall"
        ipcServiceName = "qinternalservice"
        ipcInterfaceName = "android.os.IQInternalService"
        ipcTransactionID = 7
        requestID = str(uuid.uuid4())
        remoteMacAddress = self._controller.settings.random_mac
        responseTopic = "response_" + self._controller.settings.random_mac

        payload = {
            "eventName": eventName,
            "ipcServiceName": ipcServiceName,
            "ipcInterfaceName": ipcInterfaceName,
            "ipcTransactionID": ipcTransactionID,
            "ipcRequest": [{
                "dataType": "string",
                "dataValue":  json.dumps(scene_command),
            }],
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddress": remoteMacAddress,
        }

        await self.send_command(topic, payload, requestID)
        LOGGER.debug("MQTT: Receiving execute_scene command")

        return False
