#  -*- coding: utf-8 -*-

"""Base email backend class."""


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

class BaseEmailBackend:
    """
    Base class for email backend implementations.
    Subclasses must at least overwrite send_messages().
    open() and close() can be called indirectly by using a backend object as a
    context manager:
       with backend as connection:
           # do something with connection
           pass
    """

    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently

    def open(self):
        """
        Open a network connection.
        This method can be overwritten by backend implementations to
        open a network connection.
        It's up to the backend implementation to track the status of
        a network connection if it's needed by the backend.
        This method can be called by applications to force a single
        network connection to be used when sending mails. See the
        send_messages() method of the SMTP backend for a reference
        implementation.
        The default implementation does nothing.
        """
        pass

    def close(self):
        """Close a network connection."""
        pass

    def __enter__(self):
        try:
            self.open()
        except Exception:
            self.close()
            raise
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        raise NotImplementedError(
            "subclasses of BaseEmailBackend must override send_messages() method"
        )
