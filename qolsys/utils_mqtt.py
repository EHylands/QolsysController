import random
import logging

LOGGER = logging.getLogger(__name__)


def fix_json_string(json_string):
        def replace_escape(match):
            hex_value = match.group(1)
            decimal_value = int(hex_value, 16)
            return f'\\u{decimal_value:04x}'
    
        import re
        return re.sub(r'\\x([0-9a-fA-F]{2})', replace_escape, json_string)

def generate_random_mac():
        mac = [ 0xf2, 0x16, 0x3e,
            random.randint(0x00, 0x7f),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff) ]
        return ':'.join(map(lambda x: "%02x" % x, mac))

def mqtt_arming_status_to_C4(state:str):

        match state:
          
                case 'Disarmed':
                        return 'DISARM'
                
                case 'Arm-Stay':
                        return 'ARM_STAY'
                
                case 'Arm-Away':
                        return 'ARM_AWAY'
                
                case 'Triggered Alarm':
                        return 'ALARM'

                case _:
                        LOGGER.warning(f'Unknow MQTT Arming Status')

def c4_arming_status_to_mqtt(state:str):

        match state:
          
                case 'DISARM':
                        return 'Disarmed'
                
                case 'ARM_STAY':
                        return 'ARM-STAY'
                
                case 'ARM_AWAY':
                        return 'ARM-AWAY'
                
                case 'ALARM':
                        return 'Triggered Alarm'
                
                case 'EXIT_DELAY':
                        return 'ARM-AWAY'

                case _:
                        print(state)
                        LOGGER.warning(f'Unknow C4 Arming Status')

