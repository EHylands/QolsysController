# qolsys-controller user guide

## How to run

Install the package and run the controller:
```
pip install qolsys-controller
qolsys-controller --verbose --config path_to_config_file
```

## Quick Start (Minimal Configuration)
Use this minimal configuration to get started quickly:
```json
{
  "panel_ip": "192.168.1.100",
  "config_dir": "/config",
  "auto_discover_pki": true,
  "start_pairing": true,
  "pairing_resume": true
}
```

Then run:
```
qolsys-controller --config /config/config.json
```
On first run, pairing will start automatically if required.

## Configuration File Options

### `panel_ip`
IP address or hostname of the IQ Panel.

### `plugin_ip`
Optional. If set, specifies the IP address the controller will bind to.
If set to an empty string (`""`), qolsys-controller will automatically detect the appropriate IP address

### `random_mac`:
Identifier used by qolsys-controller to name and distinguish PKI currently used.
If not set, a random value may be generated automatically.

### `config_dir`
Path to the qolsys-controller configuration directory.

### `auto_discover_pki`
If set to `true`, qolsys-controller will attempt to automatically locate and use a valid PKI directory within the configuration directory.

### `start_pairing`
Automatically starts the pairing process if the panel is not already paired.

To successfully pair, the following are required:

- A valid panel_ip
- A valid PKI directory containing:
  - Private key (`.key`)
  - Signed client certificate (`.secure`)
  - Qolsys public certificate (`.qolsys`)

### `pairing_resume`
If the pairing process fails, reuse the in-progress PKI directory for subsequent attempts.

### `check_user_code_on_arm`
Validate `user_code` before arming any partition

### `check_user_code_on_disarm`
Validate `user_code` before disarming any partition

### `log_mqtt_messages`
Log all MQTT traffic between the IQ Panel and qolsys-controller.
- **Warning**: IQ Panel versions >= 4.6.1 may become unstable when this option is enabled. Use with caution.

### `mqtt_bridge_enabled`
Enable the internal MQTT bridge.

### `mqtt_bridge_brooker_enabled`
Enable the internal MQTT bridge Brooker

### `mqtt_bridge_brooker_allowed_users`: 
Dictionary of allowed users for MQTT authentication. External clients will not be able to authenticate unless explicitly configured.

Keys: usernames
Values: SHA-512 hashed passwords

The `internal_user` account is automatically created for internal use by qolsys-controller.

Example:
```json
{
  "user1": "sha512-password1-hash",
  "user2": "$6$xAH93w/w$pdHHu/8r3uiUiazX1ukRDD4lymlwqBcg21PRaaK9jhpi/dmRq2oyd.O2TzFTN0uhwEi8USa5RSnZlkmU6qXgU/"
}
```

### `mqtt_bridge_port`
Port used by the internal MQTT broker.

### `mqtt_bridge_root_topic`
Root topic prefix used by the MQTT bridge.

### `mqtt_bridge_friendly_name`
Friendly name for the MQTT bridge.
- Defaults to the panel unique_id if set to an empty string ("").

### `mqtt_bridge_max_connections`
Maximum number of simultaneous connections allowed to the MQTT broker.

### `mqtt_bridge_tls_enabled`
Enable TLS for secure MQTT connections.

### Configuration File Example
``` json
{
  "panel_ip": "192.168.10.220",
  "plugin_ip": "",
  "panel_mac": "",
  "random_mac": "",
  "config_dir": "/config",

  "auto_discover_pki": true,
  "start_pairing": true,
  "pairing_resume": true,
  "check_user_code_on_arm": false,
  "check_user_code_on_disarm": false,
  "log_mqtt_messages": false,
  
  "mqtt_bridge_enabled": true,
  "mqtt_bridge_tls_enabled": true,
  "mqtt_bridge_brooker_allowed_users": {},
  "mqtt_bridge_max_connections": 5,
  "mqtt_bridge_root_topic": "qolsys",
  "mqtt_bridge_friendly_name": "iq_Panel",
  "mqtt_bridge_port": 8883
}
```