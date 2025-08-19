## Qolsys IQ Remote and Qolsys inner component
The Qolsys Main Panel maintains its internal state using an Android ContentProvider-based database.  When an IQ Remote is paired with the main panel, it downloads a full copy of the main panel’s database. Subsequent updates are sent from the main panel to the remote via MQTT messages on the `iq2meid` topic.

Databases Created on IQ Remote.
Each of these corresponds to a ContentProvider managing a specific domain:


| Provider Name             | Description                  |
|--------------------------|------------------------------|
| `PartitionContentProvider` | Partition info               |
| `SensorProvider`           | Sensors and their state      |
| `SettingsProvider`         | User/system settings         |
| `StateProvider`            | Current state of the system  |
| `HistoryProvider`          | Logs of past events          |
| `DimmerLightProvider`      | Smart dimmer lights          |
| `SmartOutletProvider`      | Smart plugs/outlets          |
| `ThermostateProvider`      | Thermostat control           |
| `ZwaveConteProvider`       | Z-Wave device info           |


### Qolsys Partition
Each partition contains the following data:

| Field          | Description |
|----------------|-------------|
| `name`         | Name of the partition  |
| `system_status`| `DISARM`, `ARM-STAY`, `ARM-AWAY`,`ARM-AWAY-EXIT-DELAY`,`ARM-STAY-EXIT-DELAY` |
| `alarm_state`  | `None`, `Delay`, or `Alarm` |
| `alarm_type`   | `Police Emergency`,`Fire Emergency`,`Auxiliary Emergency`,`Silent Auxiliary Emergency`,`Silent Police Emergency`|
| `exit_sounds`  | `ON` or `OFF` – Beeping sounds during exit delay |
| `entry_delays` | `ON` or `OFF` – Delay before alarm triggers when entering |

### Qolsys Zone
Each zone contains the following data:
| Field          | Description |
|----------------|-------------|
| `sensorsstatus`| `Open`, `Closed`, `Active`, `Inactive`,`Activated`,`Idle`,`Unreachable`,`Tampered`,`Synchonizing`|
| `group`        |              |
| `battery_level`|              | 
| `partition_id `|              | 
| `latestdBm`|              | 
| `averagedBm`|              | 
| `time`|              | 
| `zone_type`|              | 