"ssh functions"
import sys
from subprocess import run

from click_conf_file import conf_option
import click

from .constants import ACCESS_TOKEN
from .droplet_helper import find_droplet_by_name, DropletNotFound
from .ssh import make_tunnel


@click.command("ssh")
@click.option("-a", "--ip-address")
@click.option("-n", "--droplet-name", default="downloader")
@click.option("-T", "--access-token", type=str, envvar=ACCESS_TOKEN, show_envvar=True)
# @click.option("-p", "--transmission-port", default=9091)
@conf_option(app_name="torrentdoer")
def ssh_connect(  # pylint: disable=R0913
    ip_address,
    droplet_name,
    access_token,
    # transmission_port,
):
    "Open an SSH session to the droplet."

    if ip_address is None:
        try:
            ip_address = find_droplet_by_name(droplet_name, access_token).ip_address
        except DropletNotFound:
            click.secho("Droplet not found.", fg="cyan", err=True)
            sys.exit(1)
    run(f"ssh root@{ip_address}", shell=True, check=False)


@click.command("ssh-tunnel")
@click.option("-a", "--ip-address")
@click.option("-n", "--droplet-name", default="downloader")
@click.option("-T", "--access-token", type=str, envvar=ACCESS_TOKEN, show_envvar=True)
@click.option("-p", "--transmission-port", default=9091)
@conf_option(app_name="torrentdoer")
def ssh_tunnel(  # pylint: disable=R0913
    ip_address,
    droplet_name,
    access_token,
    transmission_port,
):
    "Open an SSH session to the droplet."

    if ip_address is None:
        try:
            ip_address = find_droplet_by_name(droplet_name, access_token).ip_address
        except DropletNotFound:
            click.secho("Droplet not found.", fg="cyan", err=True)
            sys.exit(1)
    make_tunnel(ip_address, transmission_port)
