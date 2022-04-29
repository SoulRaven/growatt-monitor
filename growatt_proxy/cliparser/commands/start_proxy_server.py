#  -*- coding: utf-8 -*-
#
#  Copyright (C) 2020-2022 ProGeek
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import errno
import re
import os
import sys
import socket

from datetime import datetime

from RoundBox.conf.project_settings import settings
from RoundBox.apps import apps
from RoundBox.core import checks
from RoundBox.core.cliparser import BaseCommand, CommandError
from RoundBox.utils.regex_helper import _lazy_re_compile
from RoundBox.utils import autoreload

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

    default_addr: str = "0.0.0.0"
    default_addr_ipv6: str = "::1"
    default_port: int = 5279

    def add_arguments(self, parser):
        """

        :param parser:
        :return:
        """

        parser.add_argument("args", metavar="start_proxy_server", nargs="*")

        parser.add_argument(
            "--addrport",
            action="store",
            dest="addrport",
            help="Optional port number, or ipaddr:port"
        )
        parser.add_argument(
            "--bind-ip",
            "-bindIP",
            action="store",
            dest="bindIP",
            help="Sets the ip from ware the proxy will listen for new connection. If the IP se set as 0.0.0.0 will "
            "listen on all interfaces ",
        )

        parser.add_argument(
            "--bind-port",
            "-bindPort",
            action="store",
            dest="bindPort",
            help="Set the port from where the proxy will listen for new connection. Default is 5279",
        )

        parser.add_argument(
            "--ipv6",
            "-6",
            action="store_true",
            dest="use_ipv6",
            help="Tells Growatt Proxy to use an IPv6 address.",
        )

        parser.add_argument(
            "--noreload",
            action="store_false",
            dest="use_reloader",
            help="Not autoreload the started server when file changes are done.",
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

        if options['addrport'] and (options['bindIP'] or options['bindPort']):
            raise CommandError(
                'If you are using `addrport` you can\'t use in the same time `bind_port` or `bind_addr`. Thare are '
                'mutually exclusive'
            )

        self.use_ipv6 = options["use_ipv6"]
        if self.use_ipv6 and not socket.has_ipv6:
            raise CommandError("Your Python does not support IPv6.")
        self._raw_ipv6 = False
        if not options["addrport"]:
            self.addr = ""
            self.port = self.default_port
        else:
            m = re.match(naiveip_re, options["addrport"])
            if m is None:
                raise CommandError(
                    '"%s" is not a valid port number '
                    "or address:port pair." % options["addrport"]
                )
            self.addr, _ipv4, _ipv6, _fqdn, self.port = m.groups()
            if not self.port.isdigit():
                raise CommandError("%r is not a valid port number." % self.port)
            if self.addr:
                if _ipv6:
                    self.addr = self.addr[1:-1]
                    self.use_ipv6 = True
                    self._raw_ipv6 = True
                elif self.use_ipv6 and not _fqdn:
                    raise CommandError('"%s" is not a valid IPv6 address.' % self.addr)
        if not self.addr:
            self.addr = self.default_addr_ipv6 if self.use_ipv6 else self.default_addr
            self._raw_ipv6 = self.use_ipv6

        self.run(None, **options)

    def run(self, *args, **options):
        """

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
                    "Growatt Proxy Server running on RoundBox version %(version)s\n"
                    "Using settings %(settings)r\n"
                    "Starting server on %(addr)s:%(port)s\n\n"
                    "Quit the server with %(quit_command)s."
                )
                % {
                    "version": self.get_version(),
                    "settings": settings.SETTINGS_MODULE,
                    "addr": "[%s]" % self.addr if self._raw_ipv6 else self.addr,
                    "port": self.port,
                    "quit_command": quit_command,
                }
            )

            try:
                pass
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
