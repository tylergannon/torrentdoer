"Download files from server."
import sys
from typing import Iterable

import click
from click_conf_file import conf_option
from .constants import ACCESS_TOKEN
from .droplet_helper import DropletNotFound, find_droplet_by_name, rsync, expandall


@click.command("retrieve")
@click.option("-d", "--download_to", default="~/Downloads/torrent")
@click.option("-a", "--ip-address")
@click.option(
    "-n",
    "--droplet-name",
    default="downloader",
    help="Optional droplet name that will be used if IP Address is not given.",
)
@click.option(
    "-t",
    "--access-token",
    type=str,
    envvar=ACCESS_TOKEN,
    show_envvar=True,
    help="Optional DigitalOcean droplet name that will be used to find "
    "IP address of droplet if not given.",
)
@click.option(
    "-i",
    "--include",
    multiple=True,
    help="Files to include.  Can be provided multiple times.  "
    "Be sure to enquote and add stars for match.",
)
@click.option(
    "-I",
    "--include-partial",
    multiple=True,
    help="Partial names to include. Example: '-I \"some_file\"' "
    "is the same as '-i \"*some_file*\"'.",
)
@conf_option(app_name="torrentdoer")
def retrieve_files(
    download_to,
    ip_address,
    droplet_name,
    access_token,
    include: Iterable[str],
    include_partial: Iterable[str],
):
    "Download files from dest with rsync"
    include = (*include, *(f"*{inc}*" for inc in include_partial))
    if ip_address is None:
        try:
            ip_address = find_droplet_by_name(droplet_name, access_token).ip_address
            click.secho(f"Droplet: {ip_address}", fg="magenta", err=True)
        except DropletNotFound:
            click.secho("Does the server exist?", fg="red", err=True)
            sys.exit(1)

    rsync(
        f"root@{ip_address}:/var/lib/transmission/Downloads/*",
        expandall(download_to),
        include,
    )
