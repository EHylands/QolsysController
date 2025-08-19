## Qolsys MQTT Server Commands
### MQTT Messages 
#### PanelEvent Topic
##### `EVENT ZONE_EVENT`
`ZONE_DELETE`
```json
{
        "event":"ZONE_EVENT",
        "zone_event_type":"ZONE_DELETE",
        "zone":{
                "zone_id":2
        },
        "version":1,
        "requestID":"18f4ff3e-492c-4f18-9fa7-04c286b85a3c"
}
```
`ZONE_ACTIVE`
```json
{
        "event":"ZONE_EVENT",
        "zone_event_type":"ZONE_ACTIVE",
        "zone":{
                "status":"Closed",
                "zone_id":4
        },
        "version":1,
        "requestID":"1441048c-6330-466c-abfd-0edb9f89bd3b"
}
```
`ZONE_UPDATE`
```json
{
        "event":"ZONE_EVENT",
        "zone_event_type":"ZONE_UPDATE",
        "zone":{
                "id":"IQR2",
                "type":"Keypad",
                "name":"QolsysController",
                "group":"fixedintrusion",
                "status":"Closed",
                "state":"0",
                "zone_id":2,
                "zone_physical_type":4,
                "zone_alarm_type":0,
                "zone_type":104,
                "partition_id":0
        },
        "version":1,
        "requestID":"0ba58aa6-193b-4a2a-9e92-33e4a357313b"
}
```
`ZONE_ADD`
To be determined
#### `EVENT ARMING`
`EXIT_DELAY`
```json
{
        "event":"ARMING",
        "arming_type":"EXIT_DELAY",
        "delay":60,
        "partition_id":0,
        "version":1,
        "requestID":"9fee3bbb-c45d-4722-a0b3-65603f5f6040"
}
```
`ENTRY_DELAY`
```json
{
        "event":"ARMING",
        "arming_type":"ENTRY_DELAY",
        "delay":30,
        "partition_id":0,
        "version":1,
        "requestID":"d4f3a2bc-be80-4174-be25-c9faee8cf267"
}
```
`ARM_AWAY`
```json
{
        "event":"ARMING",
        "arming_type":"ARM_AWAY",
        "partition_id":0,
        "version":1,
        "requestID":"ae67f765-95d0-4977-99a2-00abc08f1b73"
}
```
`DISARM`
```json
{
        "event":"ARMING",
        "arming_type":"DISARM",
        "partition_id":0,
        "version":1,
        "requestID":"1edbf716-75bf-4b94-acdd-2381f85143fe"
}
```
#### `EVENT ALARM`
`alarm_type` `""`
```json
{
        "event":"ALARM",
        "alarm_type":"",
        "version":1,
        "partition_id":0,
        "requestID":"62774012-a046-4c8e-b883-44865dc60e5a"
}
```
`alarm_type` `POLICE`
```json
{
        "event":"ALARM",
        "alarm_type":"POLICE",
        "version":1,
        "partition_id":0,
        "requestID":"5add7185-7c94-41a7-8a67-3df911c80d0f"
}
```
`alarm_type` `AUXILIARY`
```json
{
        "event":"ALARM",
        "alarm_type":"AUXILIARY",
        "version":1,
        "partition_id":0,
        "requestID":"9e0986d7-491d-41e9-bf21-5ece79409f10"
}
```
`alarm_type` `FIRE`
```json
{
        "event":"ALARM",
        "alarm_type":"FIRE",
        "version":1,
        "partition_id":0,
        "requestID":"f891435e-0891-41d7-8f52-0eed494141c9"
}
```

### MQTT COMMANDS
#### command ui_armaway
```
{
        "eventName":"ipcCall",
        "ipcServiceName":"qinternalservice",
        "ipcInterfaceName":"android.os.IQInternalService",
        "ipcTransactionID":7,
        "ipcRequest":[{
                "dataType":"string",
                "dataValue":"{\\"operation_name\\":\\"ui_armaway\\",\\"bypass_zoneid_set\\":\\"[]\\",\\"userID\\":0,\\"partitionID\\":0,\\"exitSoundValue\\":\\"ON\\",\\"entryDelayValue\\":\\"ON\\",\\"multiplePartitionsSelected\\":false,\\"instant_arming\\":false,\\"final_exit_arming_selected\\":false,\\"manually_selected_zones\\":\\"[]\\",\\"operation_source\\":1,\\"macAddress\\":\\"F2:16:3E:08:81:A7\\""
        }],
        "requestID":"11e6b01b-c35f-4050-a72c-900c6d481a85",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command ui_armstay
```
{
        "eventName":"ipcCall",
        "ipcServiceName":"qinternalservice",
        "ipcInterfaceName":"android.os.IQInternalService",
        "ipcTransactionID":7,
        "ipcRequest":[
                {"dataType":"string",
                "dataValue":"{\\"operation_name\\":\\"ui_armstay\\",\\"bypass_zoneid_set\\":\\"[]\\",\\"userID\\":0,\\"partitionID\\":0,\\"exitSoundValue\\":\\"ON\\",\\"entryDelayValue\\":\\"ON\\",\\"multiplePartitionsSelected\\":false,\\"instant_arming\\":false,\\"final_exit_arming_selected\\":false,\\"manually_selected_zones\\":\\"[]\\",\\"operation_source\\":1,\\"macAddress\\":\\"F2:16:3E:08:81:A7\\"}"
        }],
        "requestID":"0702a01d-180c-47d5-9007-bb7c7534b8c8",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command disarm_the_panel_from_entry_delay
Disarm the panel when partition is in entry_delay mode
```
{
        "eventName":"ipcCall",
        "ipcServiceName":"qinternalservice",
        "ipcInterfaceName":"android.os.IQInternalService",
        "ipcTransactionID":7,
        "ipcRequest":[{
                "dataType":"string","
                dataValue":"{\\"operation_name\\":\\"disarm_the_panel_from_entry_delay\\",\\"userID\\":2,\\"partitionID\\":0,\\"operation_source\\":1,\\"macAddress\\":\\"F2:16:3E:08:81:A7\\"}"
        }],
        "requestID":"4a655801-8609-485b-aa23-089b10494a6e",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command disarm_from_openlearn_sensor
Disarm the panel when partition is in exit_delay mode
```
{
        "eventName":"ipcCall",
        "ipcServiceName":"qinternalservice",
        "ipcInterfaceName":"android.os.IQInternalService",
        "ipcTransactionID":7,
        "ipcRequest":[{
                "dataType":"string","
                dataValue":"{\\"operation_name\\":\\"disarm_from_openlearn_sensor\\",\\"userID\\":2,\\"partitionID\\":0,\\"operation_source\\":1,\\"macAddress\\":\\"F2:16:3E:08:81:A7\\"}"
        }],
        "requestID":"4a655801-8609-485b-aa23-089b10494a6e",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command disarm_from_emergency
```
Disarm the panel when partition alarm state is triggered
{
        "eventName":"ipcCall",
        "ipcServiceName":"qinternalservice",
        "ipcInterfaceName":"android.os.IQInternalService",
        "ipcTransactionID":7,
        "ipcRequest":[{
                "dataType":"string","
                dataValue":"{\\"operation_name\\":\\"disarm_from_emergency\\",\\"userID\\":2,\\"partitionID\\":0,\\"operation_source\\":1,\\"macAddress\\":\\"F2:16:3E:08:81:A7\\"}"
        }],
        "requestID":"4a655801-8609-485b-aa23-089b10494a6e",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```

#### command ui_delay
```
{
        "eventName":"ipcCall",
        "ipcServiceName":"qinternalservice",
        "ipcInterfaceName":"android.os.IQInternalService",
        "ipcTransactionID":7,
        "ipcRequest":[{
                "dataType":"string",
                "dataValue":"{\\"operation_name\\":\\"ui_delay\\",\\"panel_status\\":\\"ARM-STAY\\",\\"userID\\":0,\\"partitionID\\":0,\\"operation_source\\":1,\\"macAddress\\":\\"F2:16:3E:08:81:A7\\"}"
        }],
        "requestID":"5fdd97ed-8b8a-47f2-884f-c2e3935597c3",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command generate_emergency - Silent Police Emergency
```
{
        "eventName":"ipcCall",
        "ipcServiceName":"qinternalservice",
        "ipcInterfaceName":"android.os.IQInternalService",
        "ipcTransactionID":7,
        "ipcRequest":[{
                "dataType":"string",
                "dataValue":"{\\"operation_name\\":\\"generate_emergency\\",\\"partitionID\\":0,\\"zoneID\\":1,\\"emergencyType\\":\\"Silent Police Emergency\\",\\"operation_source\\":1,\\"macAddress\\":\\"F2:16:3E:08:81:A7\\"}"
        }],
        "requestID":"5181dbd0-6b8c-477e-93ce-d8a969915d9c",
        "responseTopic":
        "response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command generate_emergency - Police Emergency
```
{
        "eventName":"ipcCall",
        "ipcServiceName":"qinternalservice",
        "ipcInterfaceName":"android.os.IQInternalService",
        "ipcTransactionID":7,
        "ipcRequest":[{
                "dataType":"string",
                "dataValue":"{\\"operation_name\\":\\"generate_emergency\\",\\"partitionID\\":0,\\"zoneID\\":1,\\"emergencyType\\":\\"Police Emergency\\",\\"operation_source\\":1,\\"macAddress\\":\\"F2:16:3E:08:81:A7\\"}"
        }],
        "requestID":"361190dc-e75e-436f-9158-1f459aecdaba",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command generate_emergency - Silent Auxiliary Emergency
```
{
        "eventName":"ipcCall",
        "ipcServiceName":"qinternalservice",
        "ipcInterfaceName":"android.os.IQInternalService",
        "ipcTransactionID":7,
        "ipcRequest":[{
                "dataType":"string",
                "dataValue":"{\\"operation_name\\":\\"generate_emergency\\",\\"partitionID\\":0,\\"zoneID\\":1,\\"emergencyType\\":\\"Silent Auxiliary Emergency\\",\\"operation_source\\":1,\\"macAddress\\":\\"F2:16:3E:08:81:A7\\"}"
        }],
        "requestID":"ca578687-a1a0-482e-b434-7de313adf8b5",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command generate_emergency - Auxiliary Emergency
```
{
        "eventName":"ipcCall",
        "ipcServiceName":"qinternalservice",
        "ipcInterfaceName":"android.os.IQInternalService",
        "ipcTransactionID":7,
        "ipcRequest":[{
                "dataType":"string",
                "dataValue":"{\\"operation_name\\":\\"generate_emergency\\",\\"partitionID\\":0,\\"zoneID\\":1,\\"emergencyType\\":\\"Auxiliary Emergency\\",\\"operation_source\\":1,\\"macAddress\\":\\"F2:16:3E:08:81:A7\\"}"
        }],
        "requestID":"20257444-dfac-4e6c-a82b-fe7ff5d423b6",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command generate_emergency - Fire Emergency
```
{
        "eventName":"ipcCall",
        "ipcServiceName":"qinternalservice",
        "ipcInterfaceName":"android.os.IQInternalService",
        "ipcTransactionID":7,
        "ipcRequest":[{
                "dataType":"string",
                "dataValue":"{\\"operation_name\\":\\"generate_emergency\\",\\"partitionID\\":0,\\"zoneID\\":1,\\"emergencyType\\":\\"Fire Emergency\\",\\"operation_source\\":1,\\"macAddress\\":\\"F2:16:3E:08:81:A7\\"}"
        }],
        "requestID":"3f34cec3-3cc2-4f4f-afab-252f01d6dadb",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command pairing_request
Pair QolsysController with Panel (QolsysController will appear in IQ Remote list on Panel with an Inactive state)
```
{
        "eventName": "connect_v204", 
        "pairing_request": true, 
        "ipAddress": "192.168.10.219", 
        "macAddress": "F2:16:3E:08:81:A7", 
        "remoteClientID": "QolsysController", 
        "softwareVersion": "4.4.1", 
        "producType": "tab07_rk68", 
        "bssid": "24:5a:4c:6b:87:29", 
        "dhcpInfo": "{\\"ipaddress\\": \\"192.168.10.219\\", \\"gateway\\": \\"192.168.10.1\\", \\"netmask\\": \\"0.0.0.0\\", \\"dns1\\": \\"8.8.8.8\\", \\"dns2\\": \\"0.0.0.0\\", \\"dhcpServer\\": \\"192.168.10.1\\", \\"leaseDuration\\": \\"360000\\"}", 
        "lastUpdateChecksum": "2132501716", 
        "dealerIconsCheckSum": "", 
        "remote_feature_support_version": "1", 
        "requestID": "f96b3774-4887-4d5a-8021-709927e3d0bd", 
        "responseTopic": "response_F2:16:3E:08:81:A7", 
        "remoteMacAddess": "F2:16:3E:08:81:A7"
}
```      
#### command syncdatabase
Panel sends full database (settings, events, devices, history, etc ...) over MQTT 
```json
{
        "eventName": "syncdatabase", 
        "requestID": "8bcd81f6-be01-4c01-8a73-9918366f7a48", 
        "responseTopic": "response_F2:16:3E:08:81:A7", 
        "remoteMacAddess": "F2:16:3E:08:81:A7"
}
```
#### command timeSync
Sync time between Panel and Plugin
```json
{
        "eventName":"timeSync",
        "startTimestamp":405682063,
        "requestID":"65d650bc-b459-41bf-a3fe-8edfd91cef29",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command pingevent
Keepalive command
```json
{
        "eventName":"pingevent",
        "macAddress":"F2:16:3E:08:81:A7",
        "remote_panel_status":"Active",
        "ipAddress":"192.168.10.214",
        "current_battery_status":"Normal",
        "remote_panel_battery_percentage":100,
        "remote_panel_battery_temperature":450,
        "remote_panel_battery_status":3,
        "remote_panel_battery_scale":100,
        "remote_panel_battery_voltage":4079,
        "remote_panel_battery_present":true,
        "remote_panel_battery_technology":"",
        "remote_panel_battery_level":100,
        "remote_panel_battery_health":2,
        "remote_panel_plugged":1,
        "requestID":"3c3103a9-6dfc-4944-a78b-2072a33216a0",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command pair_status_request
WIP - to be determined
```json
{
        "eventName": "pair_status_request", 
        "requestID": "d94aaeae-185b-4172-be04-6675637cd372", 
        "responseTopic": "response_F2:16:3E:08:81:A7", 
        "remoteMacAddess": "F2:16:3E:08:81:A7"
}
```
#### command execute_scene
```
{
        "eventName":"ipcCall",
        "ipcServiceName":"qinternalservice",
        "ipcInterfaceName":"android.os.IQInternalService",
        "ipcTransactionID":7,
        "ipcRequest":[{
                "dataType":"string",
                "dataValue":"{\\"operation_name\\":\\"execute_scene\\",\\"scene_id\\":1,\\"operation_source\\":1,\\"macAddress\\":\\"F2:16:3E:08:81:A7\\"}"
        }],
        "requestID":"894df3a9-eb1a-4ec2-9780-7f8fdc2a85a1",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command acStatus
`acStatus = Connected`
```json
{
        "eventName": "acStatus", 
        "acStatus": "Connected", 
        "requestID": "18404232-ed7f-43a6-add1-eb403f69182f", 
        "responseTopic": "response_F2:16:3E:08:81:A7", 
        "remoteMacAddess": "F2:16:3E:08:81:A7"
}
```
`acStatus = Disconnected`
```json
{
        "eventName":"acStatus",
        "macAddress":"F2:16:3E:08:81:A7",
        "acStatus":"Disconnected",
        "requestID":"8e85fe8f-7747-472b-92c5-dde01dc701b4",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command disconnect:
```json
{
        "eventName":"disconnect",
        "remoteClientID":"QolsysController",
        "remoteMac":"F2:16:3E:08:81:A7",
        "requestID":"disconnect"
}
```
#### command glassbreakservice
TBD
```json
{
        "eventName":"ipcCall",
        "ipcServiceName":"glassbreakservice",
        "ipcInterfaceName":"glassbreakservice",
        "ipcTransactionID":2,
        "requestID":"ff141b8a-8bd1-4b69-bcc5-11a5d6c2f604",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command disarmPhoto
```json
{
        "eventName":"disarmPhoto",
        "remoteDisarmPhoto":"encoded file data",
        "remoteDisarmPhotoName":"fd37207c-05b3-4afe-963b-d007895dbc47_1750369034.jpg",
        "macAddress":"F2:16:3E:08:81:A7",
        "remoteDisarmPhotoEntry":{"description":"$$ - $$##IQ Remote 1##Silent Police Emergency",
        "partition_id":"0",
        "uploaded":"False",
        "request_id":"fd37207c-05b3-4afe-963b-d007895dbc47",
        "file_type":"IMAGE",
        "name":"fd37207c-05b3-4afe-963b-d007895dbc47_1750369034.jpg",
        "_id":"71",
        "type":"ALARM",
        "user_id":"-1",
        "update_time":"1750369032109",
        "create_time":"1750369032109"},
        "requestID":"494d8b4c-3f1f-482a-bf0e-ea0fc2da5177",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```
#### command zwaveservice
```json
{
        "eventName":"ipcCall",
        "ipcServiceName":"zwaveservice",
        "ipcInterfaceName":"zwaveservice",
        "ipcTransactionID":28,
        "ipcRequest":[
                {"dataType":"int","dataValue":2},
                {"dataType":"int","dataValue":106},
                {"dataType":"int","dataValue":0},
                {"dataType":"int","dataValue":5},
                {"dataType":"byteArray","dataValue":[1,2,2,37,2]
        }],
        "requestID":"c3a1c5c1-3187-4db0-a97d-0d80ded9c058",
        "responseTopic":"response_F2:16:3E:08:81:A7",
        "remoteMacAddress":"F2:16:3E:08:81:A7"
}
```

