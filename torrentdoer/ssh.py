"ssh functions"
import socket
import time
from contextlib import closing

import click


def socket_available(host, port) -> bool:
    "Returns whether or not the socket can be opened."
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return sock.connect_ex((host, port)) == 0


def wait_for_ssh(host):
    "Waits for SSH on host to be available."
    click.secho("Waiting for ssh to be available", err=True, fg="yellow", nl="")
    while not socket_available(host, 22):
        click.secho(".", err=True, fg="yellow", nl="")
        time.sleep(1)
