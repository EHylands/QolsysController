import logging
import random

LOGGER = logging.getLogger(__name__)


def generate_random_mac() -> str:  # noqa: D103
    mac = [
        0xf2, 0x16, 0x3e,
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
    ]
    return ":".join(map(lambda x: "%02x" % x, mac))  # noqa: C417, UP031
