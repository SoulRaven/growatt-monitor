#  -*- coding: utf-8 -*-

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

#
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
import smtplib
import threading
from pathlib import Path

from yagmail import SMTP
from yagmail.dkim import DKIM

from growatt_monitor.conf import settings
from growatt_monitor.core.mail.backends.base import BaseEmailBackend
from growatt_monitor.core.mail.utils import DNS_NAME


class EmailBackend(BaseEmailBackend):
    def __init__(
        self,
        host=None,
        port=None,
        username=None,
        password=None,
        oauth_file=None,
        smtp_starttls=None,
        smtp_ssl=None,
        fail_silently=False,
        use_dkim=False,
        dkim_domain=None,
        dkim_selector=None,
        dkim_private_key_file=None,
        dkim_include_headers=None,  # include all headers
        **kwargs,
    ):
        super().__init__(fail_silently=fail_silently)
        self.host = host or settings.EMAIL_HOST
        self.port = port or settings.EMAIL_PORT
        self.username = settings.EMAIL_HOST_USER if username is None else username
        self.password = settings.EMAIL_HOST_PASSWORD if password is None else password
        self.oauth = settings.EMAIL_OAUTH2 if oauth_file is None else oauth_file

        self.use_tls = settings.EMAIL_START_TLS if smtp_starttls is None else smtp_starttls
        self.use_ssl = settings.EMAIL_SSL if smtp_ssl is None else smtp_ssl

        if self.use_ssl and self.use_tls:
            raise ValueError(
                "EMAIL_USE_TLS/EMAIL_USE_SSL are mutually exclusive, so only set "
                "one of those settings to True."
            )

        self.use_dkim = settings.EMAIL_USE_DKIM if use_dkim is None else use_dkim
        self.dkim_domain = settings.EMAIL_DKIM_DOMAIN if dkim_domain is None else dkim_domain
        self.dkim_selector = (
            settings.EMAIL_DKIM_SELECTOR if dkim_selector is None else dkim_selector
        )
        self.dkim_private_key_file = (
            settings.EMAIL_DKIM_KEY_FILE
            if dkim_private_key_file is None
            else dkim_private_key_file
        )
        self.dkim_include_headers = (
            settings.EMAIL_DKIM_INCLUDE_HEADERS
            if dkim_include_headers is None
            else dkim_include_headers
        )

        self.dkim_obj = None
        self.connection = None
        self._lock = threading.RLock()

    def open(self) -> [SMTP, bool]:
        """Ensure an open connection to the email server. Return whether or not a
        new connection was required (True or False) or None if an exception
        passed silently.

        :return:
        """

        if self.connection:
            # Nothing to do if the connection is already open.
            return False

        # If local_hostname is not specified, socket.getfqdn() gets used.
        # For performance, we use the cached FQDN for local_hostname.
        connection_params = {
            "host": self.host,
            "port": self.port,
            "smtp_ssl": self.use_ssl,
            "smtp_starttls": self.use_tls,
        }

        if self.use_dkim:
            dkim_private_key = Path(self.dkim_private_key_file).read_bytes()

            self.dkim_obj = DKIM(
                domain=self.dkim_domain,
                selector=self.dkim_selector,
                private_key=dkim_private_key,
                include_headers=self.dkim_include_headers,
            )
            connection_params.update({"dkim": self.dkim_obj})

        if self.oauth:
            connection_params.update({"oauth2_file": self.oauth})
        else:
            connection_params.update({"user": self.username, "password": self.password})

        try:
            self.connection = SMTP(**connection_params)
            return True
        except OSError:
            if not self.fail_silently:
                raise

    def close(self):
        """Close the connection to the email server."""
        if self.connection is None:
            return

        try:
            try:
                if self.connection.is_closed:
                    self.connection.close()
            except:
                if self.fail_silently:
                    return
                raise
        finally:
            self.connection = None

    def send_messages(self, email_messages) -> int:
        """
        Send one or more EmailMessage objects and return the number of email messages sent.
        """
        if not email_messages:
            return 0

        with self._lock:
            new_conn_created = self.open()
            if not self.connection or new_conn_created is None:
                # We failed silently on open().
                # Trying to send would be pointless.
                return 0

            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if not sent:
                    num_sent += 1

            if not self.connection.is_closed:
                self.close()

            return num_sent

    def _send(self, email_message) -> bool:
        """
        A helper method that does the actual sending.
        :param email_message:
        :return:
        """

        try:
            return self.connection.send(**email_message)
        except (
            smtplib.SMTPRecipientsRefused,
            smtplib.SMTPHeloError,
            smtplib.SMTPSenderRefused,
            smtplib.SMTPDataError,
            smtplib.SMTPNotSupportedError,
        ):
            if not self.fail_silently:
                raise
            return False
