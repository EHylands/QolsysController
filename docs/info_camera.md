# Local panel camera snapshots

`controller.commands.camera` supports an explicit, request-driven still capture
and downloading a known saved JPEG. The protocol was verified on IQ Panel 2+
firmware 2.8.1. Other panels and firmware versions still need hardware testing.

```python
snapshot = await controller.commands.camera.capture_snapshot()
jpeg_bytes = snapshot.jpeg
```

Run this against an already connected controller. Each call creates one Peek-In
photo and its request record, downloads the JPEG, then removes that exact file
and metadata row with readback verification. It does not change arming, camera
settings, or enable continuous recording. The local-only request uses firmware
2.8.1's `user_id=-2` sentinel, which suppresses forwarding that picture to ADC.
The controller follows the callback's filename, so panel and client clocks do
not need to match. Concurrent calls through the same command service serialize
camera access. Use `capture_snapshot(retain_on_panel=True)` to deliberately
retain the panel copy.

The `timeout` bounds capture and download. Cleanup runs after it, so a slow
cleanup never discards an image that was already downloaded. If cleanup fails,
the image is still returned with `retained_on_panel=True`. A failed capture
raises `QolsysSnapshotError`, whose `request_id` identifies the panel request.
Either way, remove the leftover file and record later with:

```python
await controller.commands.camera.cleanup_snapshot(request_id)
```

`cleanup_snapshot` only matches records created by `capture_snapshot`. It leaves
a capture the panel has not finished yet, so retry after it completes.

Every snapshot is a database insert, a native still, a flash write and a delete
on the panel. Callers that refresh automatically, such as camera dashboards,
should cache images and limit captures to one every 30 to 60 seconds.

Downloading an existing photo does not initiate capture:

```python
from qolsys_controller.commands.camera import PhotoDirectory

jpeg_bytes = await controller.commands.camera.download_photo(PhotoDirectory.DISARM, "known-existing-photo.jpg")
```

The IQ2 named-file removal API only exposes the alarm-photo and alarm-video
directories. Cleanup uses the fixed `../PeekInPhotos/` relative prefix from the
alarm-photo root, followed by the internally generated UUID/timestamp filename.
Callers cannot supply a cleanup path. It never synchronizes a whole directory
or deletes existing alarm photos. Metadata deletion alone would leave the image
file behind, so cleanup verifies file disappearance before removing its record.

Camera-only consumers can use `controller.pki` to access the same pairing
identity used by the controller's native transport. Preserve its signed files
and identity across restarts; do not regenerate them during connection retries.

Video is not part of this API. The panel's named-file download returns a whole
file per request with no byte range, so a growing recording cannot be streamed
continuously through it.
