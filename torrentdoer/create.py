"Create Droplet"
import subprocess
import time
from os.path import dirname, join
from sys import executable
from tempfile import NamedTemporaryFile

import click
import digitalocean
from click_conf_file import conf_option

from .ssh import wait_for_ssh

PLAYBOOK = "/Users/tyler/src/devops/ansible-playbooks/downloader/playbook.yml"
ANSIBLE = join(dirname(executable), "ansible-playbook")
ACCESS_TOKEN = "DIGITALOCEAN_ACCESS_TOKEN"


@click.command("create")
@click.option("-n", "--name", default="downloader")
@click.option("-r", "--region", default="sfo2")
@click.option("-s", "--size-slug", default="s-1vcpu-1gb")
@click.option("-c", "--connect", type=bool, default=True)
@click.option("-i", "--image", default="s-1vcpu-1gb")
@click.option("-t", "--access-token", type=str, envvar=ACCESS_TOKEN)
@conf_option(app_name="torrentdoer")
def create_downloader(name, region, size_slug, connect, access_token, image):
    "Create Downloader."
    manager = digitalocean.Manager(token=access_token)
    try:
        droplet = next(drop for drop in manager.get_all_droplets() if drop.name == name)
        click.secho(f"Found droplet at {droplet.ip_address}", fg="magenta", err=True)
    except StopIteration:
        droplet = create_droplet(name, region, size_slug, access_token, image)
        wait_for_ssh(droplet.ip_address)
    ansible_create_droplet(droplet.ip_address)
    if connect:
        subprocess.run("ssh root@" + droplet.ip_address, shell=True, check=True)
    click.secho("\nssh root@" + droplet.ip_address, fg="magenta")


def create_droplet(name, region, size_slug, access_token, image):
    "Makes a new droplet if one doesn't already exist."
    manager = digitalocean.Manager(token=access_token)
    keys = manager.get_all_sshkeys()
    click.secho("Creating droplet", fg="cyan")
    image = manager.get_image(image)
    droplet = digitalocean.Droplet(
        token=access_token,
        name=name,
        region=region,
        image=image.slug,
        size_slug=size_slug,
        ssh_keys=keys,
        backups=False,
    )
    droplet.create()
    while droplet.status != "active":
        time.sleep(1)
        click.secho(".", fg="yellow", nl="", err=True)
        droplet = manager.get_droplet(droplet.id)
    click.secho("", err=True)
    return droplet


def ansible_create_droplet(ip_address):
    "Execute ansible"
    with NamedTemporaryFile("w+t") as tempfile:
        tempfile.write(f"[downloaders]\n{ip_address}\n")
        tempfile.flush()
        subprocess.run(
            [ANSIBLE, "-i", tempfile.name, "-u", "root", PLAYBOOK], check=True
        )
