#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import ssl
from datetime import datetime, timezone
from typing import Any

import aiomqtt

from qolsys_controller.automation_zwave.device import QolsysAutomationDeviceZwave
from qolsys_controller.automation_zwave.service_meter import MeterServiceZwave
from qolsys_controller.commands.service import QolsysCommandService
from qolsys_controller.mqtt_command import (
    MQTTCommand,
)
from qolsys_controller.observable import Event
from qolsys_controller.pairing_server import QolsysPairingServer

from .enum_qolsys import (
    VALID_CONTROLLER_TRANSITIONS,
    ControllerState,
    QolsysNotification,
)
from .errors import (
    InvalidControllerStateTransitionError,
    QolsysConfigError,
    QolsysMqttError,
    QolsysSslError,
)
from .mqtt_bridge.bridge import MqttBridge
from .mqtt_command_queue import QolsysMqttCommandQueue
from .panel import QolsysPanel
from .pki import QolsysPKI
from .settings import QolsysSettings
from .state import QolsysState
from .utils_mqtt import generate_random_mac

LOGGER = logging.getLogger(__name__)


class QolsysController:
    def __init__(self) -> None:
        self._state = QolsysState(self)
        self._settings = QolsysSettings(self)
        self._panel = QolsysPanel(self)
        self._pki = QolsysPKI(settings=self.settings)
        self.commands = QolsysCommandService(self)

        self._controller_state = ControllerState.STOPPED
        self._controller_state_condition = asyncio.Condition()

        self._initial_run: bool = True
        self._is_configured: bool = False
        self._shutdown_requested: bool = False

        self._task_supervisor: asyncio.Task[None] | None = None
        self._pairing_was_started: bool = False

        # Plugin
        self._mqtt_command_queue = QolsysMqttCommandQueue()
        self._zone_id: str = "1"
        self._pairing_server: QolsysPairingServer | None = None

        # MQTT Panel Client
        self._reconnect_attempt: int = 0
        self._mqtt_publish_queue: asyncio.Queue[MQTTCommand] = asyncio.Queue()

        # MQTT Bridge
        self._mqtt_bridge: MqttBridge | None = None

    @property
    def state(self) -> QolsysState:
        return self._state

    @property
    def panel(self) -> QolsysPanel:
        return self._panel

    @property
    def settings(self) -> QolsysSettings:
        return self._settings

    @property
    def mqtt_command_queue(self) -> QolsysMqttCommandQueue:
        return self._mqtt_command_queue

    ###########################################################################
    # Controller Operations
    ###########################################################################

    async def start_operation(self, reconnect: bool = True, run_once: bool = False, start_pairing: bool = False) -> None:
        LOGGER.debug("Starting Qolsys Controller Operation")
        self._shutdown_requested = False
        self._task_supervisor = asyncio.create_task(
            self.run_supervised(reconnect=reconnect, run_once=run_once, start_pairing=start_pairing),
            name="MQTT Panel Client Supervisor",
        )

        wait_task = asyncio.create_task(self.wait_until_connected(), name="MQTT Panel Client Initial Connection Wait")
        done, _ = await asyncio.wait(
            [wait_task, self._task_supervisor],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # supervisor exited first -> propagate exception
        if self._task_supervisor in done:
            wait_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await wait_task
            await self._task_supervisor

        # Start MQTT Bridge Broker
        await self.start_mqtt_bridge()

        LOGGER.info("Qolsys Controller Ready for Operation")

    async def stop_operation(self) -> None:
        await self.set_controller_state(ControllerState.SHUTTING_DOWN)
        self._shutdown_requested = True

        if self._pairing_server is not None:
            await self._pairing_server.stop()
            self._pairing_server = None

        if self._task_supervisor is not None and not self._task_supervisor.done():
            self._task_supervisor.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task_supervisor

        if self._mqtt_bridge is not None:
            await self._mqtt_bridge.shutdown()

        await self.set_controller_state(ControllerState.STOPPED)
        self.notify_panel_status_update()

    async def config_task(self, start_pairing: bool) -> None:
        await self.set_controller_state(ControllerState.CONFIGURING)

        # Check and created config_directory
        self.settings.check_config_directory(create=start_pairing)

        # Read user file for access codes
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.panel.read_users_file)

        # Config PKI
        if self.settings.auto_discover_pki:
            if self._pki.auto_discover_pki():
                self.settings.random_mac = self._pki.formatted_id()
        else:
            self._pki.set_id(self.settings.random_mac)

        # Check if plugin is paired
        if await self.is_paired():
            LOGGER.debug("Panel is Paired")

        else:
            LOGGER.debug("Panel not paired")

            if not start_pairing:
                LOGGER.debug("Aborting pairing.")
                raise QolsysConfigError("Panel not paired and start_pairing=False")

            await self.start_initial_pairing()

        # Set mqtt_remote_client_id
        self.settings.mqtt_remote_client_id = "qolsys-controller-" + self._pki.formatted_id()
        LOGGER.debug("MQTT Panel Client - Using remoteClientID: %s", self.settings.mqtt_remote_client_id)

        # Everything is configured
        self._is_configured = True
        return

    async def is_paired(self) -> bool:
        return (
            self._pki.id != ""
            and await self._pki.check_key_file()
            and await self._pki.check_cer_file()
            and await self._pki.check_qolsys_cer_file()
            and await self._pki.check_secure_file()
            and self.settings.check_panel_ip()
            and self.settings.check_plugin_ip()
        )

    ###########################################################################
    # MQTT Panel Client
    ###########################################################################

    async def run_supervised(self, reconnect: bool = True, run_once: bool = False, start_pairing: bool = False) -> None:
        while not self._shutdown_requested:
            try:
                # Fresh outbound queue per connection attempt so stale commands
                # from a previous session don't get sent on reconnect.
                self._mqtt_publish_queue = asyncio.Queue()

                # Configure controller
                if not self._is_configured:
                    await self.config_task(start_pairing)

                # Open transport
                await self.set_controller_state(ControllerState.CONNECTING)
                mqtt_panel_client: aiomqtt.Client = await self.mqtt_open_transport_task()

                async with mqtt_panel_client:
                    await mqtt_panel_client.subscribe("iq2meid")
                    await mqtt_panel_client.subscribe("response_" + self.settings.random_mac, qos=self.settings.mqtt_qos)
                    await mqtt_panel_client.subscribe("ZWAVE_RESPONSE", qos=self.settings.mqtt_qos)

                    if self.settings.log_mqtt_messages:
                        await mqtt_panel_client.subscribe("mastermeid", qos=self.settings.mqtt_qos)

                    # Managed Background Tasks
                    async with asyncio.TaskGroup() as tg:
                        tg.create_task(self.mqtt_listen_task(mqtt_panel_client))
                        tg.create_task(self.mqtt_publish_task(mqtt_panel_client))

                        await asyncio.sleep(
                            2
                        )  # Short delay to ensure listen and publish tasks are running before initializing session

                        # Initialize session before background loops
                        await self.mqtt_initialize_session_task()
                        await self.set_controller_state(ControllerState.CONNECTED)
                        self.notify_panel_status_update()
                        self._reconnect_attempt = 0

                        if run_once:
                            LOGGER.debug("MQTT Panel Client - Exiting after initialization (run_once=True)")
                            self._shutdown_requested = True
                            return

                        tg.create_task(self.mqtt_ping_task(mqtt_panel_client))
                        tg.create_task(self.mqtt_zwave_meter_update())

            except* asyncio.CancelledError:
                raise

            except* QolsysConfigError as err:
                self._shutdown_requested = True
                LOGGER.exception("MQTT Panel Client - Supervisor detected configuration error: %s", err)
                raise

            except* aiomqtt.exceptions.MqttError as err:
                for exc in err.exceptions:
                    LOGGER.debug("MQTT Panel Client - Supervisor detected MQTT Error: %r", exc)

                if not reconnect:
                    raise QolsysMqttError from err

            except* ssl.SSLError as err:
                # SSL error is and authentication error with invalid certificates en pki
                # We cannot recover from this error automaticly
                LOGGER.debug("MQTT Panel Client - Supervisor detected SSL Error: %s", err)
                self._shutdown_requested = True
                raise QolsysSslError from err

            except* Exception as err:
                for exc in err.exceptions:  # type: ignore[assignment]
                    LOGGER.exception("MQTT Panel Client - Supervisor detected failure: %r", exc)
                raise

            finally:
                self.mqtt_command_queue.fail_all_pending(QolsysMqttError("MQTT Command failed due to disconnection"))
                self.notify_panel_status_update()

                if reconnect and not self._shutdown_requested and self.controller_state != ControllerState.SHUTTING_DOWN:
                    MAX_RECONNECT_DELAY = 300
                    delay = min(1 * (2**self._reconnect_attempt), MAX_RECONNECT_DELAY)
                    self._reconnect_attempt += 1

                    await self.set_controller_state(ControllerState.RECONNECTING)
                    LOGGER.debug(
                        "MQTT Panel Client - Reconnecting in %s seconds (attempt %d)",
                        delay,
                        self._reconnect_attempt,
                    )
                    await asyncio.sleep(delay)

    async def mqtt_open_transport_task(self) -> aiomqtt.Client:
        # Configure TLS context for MQTT connection
        def create_tls_context() -> ssl.SSLContext:
            ctx = ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH,
                cafile=str(self._pki.qolsys_cer_file_path),
            )
            ctx.set_ciphers("DEFAULT:@SECLEVEL=0")
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ctx.load_cert_chain(
                certfile=str(self._pki.secure_file_path),
                keyfile=str(self._pki.key_file_path),
            )
            return ctx

        loop = asyncio.get_running_loop()
        ctx = await loop.run_in_executor(None, create_tls_context)

        return aiomqtt.Client(
            hostname=self.settings.panel_ip,
            port=8883,
            tls_context=ctx,
            tls_insecure=True,
            clean_session=True,
            keepalive=self.settings.mqtt_timeout,
            identifier=self.settings.mqtt_remote_client_id,
        )

    def enqueue_mqtt_command(self, command: MQTTCommand) -> None:
        self._mqtt_publish_queue.put_nowait(command)

    async def mqtt_publish_task(self, client: aiomqtt.Client) -> None:
        LOGGER.debug("MQTT Panel Client - Publish task started")

        command: MQTTCommand | None = None
        while not self._shutdown_requested:
            try:
                command = await self._mqtt_publish_queue.get()
                payload = json.dumps(command._payload)
                await client.publish(command._topic, payload, command._qos)

            except asyncio.CancelledError:
                raise

            except aiomqtt.MqttError:
                if command is not None:
                    LOGGER.exception("MQTT Panel Client - error while publishing command %s", command._eventName)
                    self.mqtt_command_queue.fail_waiter(command._requestID, QolsysMqttError("Failed to publish MQTT command"))
                raise

            except Exception as err:
                LOGGER.exception("MQTT Panel Client - publish task error: %s", err)
                if command is not None:
                    self._mqtt_command_queue.fail_waiter(command._requestID, err)
                raise

    async def mqtt_listen_task(self, client: aiomqtt.Client) -> None:
        LOGGER.debug("MQTT Panel Client - Listen task started")

        async for message in client.messages:
            if self._shutdown_requested:
                break

            # Log all MQTT messages for debug purposes if enabled in settings
            if self.settings.log_mqtt_messages:
                if isinstance(message.payload, bytes):
                    try:
                        LOGGER.debug("MQTT TOPIC: %s\n%s", message.topic, message.payload.decode())
                    except json.JSONDecodeError:
                        LOGGER.warning("Invalid JSON payload on topic %s", message.topic)
                        continue

            # Panel response to MQTT Commands and Panel Commands to IQ Remote
            if message.topic.matches("response_" + self.settings.random_mac):  # noqa: SIM102
                if isinstance(message.payload, bytes):
                    try:
                        data = json.loads(message.payload.decode())
                        await self._mqtt_command_queue.handle_response(data)
                    except json.JSONDecodeError:
                        LOGGER.warning("Invalid JSON payload on topic %s", message.topic)
                        continue

            # Panel updates to IQ2MEID database
            if message.topic.matches("iq2meid"):  # noqa: SIM102
                if isinstance(message.payload, bytes):
                    try:
                        data = json.loads(message.payload.decode())
                        self.panel.parse_iq2meid_message(data)
                    except json.JSONDecodeError:
                        LOGGER.warning("Invalid JSON payload on topic %s", message.topic)
                        continue

            # Panel Z-Wave response
            if message.topic.matches("ZWAVE_RESPONSE"):  # noqa: SIM102
                if isinstance(message.payload, bytes):
                    try:
                        data = json.loads(message.payload.decode())
                        self.panel.parse_zwave_message(data)
                    except json.JSONDecodeError:
                        LOGGER.warning("Invalid JSON payload on topic %s", message.topic)
                        continue

    async def mqtt_initialize_session_task(self) -> None:
        LOGGER.debug("MQTT Panel Client - Initializing session")
        response_connect = await self.commands.panel.connect()
        self.panel.imei = response_connect.get("master_imei", "")
        self.panel.product_type = response_connect.get("primary_product_type", "")

        await self.commands.panel.pingevent()
        await self.commands.panel.pair_status_request()

        response_database = await self.commands.panel.sync_database()
        await self.panel.load_database(response_database.get("fulldbdata"))

        if self._pairing_was_started:
            LOGGER.debug("Plugin Pairing Completed ")
            await self._pki.pairing_resume_pki_set(False)

        if self._initial_run:
            self._initial_run = False
            self.panel.dump()
            self.state.dump()

    async def mqtt_ping_task(self, client: aiomqtt.Client) -> None:
        LOGGER.debug("MQTT Panel Client - Ping task started")
        while not self._shutdown_requested:
            try:
                if self.controller_state == ControllerState.CONNECTED:
                    await self.commands.panel.pingevent()
                await asyncio.sleep(self.settings.mqtt_ping)

            except asyncio.CancelledError:
                raise

            except Exception as err:
                LOGGER.exception("MQTT Panel Client - error in ping task: %s", err)
                raise

    async def mqtt_zwave_meter_update(self) -> None:
        LOGGER.debug("MQTT Panel Client - Z-Wave meter update task started")
        while not self._shutdown_requested:
            if self.controller_state == ControllerState.CONNECTED:
                for autdev in self.state.automation_devices:
                    if self._shutdown_requested:
                        return

                    if not isinstance(autdev, QolsysAutomationDeviceZwave):
                        continue

                    if not autdev._FIX_MULTICHANNEL_METER_ENDPOINT:
                        continue

                    for service in autdev.service_get_protocol(MeterServiceZwave):
                        if isinstance(service, MeterServiceZwave):
                            await service.refresh_meter_zwave()
                            await asyncio.sleep(5)

            await asyncio.sleep(300)

    ###########################################################################
    # MQTT Bridge
    ###########################################################################

    async def start_mqtt_bridge(self) -> None:
        # Start MQTT Bridge if enabled
        LOGGER.debug("MQTT Bridge Enabled: %s", self.settings.mqtt_bridge_enabled)
        if self.settings.mqtt_bridge_enabled:
            # Create MQTT Bridge if not already created
            if not self._mqtt_bridge:
                self._mqtt_bridge = MqttBridge(self)

            # Start MQTT Bridge
            if not await self._mqtt_bridge.start():
                LOGGER.error("MQTT Bridge failed to start")
                await self.stop_operation()
                return

    def _to_event_dict(self) -> dict[str, Any]:
        return {
            "connected": self.controller_state == ControllerState.CONNECTED,
            "panel_ip": self.settings.panel_ip,
            "unique_id": self.panel.unique_id,
            "plugin_ip": self.settings.plugin_ip,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

    def notify_panel_status_update(self) -> None:
        self.state.notify(Event(QolsysNotification.PANEL_STATUS_UPDATE, self.panel, self._to_event_dict()))

    async def start_initial_pairing(self) -> None:
        self._pairing_was_started = True
        # check if random_mac has been configured
        if self.settings.random_mac == "":
            # If pairing_resume is enabled, look for existing PKI folders to resume pairing process with previous random_mac
            resume_pki_id = await self._pki.pairing_resume_get_in_progress_pki()
            if self.settings.pairing_resume and resume_pki_id:
                self.settings.random_mac = resume_pki_id

            else:
                LOGGER.debug("Creating random_mac")
                self.settings.random_mac = generate_random_mac()
                await self._pki.create(self.settings.random_mac, key_size=self.settings.key_size)
                await self._pki.pairing_resume_pki_set(True)

        # Check if PKI is valid
        self._pki.set_id(self.settings.random_mac)
        LOGGER.debug("Checking PKI")
        if not (await self._pki.check_key_file() and await self._pki.check_cer_file() and await self._pki.check_csr_file()):
            raise QolsysConfigError("PKI files not found or invalid")

        LOGGER.debug("Starting Pairing Process")

        if not self.settings.check_plugin_ip():
            raise QolsysConfigError("Plugin IP Address not configured")

        # If we dont allready have client signed certificate, start the pairing server
        if (
            not await self._pki.check_secure_file()
            or not await self._pki.check_qolsys_cer_file()
            or not self.settings.check_panel_ip()
        ):
            self._pairing_server = QolsysPairingServer(self.settings, self._pki)
            await self._pairing_server.start()
            await self._pairing_server.wait_until_paired()
            await self._pairing_server.stop()
            self._pairing_server = None

        LOGGER.debug("Sending MQTT Pairing Request to Panel")

        # We have client signed certificate at this point
        # Connect to Panel MQTT to send pairing command

    @property
    def controller_state(self) -> ControllerState:
        return self._controller_state

    async def set_controller_state(self, new_state: ControllerState) -> None:
        async with self._controller_state_condition:
            if new_state not in VALID_CONTROLLER_TRANSITIONS[self._controller_state]:
                raise InvalidControllerStateTransitionError(f"{self._controller_state.name} -> {new_state.name}")

            LOGGER.debug("Controller State: %s -> %s", self._controller_state.name, new_state.name)

            self._controller_state = new_state
            self._controller_state_condition.notify_all()

    async def wait_until_connected(self) -> None:
        async with self._controller_state_condition:
            await self._controller_state_condition.wait_for(lambda: self._controller_state == ControllerState.CONNECTED)
