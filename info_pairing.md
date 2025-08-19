## QolsysController Pairing Process
- `plugin`: Python Plugin
- `plugin_ip`: Plugin IP Address
- `plugin_pairing_port`: Random high level port number used by certificates exchange server
- `random_mac`: random MAC Address used by plugin as a random identifier
- `panel`: Qolsys Panel
- `panel_ip`: Qolsys Panel IP Address
- `panel_mac`: Qolsys Panel MAC address

### Step 1 - QolsysController obtains a signed client certificate from the Panel
- Plugin generates a **2048-bit RSA private key** (`.key`)
- Plugin Creates a **Certificate** (`.cer`)
- Plugin Creates a **Certificate Signing Request (CSR)** (`.csr`)
- plugin publishes the following mDNS information:

```
(
   "_http._tcp.local.",
   "NsdPairService._http._tcp.local.",
   addresses=['plugin_ip'],
   port='plugin_pairing_port',
)
```

- QolsysController starts a KeyExchangeServer (TLS Socket) listenning on `plugin_ip`:`plugin_pairing_port`

On Panel, go to IQ Remote pairing config page:

`Settings` -> `Advanced Settings` -> (enter Installer or Dealer Code) -> `Wifi devices` -> `IQ Remote` -> `Pair`

- panel will automatically connect to `plugin_ip`:`plugin_pairing_port`
- panel sends `0x000x11` + `panel_mac`
- plugin sends `0x000x11` + `random_mac`
- plugin sends CSR file content
- plugin sends `sent`
- panel sends SECURE (signed client certificate) file content
- panel sends `sent`
- panel sends Qolsys Public certificate file content
- panel sends `sent`
- plugin saves SECURE file
- plugin saves Qolsys Public certificate file
- plugin stops mDNS discovery
- plugin stops KeyExchangeServer

### Step 2 - QolsysController connects to Panel MQTT Server
- The plugin connects securely to the Qolsys Panel at `panel_ip` using **TLS 1.2**.
- The plugin authenticates using its private key and signed client certificate.

After connecting, the plugin subscribes to these MQTT topics:
| Topic                 | Description                          |
|-----------------------|------------------------------------|
| `mastermeid`          | Command channel                    |
| `response_random_mac` | Command response channel  |
| `PanelEvent`          | Status updates (partitions, zones, alarms) |


Plugin completes pairing process by sending a MQTT `pairing_request` command

Plugin marks the pairing process as completed