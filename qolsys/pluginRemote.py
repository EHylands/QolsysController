import aiomqtt
import asyncio
import datetime
import json
import random
import ssl
import uuid

from qolsys.plugin import QolsysPlugin
from qolsys.state import QolsysState
from qolsys.mdns import QolsysMDNS
from qolsys.pki import QolsysPKI
from qolsys.panel import QolsysPanel

from qolsys.event import *
from qolsys.event_mqtt import *
from qolsys.exceptions import UnknownQolsysEventException
from qolsys.settings import QolsysSettings

from qolsys.utils_mqtt import fix_json_string
from qolsys.utils_mqtt import generate_random_mac
from qolsys.utils_mqtt import c4_arming_status_to_mqtt

LOGGER = logging.getLogger(__name__)

class QolsysPluginRemote(QolsysPlugin):
        
    def __init__(self,state:QolsysState,panel:QolsysPanel,settings:QolsysSettings)-> None:
        super().__init__(state,panel,settings)
        
        # PKI
        self._keys_directory = 'keys/'
        self._pki = QolsysPKI(keys_directory = self._keys_directory)

        # Plugin
        self._plugin_ip = ''
        self.certificate_exchange_server = None
        self._check_user_code_on_disarm = True
        self._log_mqtt_messages = False

        # Qolsys Panel Infpormation
        self._panel_ip = ''
        self.panel_mqtt_port = 8883

        #MQTT Client
        self.aiomqtt = None
        self._command_list = list()

    @property
    def log_mqtt_mesages(self):
        return self._log_mqtt_messages
    
    @log_mqtt_mesages.setter
    def log_mqtt_mesages(self,log_mqtt_mesages):
        self._log_mqtt_messages = log_mqtt_mesages

    @property
    def check_user_code_on_disarm(self) -> bool:
        return self._check_user_code_on_disarm
    
    @check_user_code_on_disarm.setter
    def check_user_code_on_disarm(self,check_user_code_on_disarm:bool):
        self._check_user_code_on_disarm = check_user_code_on_disarm

    async def config(self, plugin_ip:str,panel_ip:str)->bool:
        
        LOGGER.debug(f'Configuring Plugin')
        super().config()

        self._plugin_ip = plugin_ip
        self._panel_ip = panel_ip

        # Check if pairing data is available
        if not self.settings.read_settings():
            return False

        # Start paring process if plugin is not paired
        if not self.settings.plugin_paired:
            if not await self.start_initial_pairing():
                LOGGER.debug(f'Error Pairing with Panel')
                return False

        LOGGER.debug(f'Starting Plugin Operation')
        
        # Check for valid PKI
        LOGGER.debug(f'Checking PKI')
        self._pki.set_id(self.settings.random_mac)
        if not(self._pki.check_qolsys_cer_file() and 
               self._pki.check_secure_file()):
            return False
        
        # Everything is configured
        return True
    
    async def start_operation(self):

        tls_params = aiomqtt.TLSParameters(
            ca_certs = self._pki.qolsys_cer_file_path,       
            certfile = self._pki.secure_file_path,
            keyfile = self._pki.key_file_path,
            cert_reqs=ssl.CERT_REQUIRED,    
            tls_version=ssl.PROTOCOL_TLSv1_2,  
            ciphers='ALL:@SECLEVEL=0'
        )
        
        LOGGER.debug(f'MQTT: Connecting ...')
        async with aiomqtt.Client(hostname=self._panel_ip,
                                  port=self.panel_mqtt_port,
                                  tls_params=tls_params,
                                  tls_insecure=True,
                                  clean_session=True,
                                  identifier='QolsysController') as self.aiomqtt:
            
            LOGGER.debug(f'MQTT: Client Connected')
            #await self.aiomqtt.subscribe("#")
            #await self.aiomqtt.subscribe("iq2meid")
            await self.aiomqtt.subscribe('PanelEvent',qos=2)
            await self.aiomqtt.subscribe("response_" + self.settings.random_mac,qos=2)
            await self.aiomqtt.subscribe("mastermeid",qos=2)

            await self.command_connect()
            await self.command_pingevent()
            await self.command_timesync()
            await self.command_sync_database()
            await self.command_acstatus()
            await self.command_dealer_logo()
            await self.command_pair_status_request()
            
            async for message in self.aiomqtt.messages:
                
                if self.log_mqtt_mesages:
                    LOGGER.debug(f'MQTT TOPIC: {message.topic}\n{message.payload.decode()}')

                if message.topic.matches("PanelEvent"):
                    
                    data = json.loads(message.payload)    
                    event_type = data.get('event')
                        
                    if not event_type:
                        raise UnknownQolsysEventException(f'Event type not found for event {data}')

                    match event_type:

                        case 'ARMING':

                            event = QolsysEventArming.from_json(data)

                            partition = self.state.partition(event.partition_id)
                            if partition is None:
                                LOGGER.debug(f'Partition {event.partition_id} not found')
                                return

                            partition.status = event.arming_type

                        case 'ALARM':

                            event = QolsysEventAlarm.from_json(data)
                            
                            #LOGGER.debug(f'ARMING partition_id={event.partition_id} '
                            #             f'status={event.arming_type}')

                            partition = self.state.partition(event.partition_id)
                            if partition is None:
                                LOGGER.debug(f'Partition {event.partition_id} not found')
                                return

                            partition.status = event.alarm_type

                        case 'ZONE_EVENT':
                                
                            zone_event_type = data.get('zone_event_type')
                                
                            if not zone_event_type:
                                raise UnknownQolsysEventException(f'Zone Event type not found for event {data}')
                        
                            match(zone_event_type):
                                    
                                case 'ZONE_ACTIVE':
                                    
                                    event = QolsysEventZoneEventActive.from_json(data)

                                    if event.zone.status.lower() == 'open':
                                        self.state.zone_open(event.zone.id)
                                    else:
                                        self.state.zone_closed(event.zone.id)
                            
                                case 'ZONE_UPDATE':
                                    event = QolsysEventZoneEventUpdate.from_json(data)
                                    LOGGER.debug(f'UPDATE zone={event.zone}')

                                    partition = self.state.partition(event.zone.partition_id)
                                    if partition is None:
                                        LOGGER.debug(f'Partition {event.zone.partition_id} not found')
                                        return
                                    
                                    event.zone.partition = partition
                                    self.state.zone_update(event.zone)

                                case 'ZONE_ADD':
                                    
                                    event = QolsysEventZoneEventAdd.from_json(data)
                                    LOGGER.debug(f'ADD zone={event.zone}')

                                    partition = self.state.partition(event.zone.partition_id)
                                    if partition is None:
                                        LOGGER.debug(f'Partition {event.zone.partition_id} not found')
                                        return
                                    
                                    event.zone.partition = partition
                                    self.state.zone_add(event.zone)

                                case 'ZONE_DELETE':
                                    event = QolsysEventZoneEventDelete.from_json(data)
                                    LOGGER.debug(f'DELETE zone={event.zone}')

                                    partition = self.state.partition(event.zone.partition_id)
                                    if partition is None:
                                        LOGGER.debug(f'Partition {event.zone.partition_id} not found')
                                        return
                                    
                                    event.zone.partition = partition
                                    self.state.zone_delete(event)

                                case _:
                                    raise UnknownQolsysEventException(f'Zone Event type not found for event {data}')

                        case _:
                            raise UnknownQolsysEventException(f'Zone Event not found for event {data}')

                # Panel response to MQTT Commands
                if message.topic.matches("response_" + self.settings.random_mac):
                    
                    data = message.payload.decode().replace("\\\\", "\\")
                    data = fix_json_string(data)
                    data = json.loads(data,strict=False)
                    event = data.get('eventName')

                    match event:

                        case 'syncdatabase':
                            
                            LOGGER.debug(f'MQTT: Updating State from syncdatabase')
                            event = QolsysEventSyncDB(request_id=data['requestID'],raw_event=data)
                            self.panel.load_database(event.database_frome_json(data))
                            partitions = self.panel.get_partitions()
                            self.state.update(partitions)
                            
                            self.panel.dump()
                            self.state.dump()

                        case 'timeSync':
                            LOGGER.debug(f'MQTT: timeSync command response')

                        case 'pingevent':
                            LOGGER.debug(f'MQTT: pingevent command response')

                        case 'connect':
                            LOGGER.debug(f'MQTT: connect command response') 

                        case 'ipcCall':
                            LOGGER.debug(f'MQTT: ipcCall command response: {data.get('responseStatus')}') 

                        case 'pair_status_request':
                            LOGGER.debug(f'MQTT: pair_status_request command response') 

                        case _:
                            LOGGER.debug(f'MQTT: unknow event {event}') 

    async def start_initial_pairing(self)->bool:
       
        # check if local mac exist
        if self.settings.random_mac == '':
            LOGGER.debug(f'Creating random_mac')
            self.settings.random_mac = generate_random_mac()
            self._pki.create(self.settings.random_mac,key_size=2048)

            # Save random_mac to pairing status file
            self.settings.save_settings()

        # Check if PKI is valid
        self._pki.set_id(self.settings.random_mac)
        LOGGER.debug(f'Checking PKI')
        if not(self._pki.check_key_file() and 
               self._pki.check_cer_file() and 
               self._pki.check_csr_file()):
            LOGGER.error(f'PKI Error')
            return False
        
        LOGGER.debug(f'Starting Pairing Process')

        # If we dont allready have client signed certificate, start the pairing server
        if not self._pki.check_secure_file():
            
            # High Level Random Pairing Port
            pairing_port = random.randint(50000, 55000)

            # Start Pairing mDNS Brodcast
            LOGGER.debug(f'Starting mDNS Service Discovery:' + str(self._plugin_ip + ':' + str(pairing_port)))
            mdns_server = QolsysMDNS(self._plugin_ip,pairing_port)
            await mdns_server.start_mdns()

            # Start Key Exchange Server
            LOGGER.debug(f'Starting Certificate Exchange Server')
        
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile = self._pki.cer_file_path, keyfile = self._pki.key_file_path)
            self.certificate_exchange_server = await asyncio.start_server(self.handle_key_exchange_client,self._plugin_ip, pairing_port,ssl=context)
        
            LOGGER.debug(f'Certificate Exchange Server Waiting for Panel')
            LOGGER.debug(f'Press Pair Button in IQ Remote Config Page ...')

            async with self.certificate_exchange_server:
                try:
                    await self.certificate_exchange_server.serve_forever()
                
                except asyncio.CancelledError:

                    LOGGER.debug(f'Stoping Certificate Exchange Server')
                
                    LOGGER.debug(f'Stoping mDNS Service Discovery')
                    await mdns_server.stop_mdns()

                    if not self._pki.check_secure_file():
                        LOGGER.error(f'MQTT Pairing Error')
                        return False

        LOGGER.debug(f'Sending MQTT Pairing Request to Panel')

        # We have client sgined certificate at this point
        # Connect to Panel MQTT to send pairing command
        
        tls_params = aiomqtt.TLSParameters(
            ca_certs = self._pki.qolsys_cer_file_path,       
            certfile = self._pki.secure_file_path ,
            keyfile = self._pki.key_file_path,
            cert_reqs=ssl.CERT_REQUIRED,    
            tls_version=ssl.PROTOCOL_TLSv1_2,  
            ciphers='ALL:@SECLEVEL=0'
        )

        LOGGER.debug(f'MQTT: Connecting ...')
        async with aiomqtt.Client(hostname=self._panel_ip,
                                  port=self.panel_mqtt_port,
                                  tls_params=tls_params,
                                  tls_insecure=True,
                                  clean_session=True,
                                  identifier='QolsysController') as self.aiomqtt:
            
            LOGGER.debug(f'MQTT: Client Connected')

            await self.aiomqtt.subscribe("response_" + self.settings.random_mac,qos=2)
            await self.command_pairing_request()
        
            async for message in self.aiomqtt.messages:
                if message.topic.matches('response_' + self.settings.random_mac):
                # For the moment, pairing request always return false
                # Need to find proper parameter for panel to confirm pairing
                # Plugin will appear in IQ Remote page with inactive status
                # Mark pairing as complete
                    self.settings.plugin_paired = True
                    self.settings.save_settings()

                    LOGGER.debug(f'Plugin Pairing Completed ')
                    return True
                
        return False
    
    async def handle_key_exchange_client(self,reader, writer):
    
        received_panel_mac = False
        received_signed_client_certificate = False
        received_qolsys_cer = False

        try:
            Continue = True
            while Continue:

                request = (await reader.read(6144))

                # Plugin is receiving panel_mac from panel
                if(received_panel_mac == False and
                   received_signed_client_certificate == False and
                   received_qolsys_cer == False):
                    
                    mac = request.decode()

                    LOGGER.debug(f'Receiving from Panel: {mac}')
                    
                    # Remove \x00 and \x01 from received string
                    self.settings.panel_mac = ''.join(char for char in mac if char.isprintable())
                    received_panel_mac = True

                    # Sending random_mac to panel
                    message = b'\x00\x11' + self.settings.random_mac.encode()
                    LOGGER.debug(f'Sending to Panel: {message.decode()}')
                    writer.write(message)
                    writer.write(b'sent')
                    await writer.drain()

                    #Sending CSR File to panel
                    with open(self._pki.csr_file_path, "rb") as file:
                        content = file.read()
                        LOGGER.debug(f'Sending to Panel: [CSR File Content]')
                        writer.write(content)
                        await writer.drain()

                    continue
               
                if(received_panel_mac == True and
                   received_signed_client_certificate == False and
                   received_qolsys_cer == False):
                    
                    certificates = [item for item in request.decode().split('sent') if item]

                    # Saving signed client certificate
                    LOGGER.debug(f'Receiving from Panel: {len(certificates)} certificate')

                    if len(certificates) <= 2:
                        LOGGER.debug(f'Saving [Signed Client Certificate]')
                        if(len(certificates) > 0):
                            with open(self._pki.secure_file_path, "wb") as f:
                                f.write(certificates[0].encode())
                                received_signed_client_certificate = True
                    
                    if len(certificates) > 1:
                        # Saving Qolsys self signed certificate
                        LOGGER.debug(f'Saving [Qolsys Certificate]')
                        with open(self._pki.qolsys_cer_file_path, "w") as f:
                            f.write(certificates[1])
                            received_qolsys_cer = True

                    # Check if all data has been received   
                    if(received_panel_mac == True and
                        received_signed_client_certificate == True and
                        received_qolsys_cer == True):
                            Continue = False
                            writer.close()

                    continue

                # Sometime, panel will send signed client certificate and qolsys certificate in 2 packets
                if(received_panel_mac == True and
                   received_signed_client_certificate == True and
                   received_qolsys_cer == False):

                    certificates = [item for item in request.decode().split('sent') if item]

                    LOGGER.debug(f'Receiving from Panel: {len(certificates)} certificate')

                    if len(certificates) == 1:
                        # Saving Qolsys self signed certificate
                        LOGGER.debug(f'Saving [Qolsys Certificate]')
                        with open(self._pki.qolsys_cer_file_path, "w") as f:
                            f.write(certificates[0])
                            received_qolsys_cer = True

                            Continue = False
                            writer.close()

        except asyncio.CancelledError:
            LOGGER.error(f'Key Exchange Server asyncio CancelledError')

        except Exception as e:
            LOGGER.error(f'Key Exchange Server error: {e}')
            
        finally:
            writer.close()
            self.certificate_exchange_server.close()

    async def send_command(self,topic:str,json_payload:str):
        if self.aiomqtt == None:
            LOGGER.error(f'MQTT Client not configured')
            return
        
        await self.aiomqtt.publish(topic=topic,payload=json.dumps(json_payload),qos=2)

    async def command_connect(self):
        LOGGER.debug(f'MQTT: Sending connect command')

        topic = 'mastermeid'
        ipAddress = self._plugin_ip
        eventName = 'connect_v204'
        macAddress = self.settings.random_mac
        remoteClientID = 'QolsysController'
        softwareVersion = '4.4.1'
        producType = 'tab07_rk68'
        bssid = '24:5a:4c:6b:87:29'
        lastUpdateChecksum = '2132501716'
        dealerIconsCheckSum = ''
        remote_feature_support_version = '1'
        current_battery_status = 'Normal'
        remote_panel_battery_status = 3
        remote_panel_battery_health = 2
        remote_panel_battery_level = 100
        remote_panel_battery_present = True
        remote_panel_battery_percentage = 100
        remote_panel_battery_scale = 100
        remote_panel_battery_voltage = 4082
        remote_panel_battery_technology = ''
        remote_panel_plugged = 1
        remote_panel_battery_temperature = 430
        requestID = str(uuid.uuid4())
        responseTopic = 'response_' + self.settings.random_mac
        remoteMacAddress = self.settings.random_mac

        dhcpInfo = {
            'ipaddress':ipAddress,
            'gateway':'192.168.10.1',
            'netmask':'0.0.0.0',
            'dns1':'8.8.8.8',
            'dns2':'0.0.0.0',
            'dhcpServer':'192.168.10.1',
            'leaseDuration':'360000'
        }

        payload = { 'eventName':eventName,
                    'ipAddress':ipAddress,
                    'macAddress':macAddress,
                    'remoteClientID': remoteClientID,
                    'softwareVersion':softwareVersion,
                    'producType': producType,
                    'bssid': bssid,
                    'dhcpInfo': json.dumps(dhcpInfo),
                    'lastUpdateChecksum':lastUpdateChecksum,
                    'dealerIconsCheckSum' : dealerIconsCheckSum,
                    'remote_feature_support_version':remote_feature_support_version,
                    'current_battery_status': current_battery_status,
                    'remote_panel_battery_status':remote_panel_battery_status,
                    'remote_panel_battery_health': remote_panel_battery_health,
                    'remote_panel_battery_level': remote_panel_battery_level,
                    'remote_panel_battery_present': remote_panel_battery_present,
                    'remote_panel_battery_percentage': remote_panel_battery_percentage,
                    'remote_panel_battery_scale': remote_panel_battery_scale,
                    'remote_panel_battery_voltage': remote_panel_battery_voltage,
                    'remote_panel_battery_technology': remote_panel_battery_technology,
                    'remote_panel_plugged': remote_panel_plugged,
                    'remote_panel_battery_temperature' : remote_panel_battery_temperature,
                    'requestID':requestID,
                    'responseTopic':responseTopic ,
                    'remoteMacAddess':remoteMacAddress
            }
        #await self.aiomqtt.publish(topic=topic,payload='{"ipAddress":"192.168.10.214","macAddress":"cc:4b:73:86:5c:88","remoteClientID":"remoteClient_paho1749959228576000000","softwareVersion":"4.4.1","productType":"tab07_rk68","bssid":"24:5a:4c:6b:87:29","dhcpInfo":"{\\"ipaddress\\":\\"192.168.10.214\\",\\"gateway\\":\\"192.168.10.1\\",\\"netmask\\":\\"0.0.0.0\\",\\"dns1\\":\\"8.8.8.8\\",\\"dns2\\":\\"0.0.0.0\\",\\"dhcpServer\\":\\"192.168.10.1\\",\\"leaseDuration\\":\\"43200\\"}","eventName":"connect_v204","lastUpdateChecksum":"2132501716","dealerIconsCheckSum":"","remote_feature_support_version":"1","current_battery_status":"Normal","remote_panel_battery_status":3,"remote_panel_battery_health":2,"remote_panel_battery_level":100,"remote_panel_battery_present":true,"remote_panel_battery_percentage":100,"remote_panel_battery_scale":100,"remote_panel_battery_voltage":4082,"remote_panel_battery_technology":"","remote_panel_plugged":1,"remote_panel_battery_temperature":430,"requestID":"acdd579d-0da7-4ec7-98d7-6aa5ef745765","responseTopic":"response_cc:4b:73:86:5c:88","remoteMacAddress":"cc:4b:73:86:5c:88"}',qos=2)

        await self.send_command(topic,payload)

    async def command_pingevent(self):
        LOGGER.debug(f'MQTT: Sending pingevent command')

        topic = 'mastermeid'
        eventName = 'pingevent'
        macAddress = self.settings.random_mac
        remote_panel_status = 'Active'
        ipAddress = self._plugin_ip
        current_battery_status = 'Normal'
        remote_panel_battery_percentage = 100
        remote_panel_battery_temperature = 430
        remote_panel_battery_status = 3
        remote_panel_battery_scale = 100
        remote_panel_battery_voltage = 4102
        remote_panel_battery_present = True
        remote_panel_battery_technology = ''
        remote_panel_battery_level = 100
        remote_panel_battery_health = 2
        remote_panel_plugged = 1
        requestID = str(uuid.uuid4())
        remoteMacAddress = self.settings.random_mac
        responseTopic = 'response_' + self.settings.random_mac

        payload = {'eventName':eventName,
                    'macAddress': macAddress,
                    'remote_panel_status': remote_panel_status,
                    'ipAddress': ipAddress,
                    'current_battery_status' : current_battery_status,
                    'remote_panel_battery_percentage':remote_panel_battery_percentage,
                    'remote_panel_battery_temperature' : remote_panel_battery_temperature,
                    'remote_panel_battery_status' : remote_panel_battery_status,
                    'remote_panel_battery_scale': remote_panel_battery_scale,
                    'remote_panel_battery_voltage' : remote_panel_battery_voltage,
                    'remote_panel_battery_present' : remote_panel_battery_present,
                    'remote_panel_battery_technology': remote_panel_battery_technology,
                    'remote_panel_battery_level': remote_panel_battery_level,
                    'remote_panel_battery_health' : remote_panel_battery_health,
                    'remote_panel_plugged' : remote_panel_plugged,
                    'requestID':requestID,
                    'responseTopic': responseTopic,
                    'remoteMacAddess':remoteMacAddress
        }

        await self.send_command(topic,payload)

    async def command_timesync(self):
        LOGGER.debug(f'MQTT: Sending timeSync command')

        topic = 'mastermeid'
        eventName = 'timeSync'
        startTimestamp = datetime.datetime.now().timestamp()
        requestID = str(uuid.uuid4())
        responseTopic = 'response_' + self.settings.random_mac
        remoteMacAddress = self.settings.random_mac

        payload = {'eventName':eventName,
                   'startTimestamp': startTimestamp,
                   'requestID':requestID,
                   'responseTopic':responseTopic,
                   'remoteMacAddess':remoteMacAddress
        }
        
        await self.send_command(topic,payload)

    async def command_sync_database(self):
        LOGGER.debug(f'MQTT: Sending syncdatabase command')

        topic = 'mastermeid'
        eventName = 'syncdatabase'
        requestID = str(uuid.uuid4())
        responseTopic = 'response_' + self.settings.random_mac
        remoteMacAddress = self.settings.random_mac

        payload = {'eventName':eventName,
                   'requestID':requestID,
                   'responseTopic':responseTopic,
                   'remoteMacAddess':remoteMacAddress}

        await self.send_command(topic,payload)

    async def command_acstatus(self):
        LOGGER.debug(f'MQTT: Sending acStatus command')

        topic = 'mastermeid'
        eventName = 'acStatus'
        requestID = str(uuid.uuid4())
        responseTopic = 'response_' + self.settings.random_mac
        remoteMacAddress = self.settings.random_mac
        acStatus = 'Connected'

        payload = {'eventName':eventName,
                   'acStatus' : acStatus,
                   'requestID':requestID,
                   'responseTopic':responseTopic,
                   'remoteMacAddess':remoteMacAddress}

        await self.send_command(topic,payload)
    
    async def command_dealer_logo(self):
        LOGGER.debug(f'MQTT: Sending dealerLogo command')

        topic = 'mastermeid'
        eventName = 'dealerLogo'
        requestID = str(uuid.uuid4())
        responseTopic = 'response_' + self.settings.random_mac
        remoteMacAddress = self.settings.random_mac

        payload = {'eventName':eventName,
                   'requestID':requestID,
                   'responseTopic':responseTopic,
                   'remoteMacAddess':remoteMacAddress}

        await self.send_command(topic,payload)

    async def command_pair_status_request(self):
        LOGGER.debug(f'MQTT: Sending pair_status_request command')

        topic = 'mastermeid'
        eventName = 'pair_status_request'
        remoteMacAddress = self.settings.random_mac
        requestID = str(uuid.uuid4())
        responseTopic = 'response_' + self.settings.random_mac

        payload = {'eventName':eventName,
                   'requestID':requestID,
                   'responseTopic':responseTopic,
                   'remoteMacAddess':remoteMacAddress}

        await self.send_command(topic,payload)


    async def command_disconnect(self):
        LOGGER.debug(f'MQTT: Sending disconnect command')

        topic = 'mastermeid'
        eventName = 'disconnect'
        remoteClientID = 'QolsysRemote'
        requestID = str(uuid.uuid4())
        remoteMacAddress = self.settings.random_mac

        payload = {'eventName':eventName,
                   'remoteClientID': remoteClientID,
                   'requestID':requestID,
                   'remoteMacAddess':remoteMacAddress}
        
        await self.send_command(topic,payload)

    async def command_pairing_request(self):
        LOGGER.debug(f'MQTT: Sending pairing_request command')

        topic = 'mastermeid'
        eventName = 'connect_v204'
        pairing_request = True
        ipAddress = self._plugin_ip
        macAddress = self.settings.random_mac
        remoteClientID = 'QolsysController'
        softwareVersion = '4.4.1'
        producType = 'tab07_rk68'
        bssid = '24:5a:4c:6b:87:29'
        lastUpdateChecksum = '2132501716'
        dealerIconsCheckSum = ''
        remote_feature_support_version = '1'
        requestID = str(uuid.uuid4())
        responseTopic = 'response_' + self.settings.random_mac
        remoteMacAddress = self.settings.random_mac

        dhcpInfo = {
            'ipaddress':ipAddress,
            'gateway':'192.168.10.1',
            'netmask':'0.0.0.0',
            'dns1':'8.8.8.8',
            'dns2':'0.0.0.0',
            'dhcpServer':'192.168.10.1',
            'leaseDuration':'360000'
        }

        payload = {'eventName':eventName,
                    'pairing_request':pairing_request,
                    'ipAddress':ipAddress,
                    'macAddress':macAddress,
                    'remoteClientID': remoteClientID,
                    'softwareVersion':softwareVersion,
                    'producType': producType,
                    'bssid': bssid,
                    'dhcpInfo': json.dumps(dhcpInfo),
                    'lastUpdateChecksum':lastUpdateChecksum,
                    'dealerIconsCheckSum' : dealerIconsCheckSum,
                    'remote_feature_support_version':remote_feature_support_version,
                    'requestID':requestID,
                    'responseTopic':responseTopic,
                    'remoteMacAddess':remoteMacAddress}
        
        await self.send_command(topic,payload)


    async def command_ui_delay(self,partition_id):
        LOGGER.debug(f'MQTT: Sending ui_delay command')

        # partition state needs to be sent for ui_delay to work
        partition = self.state.partition(partition_id)

        arming_command ={
            "operation_name": 'ui_delay',
            "panel_status": c4_arming_status_to_mqtt(partition.status),
            "userID":0,
            "partitionID":partition_id,
            "operation_source": 1,
            "macAddress" : self.settings.random_mac
        }

        topic = 'mastermeid'
        eventName = 'ipcCall'
        ipcServiceName = 'qinternalservice'
        ipcInterfaceName = 'android.os.IQInternalService'
        ipcTransactionID = 7
        requestID = str(uuid.uuid4())
        remoteMacAddress = self.settings.random_mac
        responseTopic = 'response_' + self.settings.random_mac

        payload = {'eventName':eventName,
                   'ipcServiceName' : ipcServiceName,
                   'ipcInterfaceName' : ipcInterfaceName,
                   'ipcTransactionID': ipcTransactionID,
                   'ipcRequest': [{
                       'dataType': 'string',
                       'dataValue':  json.dumps(arming_command)
                   }],
                   'requestID':requestID,
                   'responseTopic':responseTopic,
                   'remoteMacAddress':remoteMacAddress}
            
        await self.send_command(topic,payload)


    async def command_disarm(self,partition_id:int,user_code:str='') -> bool:
        LOGGER.debug(f'MQTT: Sending disarm command - check_user_code:{self.check_user_code_on_disarm}')

        partition = self.state.partition(partition_id)
        if not partition:
            LOGGER.debug(f'MQTT: disarm command error - Unknow Partition')
            return False
        
        # Do local user code verification
        user_id = 0
        if self.check_user_code_on_disarm:
            user_id = self.panel.check_user(user_code)
            if user_id == -1:
                LOGGER.debug(f'MQTT: disarm command error - user_code error')
                return False

        mqtt_disarm_command = ''
        
        if partition.status == 'EXIT_DELAY':
            mqtt_disarm_command = 'disarm_from_openlearn_sensor'

        if partition.status == 'ALARM' or partition.status == 'FIRE' or partition.status == 'AUXILIARY' or partition.status == 'POLICE':
            mqtt_disarm_command = 'disarm_from_emergency'
        
        if partition.status == 'ARM_AWAY' or partition.status == 'ARM_STAY':
            await self.command_ui_delay(partition_id)
            mqtt_disarm_command = 'disarm_the_panel_from_entry_delay'
        
        disarm_command ={
            "operation_name": mqtt_disarm_command,
            "userID":user_id,
            "partitionID":partition_id,
            "operation_source": 1,
            'disarm_exit_sounds': True,
            "macAddress" : self.settings.random_mac
        }
    
        topic = 'mastermeid'
        eventName = 'ipcCall'
        ipcServiceName = 'qinternalservice'
        ipcInterfaceName = 'android.os.IQInternalService'
        ipcTransactionID = 7
        requestID = str(uuid.uuid4())
        remoteMacAddress = self.settings.random_mac
        responseTopic = 'response_' + self.settings.random_mac

        payload = {'eventName':eventName,
                   'ipcServiceName' : ipcServiceName,
                   'ipcInterfaceName' : ipcInterfaceName,
                   'ipcTransactionID': ipcTransactionID,
                   'ipcRequest': [{
                       'dataType': 'string',
                       'dataValue':  json.dumps(disarm_command)
                   }],
                   'requestID':requestID,
                   'responseTopic':responseTopic,
                   'remoteMacAddress':remoteMacAddress}
        
        await self.send_command(topic,payload)

    async def command_arm(self,partition_id:int,arming_type:str,user_code:str='',exit_sounds:bool=False) -> bool:
        
        LOGGER.debug(f'MQTT: Sending arm command: partition{partition_id}, arming_type:{arming_type}, secure_arm:{self.panel.get_secure_arming()}' )

        user_id = 0

        partition = self.state.partition(partition_id)
        if not partition:
            LOGGER.debug(f'MQTT: arm command error - Unknow Partition')
            return False
        
        if self.panel.get_secure_arming():
            # Do local user code verification to arm if secure arming is enabled
            user_id = self.panel.check_user(user_code)
            if  user_id == -1:
                LOGGER.debug(f'MQTT: arm command error - user_code error')
                return False

        mqtt_arming_type = ''
        match arming_type:
            case "ARM_STAY":
                mqtt_arming_type = 'ui_armstay'

            case "ARM_AWAY":
                mqtt_arming_type = 'ui_armaway'

            case _:
                LOGGER.debug(f'MQTT: Sending arm command: Unknow arming_type:{arming_type}')
                return False

        exitSoundValue = "ON"
        if exit_sounds == False:
             exitSoundValue = "OFF"
        
        arming_command ={
            "operation_name": mqtt_arming_type,
            "bypass_zoneid_set": "[]",
            "userID":user_id,
            "partitionID":partition_id,
            "exitSoundValue":  exitSoundValue,
            "entryDelayValue": "ON",
            "multiplePartitionsSelected" : False,
            "instant_arming": True,
            "final_exit_arming_selected" : False,
            "manually_selected_zones": "[]",
            "operation_source": 1,
            "macAddress" : self.settings.random_mac
        }
    
        topic = 'mastermeid'
        eventName = 'ipcCall'
        ipcServiceName = 'qinternalservice'
        ipcInterfaceName = 'android.os.IQInternalService'
        ipcTransactionID = 7
        requestID = str(uuid.uuid4())
        remoteMacAddress = self.settings.random_mac
        responseTopic = 'response_' + self.settings.random_mac

        payload = {'eventName':eventName,
                   'ipcServiceName' : ipcServiceName,
                   'ipcInterfaceName' : ipcInterfaceName,
                   'ipcTransactionID': ipcTransactionID,
                   'ipcRequest': [{
                       'dataType': 'string',
                       'dataValue':  json.dumps(arming_command)
                   }],
                   'requestID':requestID,
                   'responseTopic':responseTopic,
                   'remoteMacAddress':remoteMacAddress}
        
        await self.send_command(topic,payload)
