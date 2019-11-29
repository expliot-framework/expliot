"""Support for Zigbee network Scanner for zigbee auditor."""
import json
import time
from expliot.core.common.exceptions import sysexcinfo
from expliot.core.tests.test import Test, TCategory, TTarget, TLog
from expliot.core.protocols.radio.zigbee import ZigbeeNetworkScan


# pylint: disable=bare-except
class ZbAuditorNwkScan(Test):
    """Zigbee packet sniffer plugin."""

    def __init__(self):
        super().__init__(
            name="nwkscan",
            summary="Zigbee Network Scanner",
            descr="This plugin scans 2.4 GHz network for active IEEE 802.15.4 "
            "and Zigbee devices by sending IEEE 802.15.4 beacon requests on "
            "selected channels.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=[
                "https://www.zigbee.org/wp-content/uploads/2014/11/docs-05-3474-20-0csg-zigbee-specification.pdf"
            ],
            category=TCategory(TCategory.ZB_AUDITOR, TCategory.RD, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
            needroot=True,
        )

        self.argparser.add_argument(
            "-s",
            "--start",
            type=int,
            default=11,
            help="First channel to be scanned from 2.4 GHz band. "
            "If not specified, default is 11",
        )

        self.argparser.add_argument(
            "-e",
            "--end",
            type=int,
            default=26,
            help="Last channel to scanned from 2.4 GHz band"
            "if not specified, default is 26",
        )

        self.argparser.add_argument(
            "-f", "--filepath", help="file name to store network scan result as a log."
        )

        self.found = False
        self.reason = None
        self.filename = None

    @staticmethod
    def display_scan_result(result_dict):
        """This function take result as dictionary of network scan and display on ui."""

        if "device_count" in result_dict:
            count = result_dict["device_count"]
            TLog.generic("{:<17} {}".format("Devices found ", count))
            num_dev = 0

        if "beacons" in result_dict:
            dev_beacons = result_dict["beacons"]
            for dev in dev_beacons:
                num_dev += 1
                TLog.generic("{:<17}: {}".format("Device Number", num_dev))
                TLog.generic("{:<17}: {}".format("Channel", dev["channel"]))
                TLog.generic("{:<17}: {}".format("Source Address", dev["source_addr"]))
                TLog.generic("{:<17}: {}".format("Source PAN ID", dev["source_panid"]))

                if "extn_panid" in dev:
                    TLog.generic(
                        "{:<17}: {}".format(
                            "Extended PAN ID (Device Address)", dev["extn_panid"]
                        )
                    )

                TLog.generic(
                    "{:<17}: {}".format("Pan Coordinator", dev["pan_coordinator"])
                )
                TLog.generic(
                    "{:<17}: {}".format("Permit Joining", dev["permit_joining"])
                )

                if "router_capacity" in dev:
                    TLog.generic(
                        "{:<17}: {}".format("Router Capacity", dev["router_capacity"])
                    )

                if "device_capacity" in dev:
                    TLog.generic(
                        "{:<17}: {}".format("Device Capacity", dev["device_capacity"])
                    )

                if "protocol_version" in dev:
                    TLog.generic(
                        "{:<17}: {}".format("Protocol Version", dev["protocol_version"])
                    )

                if "stack_profile" in dev:
                    TLog.generic(
                        "{:<17}: {}".format("Stack Profile", dev["stack_profile"])
                    )

                TLog.generic("{:<17}: {}".format("LQI", dev["lqi"]))
                TLog.generic("{:<17}: {}".format("RSSI", dev["rssi"]))
                TLog.generic("")

    def write_result_to_logfile(self, result_dict):
        """Write results in a file as JSON."""
        with open(self.filename, "w") as write_file:
            result_json_str = json.dumps(result_dict)
            json.dump(json.loads(result_json_str), write_file, indent=4)

    def get_channel_mask(self):
        """Validate start and end scan channels and returns channel mask."""
        mask = 0x80000000  # MSB one indicate its mask
        # Calculate channel mask for scanning
        for i in range(self.args.start, self.args.end + 1):
            mask |= 1 << i  # shift 1 by channel number

        return mask

    def execute(self):
        """Execute the test."""
        if self.args.start < 11 or self.args.start > 26:
            self.result.setstatus(passed=False, reason="Invalid start channel")
            return

        if self.args.end < 11 or self.args.end > 26:
            self.result.setstatus(passed=False, reason="Invalid end channel")
            return

        if self.args.end < self.args.start:
            self.result.setstatus(passed=False, reason="Invalid start or end channel")
            return

        if self.args.filepath is not None:
            self.filename = self.args.filepath

        # Print user input
        TLog.generic("{:<13}: ({})".format("Start channel", self.args.start))
        TLog.generic("{:<13}: ({})".format("End channel", self.args.end))
        if self.filename is not None:
            TLog.generic("{:<13}: ({})".format("Log file", self.filename))

        TLog.generic("")

        # get channel mask
        ch_mask = self.get_channel_mask()

        try:
            # Get Network Scanner
            nwkscanner = ZigbeeNetworkScan()

            # Capture the scan start time
            start_time = time.time()

            # Start network scan with channel mask
            result_str = nwkscanner.scan(ch_mask)

            # Capture the scan start time
            end_time = time.time()

            if result_str is not None:
                self.found = True
                # Display result on console
                self.display_scan_result(result_str)

                TLog.generic("{:<17} {}".format("Scan duration", end_time - start_time))
                TLog.generic("")

                # Write result in log file
                if self.filename is not None:
                    self.write_result_to_logfile(result_str)
            else:
                self.found = False
                self.reason = "Couldn't find any Zigbee device on network"

        except:  # noqa: E722
            self.found = False
            self.reason = "Exception caught: {}".format(sysexcinfo())

        finally:
            self.result.setstatus(passed=self.found, reason=self.reason)
