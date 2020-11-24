"Destroy droplet"
import sys

import click
from click_conf_file import conf_option

from .constants import ACCESS_TOKEN
from .droplet_helper import DropletNotFound, find_droplet_by_name


@click.command("destroy")
@click.option("-n", "--droplet-name", default="downloader")
@click.option("-t", "--access-token", type=str, envvar=ACCESS_TOKEN, show_envvar=True)
@conf_option(app_name="torrentdoer")
def destroy_droplet(droplet_name, access_token):
    "Destroy downloader."
    try:
        find_droplet_by_name(droplet_name, access_token).destroy()
        click.secho("Destroyed droplet.", fg="magenta", err=True)
    except DropletNotFound:
        click.secho("Droplet not found.", err=True, fg="red")
        sys.exit(1)
