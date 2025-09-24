import asyncio
import datetime
import json
import logging
import random
import ssl
import uuid

import aiomqtt

from .enum import PartitionAlarmState, PartitionSystemStatus
from .errors import QolsysMqttError, QolsysSslError
from .mdns import QolsysMDNS
from .mqtt_command_queue import QolsysMqttCommandQueue
from .panel import QolsysPanel
from .pki import QolsysPKI
from .plugin import QolsysPlugin
from .settings import QolsysSettings
from .state import QolsysState
from .task_manager import QolsysTaskManager
from .utils_mqtt import fix_json_string, generate_random_mac

LOGGER = logging.getLogger(__name__)

class QolsysPluginRemote(QolsysPlugin):

    def __init__(self,state:QolsysState,panel:QolsysPanel,settings:QolsysSettings,config_directory:str)-> None:
        super().__init__(state,panel,settings)

        # PKI
        self._pki = QolsysPKI(keys_directory = config_directory + "pki/")
        self._auto_discover_pki = True

        # Plugin
        self.certificate_exchange_server = None
        self._check_user_code_on_disarm = True
        self._log_mqtt_messages = False
        self._task_manager = QolsysTaskManager()
        self._mqtt_command_queue = QolsysMqttCommandQueue()

        # MQTT Client
        self.aiomqtt = None
        self._mqtt_timeout = 30
        self._mqtt_ping = 600
        self._mqtt_task_config_label = "mqtt_task_config"
        self._mqtt_task_listen_label = "mqtt_task_listen"
        self._mqtt_task_connect_label = "mqtt_task_connect"
        self._mqtt_task_ping_label = "mqtt_task_ping"

    @property
    def log_mqtt_mesages(self) -> bool:
        return self._log_mqtt_messages

    @log_mqtt_mesages.setter
    def log_mqtt_mesages(self,log_mqtt_mesages:bool) -> None:
        self._log_mqtt_messages = log_mqtt_mesages

    @property
    def check_user_code_on_disarm(self) -> bool:
        return self._check_user_code_on_disarm

    @check_user_code_on_disarm.setter
    def check_user_code_on_disarm(self,check_user_code_on_disarm:bool) -> None:
        self._check_user_code_on_disarm = check_user_code_on_disarm

    @property
    def auto_discover_pki(self) -> bool:
        return self._auto_discover_pki

    @auto_discover_pki.setter
    def auto_discover_pki(self,value:bool) -> None:
        self._auto_discover_pki = value

    def is_paired(self) -> bool:
        # Check if plugin is paired:
        # 1- random_mac set
        # 2- KEY file present
        # 3- Signed certificate file present
        # 4- Qolsys certificate present
        # 5- Qolsys Panel IP present
        return (self._pki.id != "" and
            self._pki.check_key_file() and
            self._pki.check_secure_file() and
            self._pki.check_qolsys_cer_file() and
            self.settings.check_panel_ip() and
            self.settings.check_plugin_ip())

    async def config(self,start_pairing:bool) -> bool:
        return await self._task_manager.run(self.config_task(start_pairing), self._mqtt_task_config_label)

    async def config_task(self,start_pairing:bool) -> bool:
        LOGGER.debug("Configuring Plugin")
        super().config()

        # Read user file for access code
        loop = asyncio.get_running_loop()
        if not loop.run_in_executor(None,self.panel.read_users_file):
            return False

        if self._auto_discover_pki:
            if self._pki.auto_discover_pki():
                self.settings.random_mac = self._pki.formatted_id()
        else:
            self._pki.set_id(self.settings.random_mac)

        # Check if plugin is paired
        if self.is_paired():
            LOGGER.debug("Panel is paired")

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
        await self._task_manager.run(self.mqtt_connect_task(reconnect=True),self._mqtt_task_connect_label)

    async def mqtt_connect_task(self,reconnect:bool) -> None:
        if not self.is_paired():
            return

        tls_params = aiomqtt.TLSParameters(
            ca_certs = self._pki.qolsys_cer_file_path,
            certfile = self._pki.secure_file_path,
            keyfile = self._pki.key_file_path,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
            ciphers="ALL:@SECLEVEL=0",
        )

        LOGGER.debug("MQTT: Connecting ...")

        while True:
            try:
                self.aiomqtt = aiomqtt.Client(
                    hostname=self.settings.panel_ip,
                    port=8883,
                    tls_params=tls_params,
                    tls_insecure=True,
                    clean_session=True,
                    timeout=self._mqtt_timeout,
                    identifier="QolsysController")

                await self.aiomqtt.__aenter__()

                LOGGER.debug("MQTT: Client Connected")

                # Subscribe to panel internal databse updates
                await self.aiomqtt.subscribe("iq2meid")

                # Subscribte to MQTT commands response
                await self.aiomqtt.subscribe("response_" + self.settings.random_mac,qos=2)

                # Only log mastermeid traffic for debug purposes
                if self.log_mqtt_mesages:
                    # Subscribe to MQTT commands send to panel by other devices
                    await self.aiomqtt.subscribe("mastermeid",qos=2)

                    # Subscribe to all topics
                    await self.aiomqtt.subscribe("#",qos=2)

                # Start mqtt_listent_task and mqtt_ping_task
                self._task_manager.cancel(self._mqtt_task_listen_label)
                self._task_manager.cancel(self._mqtt_task_ping_label)
                self._task_manager.run(self.mqtt_listen_task(), self._mqtt_task_listen_label)
                self._task_manager.run(self.mqtt_ping_task(),self._mqtt_task_ping_label)

                response_connect = await self.command_connect()
                self.panel.imei = response_connect.get("master_imei","")
                self.panel.product_type = response_connect.get("primary_product_type","")

                await self.command_pairing_request()
                await self.command_pingevent()
                await self.command_timesync()
                await self.command_pair_status_request()

                response_database = await self.command_sync_database()
                LOGGER.debug("MQTT: Updating State from syncdatabase")
                self.panel.load_database(response_database.get("fulldbdata"))
                self.panel.dump()
                self.state.dump()

                self.connected = True
                self.connected_observer.notify()
                break

            except aiomqtt.MqttError as err:
                # Receive pannel network error
                self.connected = False
                self.connected_observer.notify()
                await self.aiomqtt.__aexit__(None,None,None)
                self.aiomqtt = None

                if reconnect:
                    LOGGER.debug("MQTT Error - %s: Reconnecting in %s seconds ...",err,self._mqtt_timeout)
                    await asyncio.sleep(self._mqtt_timeout)
                else:
                    raise QolsysMqttError from err

            except ssl.SSLError as err:
                # SSL error is and authentication error with invalid certificates en pki
                # We cannot recover from this error automaticly
                # Pannels need to be re-paired
                self.connected = False
                self.connected_observer.notify()
                await self.aiomqtt.__aexit__(None,None,None)
                self.aiomqtt = None
                raise QolsysSslError from err

    async def mqtt_ping_task(self) -> None:
        while True:
            if self.aiomqtt is not None and self.connected:
                await self.command_pingevent()
            await asyncio.sleep(self._mqtt_ping)

    async def mqtt_listen_task(self) -> None:
        try:
            async for message in self.aiomqtt.messages:

                if self.log_mqtt_mesages:
                    LOGGER.debug("MQTT TOPIC: %s\n%s",message.topic,message.payload.decode())

                # Panel response to MQTT Commands
                if message.topic.matches("response_" + self.settings.random_mac):
                    data = message.payload.decode()
                    #data = message.payload.decode().replace("\\\\", "\\")  # noqa: ERA001
                    #data = fix_json_string(data)  # noqa: ERA001
                    data = json.loads(data)
                    await self._mqtt_command_queue.handle_response(data)

                # Panel updates to IQ2MEID database
                if message.topic.matches("iq2meid"):
                    data = json.loads(message.payload.decode())
                    self.panel.parse_iq2meid_message(data)

        except aiomqtt.MqttError as err:
            self.connected = False
            self.connected_observer.notify()

            LOGGER.debug("%s: Reconnecting in %s seconds ...",err,self._mqtt_timeout)
            await asyncio.sleep(self._mqtt_timeout)
            self._task_manager.run(self.mqtt_connect_task(reconnect=True),self._mqtt_task_connect_label)

        except ssl.SSLError as err:
            # SSL error is and authentication error with invalid certificates en pki
            # We cannot recover from this error automaticly
            # Pannels need to be re-paired
            self.connected = False
            self.connected_observer.notify()
            await self.aiomqtt.__aexit__(None,None,None)
            self.aiomqtt = None
            raise QolsysSslError from err

    async def start_initial_pairing(self)->bool:
        # check if random_mac exist
        if self.settings.random_mac == "":
            LOGGER.debug("Creating random_mac")
            self.settings.random_mac = generate_random_mac()
            self._pki.create(self.settings.random_mac,key_size=2048)

        # Check if PKI is valid
        self._pki.set_id(self.settings.random_mac)
        LOGGER.debug("Checking PKI")
        if not(self._pki.check_key_file() and
               self._pki.check_cer_file() and
               self._pki.check_csr_file()):
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
            LOGGER.debug("Starting mDNS Service Discovery: %s:%s",self.settings.plugin_ip,str(pairing_port))
            mdns_server = QolsysMDNS(self.settings.plugin_ip,pairing_port)
            await mdns_server.start_mdns()

            # Start Key Exchange Server
            LOGGER.debug("Starting Certificate Exchange Server")
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile = self._pki.cer_file_path, keyfile = self._pki.key_file_path)
            self.certificate_exchange_server = await asyncio.start_server(self.handle_key_exchange_client,self.settings.plugin_ip, pairing_port,ssl=context)

            LOGGER.debug("Certificate Exchange Server Waiting for Panel")
            LOGGER.debug("Press Pair Button in IQ Remote Config Page ...")

            async with self.certificate_exchange_server:
                try:
                    await self.certificate_exchange_server.serve_forever()

                except asyncio.CancelledError:
                    LOGGER.debug("Stoping Certificate Exchange Server")
                    LOGGER.debug("Stoping mDNS Service Discovery")
                    await mdns_server.stop_mdns()

        LOGGER.debug("Sending MQTT Pairing Request to Panel")

        # We have client sgined certificate at this point
        # Connect to Panel MQTT to send pairing command
        await self._task_manager.run(self.mqtt_connect_task(reconnect=False),self._mqtt_task_connect_label)
        LOGGER.debug("Plugin Pairing Completed ")
        return True

    async def handle_key_exchange_client(self,reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:  # noqa: PLR0915

        received_panel_mac = False
        received_signed_client_certificate = False
        received_qolsys_cer = False

        signed_certificate_data = ""
        qolsys_certificate_data = ""

        try:
            continue_pairing = True
            while continue_pairing:

                # Plugin is receiving panel_mac from panel
                if(not received_panel_mac and
                   not received_signed_client_certificate and
                   not received_qolsys_cer):

                    request = (await reader.read(2048))
                    mac = request.decode()

                    address, port = writer.get_extra_info("peername")
                    LOGGER.debug("Panel Connected from: %s:%s",address,port)
                    LOGGER.debug("Receiving from Panel: %s",mac)

                    # Remove \x00 and \x01 from received string
                    self.settings.panel_mac = "".join(char for char in mac if char.isprintable())
                    self.settings.panel_ip = address
                    received_panel_mac = True

                    # Sending random_mac to panel
                    message = b"\x00\x11" + self.settings.random_mac.encode()
                    LOGGER.debug("Sending to Panel: %s",message.decode())
                    writer.write(message)
                    await writer.drain()

                    #Sending CSR File to panel
                    with open(self._pki.csr_file_path, "rb") as file:
                        content = file.read()
                        LOGGER.debug("Sending to Panel: [CSR File Content]")
                        writer.write(content)
                        writer.write(b"sent")
                        await writer.drain()

                    continue

                # Read signed certificate data
                if(received_panel_mac and
                   not received_signed_client_certificate and
                   not received_qolsys_cer):

                    request = (await reader.readline())
                    signed_certificate_data += request.decode()

                    if "sent" in request.decode():
                        certificates = [item for item in signed_certificate_data.split("sent") if item]
                        LOGGER.debug("Saving [Signed Client Certificate]")
                        with open(self._pki.secure_file_path, "wb") as f:
                            f.write(certificates[0].encode())
                            received_signed_client_certificate = True

                        if len(certificates) > 1:
                            qolsys_certificate_data += certificates[1]

                # Read qolsys certificate data
                if(received_panel_mac and
                   received_signed_client_certificate and
                   not received_qolsys_cer):

                    request = (await reader.readline())
                    qolsys_certificate_data += request.decode()

                    if "sent" in request.decode():
                        continue_pairing = False
                        certificates = [item for item in qolsys_certificate_data.split("sent") if item]

                        LOGGER.debug("Saving [Qolsys Certificate]")
                        with open(self._pki.qolsys_cer_file_path, "w") as f:
                            f.write(certificates[0])
                            received_qolsys_cer = True
                            continue_pairing = False
                            writer.close()

                    continue

        except asyncio.CancelledError:
            LOGGER.exception("Key Exchange Server asyncio CancelledError")

        except Exception:
            LOGGER.exception("Key Exchange Server error")

        finally:
            writer.close()
            self.certificate_exchange_server.close()

    async def send_command(self,topic:str,json_payload:str,request_id:str) -> dict:
        if self.aiomqtt is None:
            LOGGER.error("MQTT Client not configured")
            raise QolsysMqttError

        await self.aiomqtt.publish(topic=topic,payload=json.dumps(json_payload),qos=2)
        return await self._mqtt_command_queue.wait_for_response(request_id)

    async def command_connect(self) -> dict:
        LOGGER.debug("MQTT: Sending connect command")

        topic = "mastermeid"
        ipAddress = self.settings.plugin_ip
        eventName = "connect_v204"
        macAddress = self.settings.random_mac
        remoteClientID = "QolsysController"
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
        responseTopic = "response_" + self.settings.random_mac
        remoteMacAddress = self.settings.random_mac

        dhcpInfo = {
            "ipaddress":"",
            "gateway":"",
            "netmask":"",
            "dns1":"",
            "dns2":"",
            "dhcpServer":"",
            "leaseDuration":"",
        }

        payload = { "eventName":eventName,
                    "ipAddress":ipAddress,
                    "macAddress":macAddress,
                    "remoteClientID": remoteClientID,
                    "softwareVersion":softwareVersion,
                    "producType": producType,
                    "bssid": bssid,
                    "dhcpInfo": json.dumps(dhcpInfo),
                    "lastUpdateChecksum":lastUpdateChecksum,
                    "dealerIconsCheckSum" : dealerIconsCheckSum,
                    "remote_feature_support_version":remote_feature_support_version,
                    "current_battery_status": current_battery_status,
                    "remote_panel_battery_status":remote_panel_battery_status,
                    "remote_panel_battery_health": remote_panel_battery_health,
                    "remote_panel_battery_level": remote_panel_battery_level,
                    "remote_panel_battery_present": remote_panel_battery_present,
                    "remote_panel_battery_percentage": remote_panel_battery_percentage,
                    "remote_panel_battery_scale": remote_panel_battery_scale,
                    "remote_panel_battery_voltage": remote_panel_battery_voltage,
                    "remote_panel_battery_technology": remote_panel_battery_technology,
                    "remote_panel_plugged": remote_panel_plugged,
                    "remote_panel_battery_temperature" : remote_panel_battery_temperature,
                    "requestID":requestID,
                    "responseTopic":responseTopic ,
                    "remoteMacAddess":remoteMacAddress,
            }

        response = await self.send_command(topic,payload,requestID)
        LOGGER.debug("MQTT: Receiving connect command")
        return response

    async def command_pingevent(self) -> None:
        LOGGER.debug("MQTT: Sending pingevent command")

        topic = "mastermeid"
        eventName = "pingevent"
        macAddress = self.settings.random_mac
        remote_panel_status = "Active"
        ipAddress = self.settings.plugin_ip
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
        remoteMacAddress = self.settings.random_mac
        responseTopic = "response_" + self.settings.random_mac

        payload = {"eventName":eventName,
                    "macAddress": macAddress,
                    "remote_panel_status": remote_panel_status,
                    "ipAddress": ipAddress,
                    "current_battery_status" : current_battery_status,
                    "remote_panel_battery_percentage":remote_panel_battery_percentage,
                    "remote_panel_battery_temperature" : remote_panel_battery_temperature,
                    "remote_panel_battery_status" : remote_panel_battery_status,
                    "remote_panel_battery_scale": remote_panel_battery_scale,
                    "remote_panel_battery_voltage" : remote_panel_battery_voltage,
                    "remote_panel_battery_present" : remote_panel_battery_present,
                    "remote_panel_battery_technology": remote_panel_battery_technology,
                    "remote_panel_battery_level": remote_panel_battery_level,
                    "remote_panel_battery_health" : remote_panel_battery_health,
                    "remote_panel_plugged" : remote_panel_plugged,
                    "requestID":requestID,
                    "responseTopic": responseTopic,
                    "remoteMacAddess":remoteMacAddress,
        }

        await self.send_command(topic,payload,requestID)
        LOGGER.debug("MQTT: Receiving pingevent command")


    async def command_timesync(self) -> None:
        LOGGER.debug("MQTT: Sending timeSync command")

        topic = "mastermeid"
        eventName = "timeSync"
        startTimestamp = datetime.datetime.now().timestamp()
        requestID = str(uuid.uuid4())
        responseTopic = "response_" + self.settings.random_mac
        remoteMacAddress = self.settings.random_mac

        payload = {"eventName":eventName,
                   "startTimestamp": startTimestamp,
                   "requestID":requestID,
                   "responseTopic":responseTopic,
                   "remoteMacAddess":remoteMacAddress,
        }

        await self.send_command(topic,payload,requestID)
        LOGGER.debug("MQTT: Receiving timeSync command")

    async def command_sync_database(self) -> dict:
        LOGGER.debug("MQTT: Sending syncdatabase command")

        topic = "mastermeid"
        eventName = "syncdatabase"
        requestID = str(uuid.uuid4())
        responseTopic = "response_" + self.settings.random_mac
        remoteMacAddress = self.settings.random_mac

        payload = {
            "eventName": eventName,
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddess": remoteMacAddress,
        }

        response = await self.send_command(topic,payload,requestID)
        LOGGER.debug("MQTT: Receiving syncdatabase command")
        return response

    async def command_acstatus(self) -> None:
        LOGGER.debug("MQTT: Sending acStatus command")

        topic = "mastermeid"
        eventName = "acStatus"
        requestID = str(uuid.uuid4())
        responseTopic = "response_" + self.settings.random_mac
        remoteMacAddress = self.settings.random_mac
        acStatus = "Connected"

        payload = {"eventName":eventName,
                   "acStatus" : acStatus,
                   "requestID":requestID,
                   "responseTopic":responseTopic,
                   "remoteMacAddess":remoteMacAddress}

        await self.send_command(topic,payload,requestID)

    async def command_dealer_logo(self) -> None:
        LOGGER.debug("MQTT: Sending dealerLogo command")

        topic = "mastermeid"
        eventName = "dealerLogo"
        requestID = str(uuid.uuid4())
        responseTopic = "response_" + self.settings.random_mac
        remoteMacAddress = self.settings.random_mac

        payload = {
            "eventName":eventName,
            "requestID":requestID,
            "responseTopic":responseTopic,
            "remoteMacAddess":remoteMacAddress,
        }

        await self.send_command(topic,payload,requestID)

    async def command_pair_status_request(self) -> None:
        LOGGER.debug("MQTT: Sending pair_status_request command")

        topic = "mastermeid"
        eventName = "pair_status_request"
        remoteMacAddress = self.settings.random_mac
        requestID = str(uuid.uuid4())
        responseTopic = "response_" + self.settings.random_mac

        payload = {
            "eventName":eventName,
            "requestID":requestID,
            "responseTopic":responseTopic,
            "remoteMacAddess":remoteMacAddress,
        }

        await self.send_command(topic,payload,requestID)
        LOGGER.debug("MQTT: Receiving pair_status_request command")

    async def command_disconnect(self) -> None:
        LOGGER.debug("MQTT: Sending disconnect command")

        topic = "mastermeid"
        eventName = "disconnect"
        remoteClientID = "QolsysRemote"
        requestID = str(uuid.uuid4())
        remoteMacAddress = self.settings.random_mac

        payload = {
            "eventName":eventName,
            "remoteClientID": remoteClientID,
            "requestID":requestID,
            "remoteMacAddess":remoteMacAddress,
        }

        await self.send_command(topic,payload,requestID)

    async def command_pairing_request(self) -> dict:
        LOGGER.debug("MQTT: Sending pairing_request command")

        topic = "mastermeid"
        eventName = "connect_v204"
        pairing_request = True
        ipAddress = self.settings.plugin_ip
        macAddress = self.settings.random_mac
        remoteClientID = "QolsysController"
        softwareVersion = "4.4.1"
        producType = "tab07_rk68"
        bssid = ""
        lastUpdateChecksum = "2132501716"
        dealerIconsCheckSum = ""
        remote_feature_support_version = "1"
        requestID = str(uuid.uuid4())
        responseTopic = "response_" + self.settings.random_mac
        remoteMacAddress = self.settings.random_mac

        dhcpInfo = {
            "ipaddress":"",
            "gateway":"",
            "netmask":"",
            "dns1":"",
            "dns2":"",
            "dhcpServer":"",
            "leaseDuration":"",
        }

        payload = {
            "eventName": eventName,
            "pairing_request": pairing_request,
            "ipAddress": ipAddress,
            "macAddress": macAddress,
            "remoteClientID": remoteClientID,
            "softwareVersion":softwareVersion,
            "producType": producType,
            "bssid": bssid,
            "dhcpInfo": json.dumps(dhcpInfo),
            "lastUpdateChecksum": lastUpdateChecksum,
            "dealerIconsCheckSum" : dealerIconsCheckSum,
            "remote_feature_support_version": remote_feature_support_version,
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddess": remoteMacAddress,
        }

        response = await self.send_command(topic,payload,requestID)
        LOGGER.debug("MQTT: Receiving pairing_request command")
        return response

    async def command_ui_delay(self,partition_id:str) -> None:
        LOGGER.debug("MQTT: Sending ui_delay command")

        # partition state needs to be sent for ui_delay to work
        partition = self.state.partition(partition_id)

        arming_command ={
            "operation_name": "ui_delay",
            "panel_status": partition.system_status,
            "userID":0,
            "partitionID": partition_id, # STR EXPECTED
            "operation_source": 1,
            "macAddress" : self.settings.random_mac,
        }

        topic = "mastermeid"
        eventName = "ipcCall"
        ipcServiceName = "qinternalservice"
        ipcInterfaceName = "android.os.IQInternalService"
        ipcTransactionID = 7
        requestID = str(uuid.uuid4())
        remoteMacAddress = self.settings.random_mac
        responseTopic = "response_" + self.settings.random_mac

        payload = {
            "eventName":eventName,
            "ipcServiceName" : ipcServiceName,
            "ipcInterfaceName" : ipcInterfaceName,
            "ipcTransactionID": ipcTransactionID,
            "ipcRequest": [{
                "dataType": "string",
                "dataValue":  json.dumps(arming_command),
            }],
            "requestID": requestID,
            "responseTopic": responseTopic,
            "remoteMacAddress": remoteMacAddress,
        }

        await self.send_command(topic,payload,requestID)
        LOGGER.debug("MQTT: Receiving ui_delay command")

    async def command_disarm(self,partition_id:str,user_code:str="",exit_sounds:bool=True) -> bool:
        LOGGER.debug("MQTT: Sending disarm command - check_user_code:%s",self.check_user_code_on_disarm)

        partition = self.state.partition(partition_id)
        if not partition:
            LOGGER.debug("MQTT: disarm command error - Unknow Partition")
            return False

        # Do local user code verification
        user_id = 0
        if self.check_user_code_on_disarm:
            user_id = self.panel.check_user(user_code)
            if user_id == -1:
                LOGGER.debug("MQTT: disarm command error - user_code error")
                return False

        async def get_mqtt_disarm_command() -> str:
            if partition.alarm_state  == PartitionAlarmState.ALARM:
                return "disarm_from_emergency"
            if partition.system_status in {PartitionSystemStatus.ARM_AWAY_EXIT_DELAY, PartitionSystemStatus.ARM_STAY_EXIT_DELAY,PartitionSystemStatus.ARM_NIGHT_EXIT_DELAY}:
                return "disarm_from_openlearn_sensor"
            if partition.system_status in {PartitionSystemStatus.ARM_AWAY, PartitionSystemStatus.ARM_STAY, PartitionSystemStatus.ARM_NIGHT}:
                await self.command_ui_delay(partition_id)
                return "disarm_the_panel_from_entry_delay"
            return "disarm_from_openlearn_sensor"

        mqtt_disarm_command = await get_mqtt_disarm_command()

        disarm_command ={
            "operation_name": mqtt_disarm_command,
            "userID":user_id,
            "partitionID":int(partition_id), # INT EXPECTED
            "operation_source": 1,
            "disarm_exit_sounds": exit_sounds,
            "macAddress" : self.settings.random_mac,
        }

        topic = "mastermeid"
        eventName = "ipcCall"
        ipcServiceName = "qinternalservice"
        ipcInterfaceName = "android.os.IQInternalService"
        ipcTransactionID = 7
        requestID = str(uuid.uuid4())
        remoteMacAddress = self.settings.random_mac
        responseTopic = "response_" + self.settings.random_mac

        payload = {"eventName":eventName,
                   "ipcServiceName" : ipcServiceName,
                   "ipcInterfaceName" : ipcInterfaceName,
                   "ipcTransactionID": ipcTransactionID,
                   "ipcRequest": [{
                       "dataType": "string",
                       "dataValue":  json.dumps(disarm_command),
                   }],
                   "requestID":requestID,
                   "responseTopic":responseTopic,
                   "remoteMacAddress":remoteMacAddress}

        await self.send_command(topic,payload,requestID)
        LOGGER.debug("MQTT: Receiving disarm command")

        return True

    async def command_zwave_switch_multi_level(self,node_id:int,level:int) -> None:

        ipcRequest =[{
                "dataType":"int", # Node ID
                "dataValue":node_id,
            },
            {
                "dataType":"int",  # ?
                "dataValue":0,
            },
            {
                "dataType":"byteArray",  # ZWAVE MULTILEVELSWITCH COMMAND
                "dataValue":[38,1,level],
            },
            {
                "dataType":"int",  # ?
                "dataValue":0,
            },
            {
                "dataType":"int",  # ?
                "dataValue":106,
            },
            {
                "dataType":"byteArray",
                "dataValue":[0],
            },
        ]

        topic = "mastermeid"
        eventName = "ipcCall"
        ipcServiceName = "qzwaveservice"
        ipcInterfaceName = "android.os.IQZwaveService"
        ipcTransactionID = 47
        requestID = str(uuid.uuid4())
        remoteMacAddress = self.settings.random_mac
        responseTopic = "response_" + self.settings.random_mac

        payload = {"eventName":eventName,
                   "ipcServiceName" : ipcServiceName,
                   "ipcInterfaceName" : ipcInterfaceName,
                   "ipcTransactionID": ipcTransactionID,
                   "ipcRequest": ipcRequest,
                   "requestID":requestID,
                   "responseTopic":responseTopic,
                   "remoteMacAddress":remoteMacAddress}

        await self.send_command(topic,payload,requestID)


    async def command_arm(self,partition_id:str,arming_type:str,user_code:str="",exit_sounds:bool=False,instant_arm:bool=False) -> bool:

        LOGGER.debug("MQTT: Sending arm command: partition%s, arming_type:%s, secure_arm:%s",partition_id,arming_type,self.panel.SECURE_ARMING)

        user_id = 0

        partition = self.state.partition(partition_id)
        if not partition:
            LOGGER.debug("MQTT: arm command error - Unknow Partition")
            return False

        if self.panel.SECURE_ARMING == "true":
            # Do local user code verification to arm if secure arming is enabled
            user_id = self.panel.check_user(user_code)
            if  user_id == -1:
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
                LOGGER.debug("MQTT: Sending arm command: Unknow arming_type:%s",arming_type)
                return False

        exitSoundValue = "ON"
        if not exit_sounds:
             exitSoundValue = "OFF"

        arming_command ={
            "operation_name": mqtt_arming_type,
            "bypass_zoneid_set": "[]",
            "userID":user_id,
            "partitionID":int(partition_id),
            "exitSoundValue":  exitSoundValue,
            "entryDelayValue": "OFF",
            "multiplePartitionsSelected" : False,
            "instant_arming": instant_arm,
            "final_exit_arming_selected" : False,
            "manually_selected_zones": "[]",
            "operation_source": 1,
            "macAddress" : self.settings.random_mac,
        }

        topic = "mastermeid"
        eventName = "ipcCall"
        ipcServiceName = "qinternalservice"
        ipcInterfaceName = "android.os.IQInternalService"
        ipcTransactionID = 7
        requestID = str(uuid.uuid4())
        remoteMacAddress = self.settings.random_mac
        responseTopic = "response_" + self.settings.random_mac

        payload = {
            "eventName":eventName,
            "ipcServiceName" : ipcServiceName,
            "ipcInterfaceName" : ipcInterfaceName,
            "ipcTransactionID": ipcTransactionID,
            "ipcRequest": [{
                "dataType": "string",
                "dataValue":  json.dumps(arming_command),
            }],
            "requestID":requestID,
            "responseTopic":responseTopic,
            "remoteMacAddress":remoteMacAddress,
        }

        await self.send_command(topic,payload,requestID)

        return True

