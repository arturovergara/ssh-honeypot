#!/usr/bin/env python3

import argparse
import sys
import socket
import paramiko
import threading
from datetime import datetime
#  from random import randint

from util import IntRange

# Globals
LOG_FILE_NAME = "ssh-honeypot.log"
LOG_FILE_LOCK = threading.Lock()

# Banners
BANNERS = [
    "",                                        # No banner
    "OpenSSH_5.9p1 Debian-5ubuntu1.4",         # Ubuntu 12.04
    "OpenSSH_7.2p2 Ubuntu-4ubuntu2.1",         # Ubuntu 16.04
    "OpenSSH_7.6p1 Ubuntu-4ubuntu0.3",         # Ubuntu 18.04
    "OpenSSH_6.6.1",                           # openSUSE 42.1
    "OpenSSH_6.7p1 Debian-5+deb8u3",           # Debian 8.6
    "OpenSSH_7.5",                             # pfSense 2.4.4-RELEASE-p3
    "dropbear_2014.63",                        # dropbear 2014.63
    "SSH-2.0-OpenSSH_7.4p1 Raspbian-10+deb9u2" # Raspbian
]


# Class that implements the Paramiko interface for a correct handling of an SSH session
class Server(paramiko.ServerInterface):
    def __init__(self, client_address, log_file_name):
        self.event = threading.Event()
        self.client_address = client_address
        self.log_file_name = log_file_name

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED

        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    # Verify the credentials entered
    def check_auth_password(self, username, password):
        # Lock or unlock file access (Threading programming)
        LOG_FILE_LOCK.acquire()

        try:
            # The registered connection is append to the log file
            log_file = open(self.log_file_name, "a")
            print("{}\t{}\t{}\t{}".format(datetime.now().isoformat(' ', 'seconds'), self.client_address[0], username, password))
            log_file.write("{}\t{}\t{}\t{}\n".format(datetime.now().isoformat(' ', 'seconds'), self.client_address[0], username, password))
            log_file.close()
        finally:
            # Unlock file access
            LOG_FILE_LOCK.release()

        # It always returns "Authentication Failed", that is, the user with no credential will be able to log in
        return paramiko.AUTH_FAILED


# Function designed to work the SSH connection through threads, the entire connection process with
# a client must be encapsulated in a function in order to handle multiple simultaneous connections
def ssh_handle(connection, address, rsa_key, banner, log_file):
    try:
        transport = paramiko.Transport(connection)

        transport.add_server_key(rsa_key)
        transport.local_version = banner
        server = Server(address, log_file)

        try:
            transport.start_server(server=server)
        except:
            sys.stderr.write("[-] Error: SSH Negotation failed.\n")
            return

        channel = transport.accept(20)

        if channel is None:
            transport.close()
            return

        # No need for this, since the client will never authenticate
        server.event.wait()

        if not server.event.is_set():
            transport.close()
            return

        channel.close()

    except:
        sys.stderr.write("[-] There was an error generating a new connection.\n")
        transport.close()

def start_server(options):
    try:
        # Server socket is created
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print(f"[!] Using port: {options.port}")
        server_socket.bind(('', options.port))
    except:
        sys.stderr.write("[-] Failed to create and bind a new socket.\n")
        sys.exit(1)

    threads = []

    # If a RSA key file was specified uses this one else generate a new one
    if options.file is not None:
        print(f"[!] Using the following RSA Key File: {options.file.name}")
        rsa_key = paramiko.RSAKey(filename=options.file.name)
    else:
        print("[!] Generating a new RSA Key File ...")
        rsa_key = paramiko.RSAKey.generate(bits=2048)

    # Use banner option from arguments
    if options.banner is not None:
        banner = BANNERS[options.banner]
    elif options.banner_string is not None:
        banner = options.banner_string
    else:
        #  banner = BANNERS[randint(0, len(BANNERS))]
        banner = BANNERS[8]

    print(f"[!] Using the following banner: {banner}")

    if options.output is not None:
        log_file = options.output.name
    else:
        log_file = LOG_FILE_NAME

    print(f"[!] Using the following log file: {log_file}")
    print(f"[!] Number of max incoming connections: {options.number}")
    print("[!] Listening incoming connections ...\n")

    # Infinite loop waiting for incoming connections
    while True:
        try:
            server_socket.listen(options.number)
            client, address = server_socket.accept()
        except:
            sys.stderr.write("[-] Failed to create listen socket or accept the connection from the client.\n")

        # When establishing a new connection, it handles it in a thread to treat multiple simultaneous connections
        new_connection = threading.Thread(target=ssh_handle, args=((client, address, rsa_key, banner, log_file)))
        new_connection.start()
        threads.append(new_connection)

        for thread in threads:
            thread.join()

def parse_args(args=sys.argv[1:]):
    # Argument Parser
    parser = argparse.ArgumentParser(description="SSH Server Honeypot written in Python.")

    # Optional arguments
    parser.add_argument('-l', '--list-banners', action='store_true', help='List available banners to use')
    parser.add_argument('-b', '--banner', metavar='INDEX', type=int, choices=range(len(BANNERS)), help='Specify banner index to use from the list (default: 8)')
    parser.add_argument('-B', '--banner-string', metavar='STRING', type=str, help='Specify custom banner to use')
    parser.add_argument('-f', '--file', metavar='RSA_FILE', type=argparse.FileType('r'), help='RSA key file to use. If it is not specified, a new one is dynamically generated')
    parser.add_argument('-n', '--number', metavar='MAX_NUMBER', type=IntRange(min=1), default=10, help='Number of max connections (default: 10)')
    parser.add_argument('-o', '--output', metavar='LOG_FILE', type=argparse.FileType('a'), help='Specify log file to append (default: ./ssh-honeypot.log)')
    parser.add_argument('-p', '--port', type=IntRange(1, 65535), default=2222, help='Listen port (default: 2222)')

    return parser.parse_args(args)

def list_banners():
    print("\nList of available banners to use.")
    print("---------------------------------\n")

    for index, banner in enumerate(BANNERS):
        print(f"{index}. {banner}")

def main():
    # Get arguments
    options = parse_args()

    # List banners if was specified
    if options.list_banners:
        list_banners()
        return

    if (options.banner is not None) and (options.banner_string is not None):
        sys.stderr.write("[!] Error: --banner and --banner-string options cannot be used together.\n")
        exit(-1)

    # Start the server
    start_server(options)

if __name__ == "__main__":
    main()

