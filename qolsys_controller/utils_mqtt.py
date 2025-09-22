import logging
import random
import re

LOGGER = logging.getLogger(__name__)

def fix_json_string(json_string):
        def replace_escape(match):
            hex_value = match.group(1)
            decimal_value = int(hex_value, 16)
            return f"\\u{decimal_value:04x}"

        return re.sub(r"\\x([0-9a-fA-F]{2})", replace_escape, json_string)

def generate_random_mac() -> str:
        """Generate a random MAC address string with a fixed prefix."""
        mac = [ 0xf2, 0x16, 0x3e,
            random.randint(0x00, 0x7f),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff) ]
        return ":".join(map(lambda x: "%02x" % x, mac))
