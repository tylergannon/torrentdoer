"ssh functions"
import socket
import time
from contextlib import closing
from subprocess import run

import click


def socket_available(host, port) -> bool:
    "Returns whether or not the socket can be opened."
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return sock.connect_ex((host, port)) == 0


def make_tunnel(host, port, user="root"):
    "Create an SSH tunnel by shelling out to ssh."
    if socket_available("localhost", port):
        click.secho(f"Found port {port} already open.", fg="blue", err=True)
    else:
        click.secho(f"Setting up tunnel to {host}:{port}", fg="blue", err=True)
        run(f"ssh -L {port}:localhost:{port} -fN {user}@{host}", check=True, shell=True)


def wait_for_ssh(host):
    "Waits for SSH on host to be available."
    click.secho("Waiting for ssh to be available", err=True, fg="yellow", nl="")
    while not socket_available(host, 22):
        click.secho(".", err=True, fg="yellow", nl="")
        time.sleep(1)
