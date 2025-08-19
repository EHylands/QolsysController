import socket

from zeroconf import ServiceInfo
from zeroconf.asyncio import AsyncZeroconf


class QolsysMDNS:

    def __init__(self,ip: str, port: int) -> None:

        self.azc =  AsyncZeroconf()

        self.mdns_info  = ServiceInfo(
            "_http._tcp.local.",
            "NsdPairService._http._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=port,
        )

    async def start_mdns(self) -> None:
        await self.azc.async_register_service(self.mdns_info)

    async def stop_mdns(self) -> None:
        await self.azc.async_unregister_service(self.mdns_info)
