"""Sample test/plugin as demo."""
from expliot.core.tests.test import Test, TCategory, TTarget, \
    TLog, LOGNO

DEFAULT_PORT = 80


class Sample(Test):
    """
    Test class for the sample.

    Every plugin needs to define and document the output format used in output_handler()
    Output Format:

    [
        {
            {"found_entry_in_db": "FooEntry"},
            {"found_entry_in_db": "FooEntry2"},
            {
                "status": "Server is vulnerable",
                "services_available": [
                                        "ssh",
                                        "foo"
                                      ]
            }
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="Sample",
            summary="Sample Summary",
            descr="Sample Description",
            author="Sample author",
            email="email@example.com",
            ref=["https://example.com", "https://example.dom"],
            category=TCategory(TCategory.COAP, TCategory.SW, TCategory.EXPLOIT),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-r", "--rhost", required=True, help="IP address of the target"
        )
        self.argparser.add_argument(
            "-p",
            "--rport",
            default=DEFAULT_PORT,
            type=int,
            help="Port number of the target. Default is {}".format(DEFAULT_PORT),
        )
        self.argparser.add_argument(
            "-v", "--verbose", action="store_true", help="show verbose output"
        )

    def pre(self):
        """Run before the test."""
        TLog.generic("Enter {}.pre()".format(self.id))
        # Only implement this if you need to do some setup etc.
        TLog.generic("Exit {}.pre()".format(self.id))

    def post(self):
        """Run after the test."""
        TLog.generic("Enter {}.post()".format(self.id))
        # Only implement this if you need to do some cleanup etc.
        TLog.generic("Exit {}.post()".format(self.id))

    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Sending request to server({}) on port({})".format(
                self.args.rhost, self.args.rport
            )
        )
        TLog.trydo("Searching imaginary database")
        self.output_handler(found_entry_in_db="FooEntry")
        # Or if you need to print extra message for only the console
        # but not required for the actual result output (chaining plugins)
        self.output_handler(msg="Found matching entry in database - ({})".format("FooEntry"),
                            logkwargs=LOGNO,
                            found_entry_in_db="FooEntry2")
        snd = "GET / HTTP/1.1"
        TLog.generic(
            "Sending command to server ({}) on port ({})".format(
                self.args.rhost, self.args.rport
            )
        )
        if self.args.verbose is True:
            TLog.generic("More verbose output. Sending payload ({})".format(snd))
        TLog.fail("No response received")
        TLog.generic("Re-sending command")
        response = "Response received from the server"
        # In case of failure (Nothing to do in case of success)
        if response:
            self.output_handler(status="Server is vulnerable", services_available=["ssh", "foo"])
        else:
            self.result.setstatus(passed=False, reason="Server is not vulnerable")
        # Or in case you want the test to fail with whatever exception occurred as the reason
        # use reason=self.result.exception()
