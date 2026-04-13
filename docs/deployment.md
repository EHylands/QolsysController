# Deployment Guide

## Install

```bash
sudo mkdir -p /opt/qolsys
sudo chown $USER /opt/qolsys
cd /opt/qolsys

# uv (with MQTT bridge)
uv venv
uv pip install "qolsys-controller[bridge]"

# --- or ---

# pip (with MQTT bridge)
python3 -m venv .venv
.venv/bin/pip install "qolsys-controller[bridge]"
```

To install without the embedded MQTT broker (e.g. for Home Assistant):

```bash
pip install qolsys-controller
```

Both create a `.venv/` directory with the `qolsys-controller` CLI inside it.

## Configure

```bash
mkdir -p config
cp /path/to/QolsysController/config/config.json config/
# Edit config/config.json with your panel IP, bridge settings, etc.
```

## First-Time Pairing

```bash
.venv/bin/qolsys-controller --config /opt/qolsys/config/config.json
```

> The bridge must be on the same subnet as the panel for mDNS discovery
> during pairing. After pairing, PKI certificates are stored in
> `config/pki/` and subnet no longer matters.

## systemd Service

Create a dedicated service user:

```bash
sudo useradd -r -s /usr/sbin/nologin -d /opt/qolsys qolsys
sudo chown -R qolsys:qolsys /opt/qolsys
```

Install and enable:

```bash
sudo cp qolsys-controller.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now qolsys-controller
journalctl -u qolsys-controller -f
```

> Edit `User`, `WorkingDirectory`, `ExecStart`, and `ReadWritePaths`
> in the service file if your layout differs from `/opt/qolsys`.

## Resilience

- **Panel disconnects/reboots:** auto-reconnect with backoff
- **systemd restart:** on-failure with 10 s delay
- **Security hardening:** `ProtectSystem=strict`, `NoNewPrivileges=true`, `PrivateTmp=true`
