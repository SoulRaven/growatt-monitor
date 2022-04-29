#  -*- coding: utf-8 -*-

import errno
import os
import re
import sys
from datetime import datetime
from logging import getLogger

from RoundBox.conf.app_settings import app_settings
from RoundBox.conf.project_settings import settings
from RoundBox.core.cliparser import BaseCommand, CommandError
from RoundBox.utils import autoreload
from RoundBox.utils.regex_helper import _lazy_re_compile

from growatt_web_api.growatt import growatt_runtime

logger = getLogger('RoundBox.utils.autoreload')

naiveip_re = _lazy_re_compile(
    r"""^(?:
(?P<addr>
    (?P<ipv4>\d{1,3}(?:\.\d{1,3}){3}) |         # IPv4 address
    (?P<ipv6>\[[a-fA-F0-9:]+\]) |               # IPv6 address
    (?P<fqdn>[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*) # FQDN
):)?(?P<port>\d+)$""",
    re.X,
)


class Command(BaseCommand):
    help = "Start the Growatt Proxy server"

    requires_system_checks = []
    stealth_options = ("shutdown_message",)
    suppressed_base_arguments = {"--verbosity", "--traceback"}

    def __init__(self):
        super().__init__()

        self.username: str | None = None
        self.password: str | None = None
        self.server: str | None = None
        self.schedule_delay: str | None = None

    def add_arguments(self, parser):
        parser.add_argument("args", metavar="start_web_api", nargs="*")

        parser.add_argument(
            "--username", action="store", dest="username", type=str, help="Growatt OSS username"
        )

        parser.add_argument(
            "--password", action="store", dest="password", type=str, help="Growatt OSS password"
        )

        parser.add_argument(
            "--server", action="store", dest="server", type=str, help="Growatt endpoint web api"
        )

        parser.add_argument(
            "--plantId", action="store", dest="plantId", type=int, help="Growatt plant ID"
        )

        parser.add_argument(
            "--schedule-delay",
            action="store",
            dest="schedule_delay",
            type=int,
            help="How many seconds between each Growatt server call",
        )

        parser.add_argument(
            "--noreload",
            action="store_false",
            dest="use_reloader",
            help="Tells Growatt Web API to NOT use the auto-reloader.",
        )

        parser.add_argument(
            "--skip-checks",
            action="store_true",
            help="Skip system checks.",
        )

    def handle(self, *app_labels, **options):
        """

        :param app_labels:
        :param options:
        :return:
        """

        self.username = options.get('username') or getattr(app_settings, 'GROWATT_USERNAME')
        self.password = options.get('password') or getattr(app_settings, 'GROWATT_PASSWORD')

        self.server = options.get('server', getattr(app_settings, 'GROWATT_DEFAULT_URL'))

        self.schedule_delay = options.get(
            'schedule_delay', getattr(app_settings, 'SCHEDULE_DELAY_TASKS')
        )

        if not any([self.username, self.password]):
            raise CommandError(
                'Growatt username or password are empty. Set both on settings file or in command options'
            )

        self.run(None, **options)

    def run(self, *args, **options):
        """Run the server, using the autoreloader if needed.

        :param args:
        :param options:
        :return:
        """

        use_reloader = options["use_reloader"]
        if use_reloader:
            autoreload.run_with_reloader(self.inner_run, **options)
        else:
            self.inner_run(None, **options)

    def inner_run(self, *args, **options):
        """

        :param args:
        :param options:
        :return:
        """

        shutdown_message = options.get("shutdown_message", "")
        quit_command = "CTRL-BREAK" if sys.platform == "win32" else "CONTROL-C"

        if not options["skip_checks"]:
            self.stdout.write("Performing system checks...\n\n")
            self.check(display_num_errors=True)

        now = datetime.now().strftime("%B %d, %Y - %X")
        self.stdout.write(now)
        self.stdout.write(
            (
                "Growatt Web API running on RoundBox version %(version)s\n"
                "Using settings %(settings)r\n\n"
                "Quit the server with %(quit_command)s."
            )
            % {
                "version": self.get_version(),
                "settings": settings.SETTINGS_MODULE,
                "quit_command": quit_command,
            }
        )

        try:
            growatt_runtime(options)
        except OSError as e:
            # Use helpful error messages instead of ugly tracebacks.
            errors = {
                errno.EACCES: "You don't have permission to access that port.",
                errno.EADDRINUSE: "That port is already in use.",
                errno.EADDRNOTAVAIL: "That IP address can't be assigned to.",
            }
            try:
                error_text = errors[e.errno]
            except KeyError:
                error_text = e
            self.stderr.write("Error: %s" % error_text)
            # Need to use an OS exit because sys.exit doesn't work in a thread
            os._exit(1)
        except KeyboardInterrupt:
            if shutdown_message:
                self.stdout.write(shutdown_message)
            sys.exit(0)
