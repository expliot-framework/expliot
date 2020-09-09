"""Support for interacting with Modbus over TCP."""
MODBUS_REFERENCE = [
    "https://en.wikipedia.org/wiki/Modbus",
    "http://www.modbus.org/specs.php",
]

MODBUS_PORT = 502
DEFAULT_ADDR = 0
DEFAULT_UNITID = 1
DEFAULT_COUNT = 1
COIL = 0
DINPUT = 1
HREG = 2
IREG = 3
READ_ITEMS = ["coil", "discrete_input", "holding_register", "input_register"]
REG = 1
WRITE_ITEMS = ["coil", "register"]
