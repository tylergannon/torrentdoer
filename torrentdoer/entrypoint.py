"entrypoint module.  Sets up cli entrypoint."
import click
from .create import create_downloader
from .destroy import destroy_droplet
from .retrieve import retrieve_files
from .sshconnect import ssh_connect, ssh_tunnel


@click.group("torrent-doer")
def cli():
    """
    torrent-doer, creates and runs Transmission Daemon servers
    on a Digital Ocean Droplet.
    """


cli.add_command(create_downloader, "create")
cli.add_command(destroy_droplet, "destroy")
cli.add_command(retrieve_files, "retrieve")
cli.add_command(ssh_connect, "ssh")
cli.add_command(ssh_tunnel, "tunnel")
