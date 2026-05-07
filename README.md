# Qolsys Controller

[![Build](https://github.com/EHylands/QolsysController/actions/workflows/tags.yml/badge.svg)](https://github.com/EHylands/QolsysController/actions/workflows/tags.yml)


A Python module that emulates a virtual IQ Remote device, enabling full **local control** of a Qolsys IQ Panel over MQTT.

## QolsysController
- ✅ Connects directly to the **Qolsys IQ Panel's local MQTT interface as an IQ Remote**
- 🔐 Pairs by only using **Installer Code** (same procedure as standard IQ Remote pairing)
- 🔢 Supports **4-digit user codes**
- ⚠️ Uses a **custom local usercode database** (panel internal validation is not yet supported)
- 🌐 Now includes a built-in MQTT Bridge - [**MQTT Bridge**](./docs/info_mqtt_bridge.md), enabling seamless publishing of panel updates and handling of incoming commands

## 📦 Installation

Please check [**Advanced instructions**](./docs/info_qolsys_controller.md)

```bash
pip install qolsys-controller
qolsys-controller --verbose --config 'path_to_config_file'
```

## Functionality Highlights

| Category               | Feature                              | Status |
|------------------------|--------------------------------------|--------|
| **Panel**              | Diagnostic Sensors                   | ✅     |
|                        | Panel Scenes                         | ✅     |
|                        | Speak Command                        | ✅     |
|                        | Weather Forecast                     | ✅     |
| **Partition**          | Arming Status and Alarm State        | ✅     |
|                        | Home Instant Arming                  | ✅     |
|                        | Home Silent Disarming (Firmware 4.6.1)| ✅     |
|                        | Set Exit Sounds and Entry Delay      | ✅     |
| **Zones**              | Sensor Status                        | ✅     |
|                        | Tamper State                         | ✅     |
|                        | Battery Level                        | ✅     |
|                        | Temperature (supported PowerG device)| ✅     |
|                        | Light (supported PowerG device)      | ✅     |
|                        | Average and Latest dBm               | ✅     |


| Automation Devices| Z-Wave | PowerG | Zigbee | Alarm.com |
|-----------------|--------|--------|-------|-------|
| Door Lock        | ✅     | ✅     | ✅    | ❌    |
| Energy Clamp     | ✅     | ❌     | ❌    | ❌    |
| External Siren   | ✅     | ❌     | ❌    | ❌    |
| Garage Door      | ✅     | ❌     | ❌    | ✅    |
| Light            | ✅     | ✅     | ✅    | ✅    |
| Smart Outlet     | 🛠️     | ❌     | ❌    | ❌    |
| Thermometer      | ✅     | ❌     | ❌    | ❌    |
| Thermostat       | ✅     | ❌     | ❌    | ❌    |
| Water Valve      | 🛠️     | ❌     | ❌    | ❌    |

🛠️ = partially supported or untested

## ⚠️ Certificate Warning

During pairing, the main panel issues **only one signed client certificate** per virtual IQ Remote. If any key files are lost or deleted, re-pairing may become impossible. 

A new PKI, including a new private key, can be recreated under specific circumstances, though the precise conditions remain unknown at this time.

**Important:**  
Immediately back up the following files from the `pki/` directory after initial pairing:

- `.key` (private key)
- `.cer` (certificate)
- `.csr` (certificate signing request)
- `.secure` (signed client certificate)
- `.qolsys` (Qolsys Panel public certificate)

Store these files securely.
