"entrypoint module.  Sets up cli entrypoint."
import click


@click.group("torrent-doer")
def cli():
    """
    torrent-doer, creates and runs Transmission Daemon servers
    on a Digital Ocean Droplet.
    """
