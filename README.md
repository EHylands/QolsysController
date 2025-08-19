# QolsysController

A Python module that emulates a virtual IQ Remote device, enabling full **local control** of a Qolsys IQ Panel over MQTT — no cloud access required.

## QolsysController
- ✅ Connects directly to the **Qolsys Panel's local MQTT server as an IQ Remote**
- 🔐 Pairs by only using **Installer Code** (same procedure as standard IQ Remote pairing)
- 🔢 Supports **4-digit user codes**
- ⚠️ Uses a **custom local usercode database** — panel's internal user code verification process is not yet supported

### Supported Features Milestones

| Device               | Feature                          | Status        |
|----------------------|----------------------------------|---------------|
| **Panel**            | Diagnostics sensors              | ✅ Supported  |
|----------------------|----------------------------------|---------------|
| **Partitions**       | Arming status                    | ✅ Supported |
|                      | Set Exit sounds                  | ✅ Supported            |
|                      | Home Instant arming              | ✅ Supported            |
|                      | Alarm state and type             | ✅ Supported            |
|----------------------|----------------------------------|---------------|
| **Zones**            | Sensor Status                    | ✅ Supported            |
|                      | Tamper State                     | ✅Supported             |
|                      | Battery Level                    | ✅ Supported            |
|                      | Signal Level                     | ✅ Supported            |
|----------------------|----------------------------------|---------------|
| **Dimmers**           | Read Light Status and Level      | ✅ Supported            |
|                      | Set Lights Status and Level       | ✅  Supported           |
|----------------------|----------------------------------|---------------|
| **Door Locks**        | Read Lock State                  | ✅ Supported            |
|                      | Set Lock State                   | 🛠️ WIP        |
|----------------------|----------------------------------|---------------|
| **Thermostats**       | Read Thermostat State            | ✅ Supported            |
|                      | Set  Thermostat State            | 🛠️ WIP        |
|----------------------|----------------------------------|---------------|
| **Garage Doors**      | All                              | 🛠️ WIP        |
|----------------------|----------------------------------|---------------|
| **Outlets**           | All                              | 🛠️ WIP        |
|----------------------|----------------------------------|---------------|
| **Generic Z-Wave**   | Read Battery Level               | ✅ Supported |
|                      | Read Pairing Status              | ✅ Supported |
|                      | Read Pairing Status              | ✅ Supported |
|                      | Control Generic Z-Wave Devices   | 🔄 TBD       |


## ⚠️ Certificate Warning

During pairing, the main panel issues **only one signed client certificate** per virtual IQ Remote. If any key files are lost or deleted, re-pairing may become impossible.

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
python3.12 main.py
```
