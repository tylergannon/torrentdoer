"Download files from server."
import sys

import click
from click_conf_file import conf_option
from .constants import ACCESS_TOKEN
from .droplet_helper import DropletNotFound, find_droplet_by_name, rsync, expandall


@click.command("retrieve")
@click.option("-d", "--download_to", default="~/Downloads")
@click.option("-a", "--ip-address")
@click.option("-n", "--droplet-name", default="downloader")
@click.option("-t", "--access-token", type=str, envvar=ACCESS_TOKEN, show_envvar=True)
@conf_option(app_name="torrentdoer")
def retrieve_files(download_to, ip_address, droplet_name, access_token):
    "Download files from dest with rsync"
    if ip_address is None:
        try:
            ip_address = find_droplet_by_name(droplet_name, access_token).ip_address
            click.secho(f"Droplet: {ip_address}", fg="magenta", err=True)
        except DropletNotFound:
            click.secho("Does the server exist?", fg="red", err=True)
            sys.exit(1)

    rsync(f"root@{ip_address}:/var/lib/transmission/Downloads", expandall(download_to))
