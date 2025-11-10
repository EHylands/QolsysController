# Qolsys Controller - qolsys-controller

[![Build](https://github.com/EHylands/QolsysController/actions/workflows/build.yml/badge.svg)](https://github.com/EHylands/QolsysController/actions/workflows/build.yml)

A Python module that emulates a virtual IQ Remote device, enabling full **local control** of a Qolsys IQ Panel over MQTT — no cloud access required.

## QolsysController
- ✅ Connects directly to the **Qolsys Panel's local MQTT server as an IQ Remote**
- 🔐 Pairs by only using **Installer Code** (same procedure as standard IQ Remote pairing)
- 🔢 Supports **4-digit user codes**
- ⚠️ Uses a **custom local usercode database** — panel's internal user code verification process is not yet supported

## ✨ Functionality Highlights

| Category               | Feature                              | Status |
|------------------------|--------------------------------------|--------|
| **Panel**              | Diagnostic Sensors                   | ✅     |
|                        | Panel Scenes                         | ✅     |
|                        | Weather Forecast                     | ✅     |
|                        | (Alarm.com Weather to Panel)         |        |
| **Partition**          | Arming Status                        | ✅     |
|                        | Alarm State                          | ✅     |
|                        | Home Instant Arming                  | ✅     |
|                        | Home Silent Disarming (Firmware 4.6.1)| ✅     |
|                        | Set Exit Sounds                      | ✅     |
|                        | Set Entry Delay                      | ✅            |
|                        | Disarm Photos                        | 🛠️     |
|                        | TTS                                  | 🛠️     |
| **Zones**              | Sensor Status                        | ✅     |
|                        | Tamper State                         | ✅     |
|                        | Battery Level                        | ✅     |
|                        | Temperature (supported PowerG device)| ✅     |
|                        | Light (supported PowerG device)      | ✅     |
|                        | Average dBm                          | ✅     |
|                        | Latest dBm                           | ✅     |
| **Z-Wave Devices**     | Battery Level                        | ✅     |
|                        | Node Status                          | ✅     |
|                        | Control Generic Devices              | TBD    |
| **Z-Wave Dimmers**     | Light Status and Level Control       | ✅     |
| **Z-Wave Door Locks**  | Lock, Unlock                         | ✅     |
| **Z-Wave Thermostats** | Read device status                   | ✅     |
|                        | Write device status                  | ✅     |
| **Z-Wave Garage Doors**|                                      | 🛠️     |
| **Z-Wave Outlets**     |                                      | 🛠️     |


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

## 📦 Installation

```bash
git clone https://github.com/EHylands/QolsysController.git
cd qolsys_controller
pip3.12 install -r requirements.txt

# Change panel_ip and plugin_in in main.py file
python3.12 example.py
```
