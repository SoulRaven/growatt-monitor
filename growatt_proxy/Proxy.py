#  -*- coding: utf-8 -*-
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

import select
import socket
import sys
import time

from loguru import logger

from RoundBox.conf.project_settings import settings
from RoundBox.conf.app_settings import app_settings
from RoundBox.utils.data_process import decrypt

from .signals import (init_proxy, on_accept, on_recv, on_close)

# to resolve errno 32: broken pipe issue (only linux)
if sys.platform != 'win32':
    from signal import signal, SIGPIPE, SIG_DFL  # noqa

# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can break things
buffer_size = 4096
# buffer_size = 65535
delay = 0.0002


class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception as e:
            print(e)
            return False


class Proxy:
    input_list = []
    channel = {}
    s = None

    def __init__(self):
        logger.info("Growatt Proxy server started")
        # to resolve errno 32: broken pipe issue (Linux only)
        if sys.platform != 'win32':
            signal(SIGPIPE, SIG_DFL)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        growatt_proxy_bind_ip = app_settings.GROWATT_PROXY_BIND_IP
        if app_settings.GROWATT_PROXY_BIND_IP == "default":
            growatt_proxy_bind_ip = '0.0.0.0'

        self.server.bind((growatt_proxy_bind_ip, app_settings.GROWATT_PROXY_BIND_PORT))

        try:
            hostname = (socket.gethostname())
            logger.info("Hostname : {}".format(hostname))
            logger.info("IP: {}, PORT: {}".format(socket.gethostbyname(hostname), app_settings.GROWATT_PROXY_BIND_PORT))
        except:
            logger.error("IP and port information not available")

        self.server.listen(200)
        self.forward_to = (app_settings.GROWATT_REMOTE_IP, app_settings.GROWATT_REMOTE_PORT)

    def main(self):
        self.input_list.append(self.server)
        while True:
            time.sleep(delay)
            ss = select.select
            readable, writable, exceptional = ss(self.input_list, [], [])
            for self.s in readable:
                if self.s == self.server:
                    self.on_accept()
                    break
                try:
                    self.data, self.addr = self.s.recvfrom(buffer_size)
                except:
                    if settings.DEBUG:
                        logger.debug("GROWATT TCP Socket Proxy connection error")

                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    self.on_recv()
            init_proxy.send(sender=self.__class__)

    def on_accept(self):
        forward = Forward().start(self.forward_to[0], self.forward_to[1])
        clientsock, clientaddr = self.server.accept()
        if forward:
            logger.info("{} has connected".format(clientaddr))
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            logger.error("Can't establish connection with remote server.")
            logger.error("Closing connection with client side {}".format(clientaddr))
            clientsock.close()

    def on_close(self):
        # try / except to resolve errno 107: Transport endpoint is not connected
        try:
            logger.info("{} has disconnected".format(self.s.getpeername()))
        except:
            logger.error("peer has disconnected")

        # remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self):
        data = self.data

        logger.info("Growatt packet received:")
        logger.info(self.channel[self.s])
        # FILTER!!!!!!!! Detect if configure data is sent!
        header = "".join("{:02x}".format(n) for n in data[0:8])

        if settings.GROWATT_BLOCK_CMD:
            # standard everything is blocked!
            block_flag = True
            # partly block configure Shine commands
            if header[14:16] == "18":
                if settings.GROWATT_BLOCK_CMD:
                    if header[6:8] == "05" or header[6:8] == "06":
                        conf_data = decrypt(data)
                    else:
                        conf_data = data

                    # get conf command (location depends on record type), maybe later more flexibility is needed
                    if header[6:8] == "06":
                        conf_cmd = conf_data[76:80]
                    else:
                        conf_cmd = conf_data[36:40]

                    if header[14:16] == "18":
                        # do not block if configure time command of configure IP (if noipf flag set)
                        logger.info("Shine Configure command detected")
                        if conf_cmd == "001f" or (conf_cmd == "0011" and settings.GROWATT_NO_IP_CHANGE):
                            block_flag = False
                            if conf_cmd == "001f":
                                conf_cmd = "Time"
                            if conf_cmd == "0011":
                                conf_cmd = "Change IP"
                            logger.info("Configure command not blocked : {}".format(conf_cmd))
                    else:
                        # All configure inverter commands will be blocked
                        logger.info("Inverter Configure command detected")

            # allow records:
            if header[12:16] in settings.GROWATT_RECWL:
                block_flag = False

            if block_flag:
                logger.info("Record blocked: {}".format(header[12:16]))
                return

        # send data to destination
        self.channel[self.s].send(data)
        if len(data) > settings.GROWATT_MIN_REC_LENGTH:
            # process received data
            procdata(data)
        else:
            logger.info("Data less then minimum record length, data not processed")
