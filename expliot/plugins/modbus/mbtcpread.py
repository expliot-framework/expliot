"""Support for reading data from Modbus over TCP."""
from expliot.core.protocols.internet.modbus import ModbusTcpClient
from expliot.core.tests.test import TCategory, Test, TLog, \
    TTarget, LOGNO
from expliot.plugins.modbus import (
    COIL,
    DINPUT,
    HREG,
    IREG,
    MODBUS_REFERENCE,
    READ_ITEMS,
    MODBUS_PORT,
    DEFAULT_ADDR,
    DEFAULT_UNITID,
    DEFAULT_COUNT,
)


# pylint: disable=bare-except
class MBTcpRead(Test):
    """
    Test for reading data from Modbus over TCP.

    Output Format:
    [
        {"addr": 2, "value": 1},
        # ... May be more entries
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="readtcp",
            summary="Modbus TCP Reader",
            descr="This plugin reads the item (coil, discrete input, holding "
            "and input register) values from a Modbus server.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=MODBUS_REFERENCE,
            category=TCategory(TCategory.MODBUS, TCategory.SW, TCategory.ANALYSIS),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-r",
            "--rhost",
            required=True,
            help="The hostname/IP address of the Modbus server",
        )
        self.argparser.add_argument(
            "-p",
            "--rport",
            default=MODBUS_PORT,
            type=int,
            help="The port number of the Modbus server. Default is {}".format(MODBUS_PORT),
        )
        self.argparser.add_argument(
            "-i",
            "--item",
            default=COIL,
            type=int,
            help="The item to read from. {coil} = {}, {} = {}, {} = {}, {} = {}. Default is {coil}".format(
                READ_ITEMS[COIL],
                DINPUT,
                READ_ITEMS[DINPUT],
                HREG,
                READ_ITEMS[HREG],
                IREG,
                READ_ITEMS[IREG],
                coil=COIL,
            ),
        )
        self.argparser.add_argument(
            "-a",
            "--address",
            default=DEFAULT_ADDR,
            type=int,
            help="The start address of item to read from. Default is {}".format(DEFAULT_ADDR),
        )
        self.argparser.add_argument(
            "-c",
            "--count",
            default=DEFAULT_COUNT,
            type=int,
            help="The count of items to read. Default is {}".format(DEFAULT_COUNT),
        )
        self.argparser.add_argument(
            "-u",
            "--unit",
            default=DEFAULT_UNITID,
            type=int,
            help="The Unit ID of the slave on the server to read from. "
                 "The default is {}".format(DEFAULT_UNITID),
        )

    def execute(self):
        """Execute the test."""
        modbus_client = ModbusTcpClient(self.args.rhost, port=self.args.rport)

        try:
            if self.args.item < 0 or self.args.item >= len(READ_ITEMS):
                raise AttributeError(
                    "Unknown --item specified ({})".format(self.args.item)
                )

            TLog.generic(
                "Sending read command to Modbus Server ({}) on port ({})".format(
                    self.args.rhost, self.args.rport
                )
            )
            TLog.generic(
                "(item={})(address={})(count={})(unit={})".format(
                    READ_ITEMS[self.args.item],
                    self.args.address,
                    self.args.count,
                    self.args.unit,
                )
            )
            modbus_client.connect()
            if self.args.item == COIL:
                response = modbus_client.read_coils(
                    self.args.address, self.args.count, unit=self.args.unit
                )
                if response.isError() is True:
                    raise Exception(str(response))
                values = response.bits
            elif self.args.item == DINPUT:
                response = modbus_client.read_discrete_inputs(
                    self.args.address, self.args.count, unit=self.args.unit
                )
                if response.isError() is True:
                    raise Exception(str(response))
                values = response.bits
            elif self.args.item == HREG:
                response = modbus_client.read_holding_registers(
                    self.args.address, self.args.count, unit=self.args.unit
                )
                if response.isError() is True:
                    raise Exception(str(response))
                values = response.registers
            elif self.args.item == IREG:
                response = modbus_client.read_input_registers(
                    self.args.address, self.args.count, unit=self.args.unit
                )
                if response.isError() is True:
                    raise Exception(str(response))
                values = response.registers
            else:
                raise AttributeError(
                    "Unknown --item specified ({})".format(self.args.item)
                )
            for entry in range(0, self.args.count):
                addr = self.args.address + entry
                self.output_handler(
                    msg="({}[{}]={})".format(
                        READ_ITEMS[self.args.item],
                        addr,
                        values[entry],
                    ),
                    logkwargs=LOGNO,
                    addr=addr,
                    value=values[entry],
                )
        except:  # noqa: E722
            self.result.exception()
        finally:
            modbus_client.close()
