import socket
import os
import threading
from threading import Thread
import filter
import sys
import time
import re

# Small configurations

lastPacketN = 20
flagRegex = r"[A-Z0-9]{31}="
flagLogDir = '/var/log/proxy'
serviceName = 'default'


class Proxy2Server(Thread):

    def __init__(self, host, port):
        super(Proxy2Server, self).__init__()
        self.closed = False
        self.game = None # game client socket not known yet
        self.socket = None
        self.filter_data = {}
        self.port = port
        self.host = host
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.lastPackets = []  # Used for stored both, input and output packets

    def close(self):
        if not self.closed:
            self.closed = True

            if not self.game.closed:
                self.game.close()

            if socket is not None:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()

            self.game = None

    # run in thread
    def run(self):
        while True:
            try:
                data = self.socket.recv(4096)
                if data:
                    if filter.output_rule(self, data):
                        self.lastPackets.append(data)

                        str_packet = str(data, 'UTF-8', errors='ignore')

                        if re.search(flagRegex, str_packet) is not None:
                            self.print_flag_report()

                        if re.search(r"Content-Encoding: (gzip|compress|deflate|br)", str_packet) is not None:
                            self.print_compression_warning("Warning! Your http server is using compression, flag reports will not be shown!")

                        self.game.socket.sendall(data)
                    else:
                        self.close()
                else:
                    self.close()
                    break

            except:
                self.close()
                break

    def print_flag_report(self):
        try:
            if not os.path.exists(flagLogDir):
                os.makedirs(flagLogDir)

            report_file_name = serviceName + '_flag_' + str(int(time.time()))
            report_file = open(flagLogDir + '/' + report_file_name, 'a')

            for packet in self.lastPackets:
                packet_str = str(packet, 'UTF-8', errors='ignore')
                report_file.write(packet_str + '\n\n')

            report_file.close()

            print("Flag leaked! Report file created: " + flagLogDir + '/' + report_file_name)
        except Exception as e:
            print("Error printing the flag report:")
            print(e)


    def print_compression_warning(self, warning):
        try:
            if not os.path.exists(flagLogDir):
                os.makedirs(flagLogDir)

            report_file_name = serviceName + '_warning_' + str(int(time.time()))
            report_file = open(flagLogDir + '/' + report_file_name, 'a')
            report_file.write(warning + '\n')
            report_file.close()

            print(warning)
        except Exception as e:
            print("Error printing the warning report:")
            print(e)


class Game2Proxy(Thread):

    def __init__(self, sock):
        super(Game2Proxy, self).__init__()
        self.server = None # real server socket not known yet
        self.filter_data = {}
        self.socket = sock
        self.closed = False

    def close(self):
        if not self.closed:

            self.closed = True

            if not self.server.closed:
                self.sever.close()

            if socket is not None:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()

            self.server = None

    def run(self):
        while True:
            try:
                data = self.socket.recv(4096)

                if data:
                    filter_out = filter.input_rule(self, data)

                    if not filter_out:
                        self.close()
                        break
                    elif type(filter_out) is bytes:
                        data = filter_out

                    self.server.lastPackets.append(data)

                    self.server.socket.sendall(data)
                else:
                    self.close()
                    break

            except:
                self.close()
                break


class Proxy(Thread):

    def __init__(self, from_host, to_host, from_port, to_port):
        super(Proxy, self).__init__()
        self.sock = None
        self.from_host = from_host
        self.to_host = to_host
        self.from_port = from_port
        self.to_port = to_port

    def handle(self, new_client, addr):
        p2s = Proxy2Server(self.to_host, self.to_port)
        g2p = Game2Proxy(new_client)
        # print "[proxy({})] Connected to the real server".format(self.port)
        p2s.game = g2p
        g2p.server = p2s

        p2s.start()
        g2p.start()

    def run(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.from_host, self.from_port))
        self.sock.listen(1)

        while True:
            new_client, addr = self.sock.accept()
            threading.Thread(target=self.handle, args=(new_client, addr)).start()


# Read arguments
if len(sys.argv) < 2:
    print("Usage: python3 server.py <LISTEN_PORT> <REAL_PORT> [<SERVICE_NAME>] [<REAL_IP>]")

if len(sys.argv) > 3:
    serviceName = sys.argv[3]

real_ip = "127.0.0.1"

if len(sys.argv) > 4:
    real_ip = sys.argv[4]

from_port = int(sys.argv[1])
to_port = int(sys.argv[2])


master_server = Proxy('0.0.0.0', real_ip, from_port, to_port)
master_server.start()
