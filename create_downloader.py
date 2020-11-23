#!/usr/bin/env python
"Create Downloader Script"
import socket
import subprocess
import sys
import time
from contextlib import closing
from os.path import expandvars, expanduser
from tempfile import NamedTemporaryFile

import click
from click_config_file import configuration_option
import digitalocean

PLAYBOOK = "/Users/tyler/src/devops/ansible-playbooks/downloader/playbook.yml"
ANSIBLE = expandvars("$CONDA_PREFIX/bin/ansible-playbook")


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


def run_ansible(ip_address):
    "Execute ansible"
    with NamedTemporaryFile("w+t") as tempfile:
        tempfile.write(f"[downloaders]\n{ip_address}\n")
        tempfile.flush()
        subprocess.run(
            [ANSIBLE, "-i", tempfile.name, "-u", "root", PLAYBOOK], check=True
        )


@click.command()
@click.option("-n", "--name", default="downloader")
@click.option("-r", "--region", default="sfo2")
@click.option("-s", "--size-slug", default="s-1vcpu-1gb")
@click.option("-c", "--connect", type=bool, default=True)
def create_downloader(name, region, size_slug, connect):
    "Create Downloader."
    manager = digitalocean.Manager()
    try:
        droplet = next(
            droplet for droplet in manager.get_all_droplets() if droplet.name == name
        )
        click.secho(f"Found droplet at {droplet.ip_address}", fg="magenta", err=True)
    except StopIteration:
        droplet = create_droplet(manager, name, region, size_slug)
        wait_for_ssh(droplet.ip_address)
    run_ansible(droplet.ip_address)
    if connect:
        subprocess.run("ssh root@" + droplet.ip_address, shell=True, check=True)
    click.secho("\nssh root@" + droplet.ip_address, fg="magenta")


@click.command()
@click.option("-d", "--destination")
@click.option("-a", "--ip-address")
@click.option("-n", "--name", default="downloader")
def retrieve_files(destination, ip_address, name):
    "Download files from dest with rsync"
    if ip_address is None:
        manager = digitalocean.Manager()
        try:
            droplet = next(
                droplet
                for droplet in manager.get_all_droplets()
                if droplet.name == name
            )
            click.secho(
                f"Found droplet at {droplet.ip_address}", fg="magenta", err=True
            )
            ip_address = droplet.ip_address
        except StopIteration:
            click.secho("Does the server exist?", fg="red", err=True)
            sys.exit(1)

    subprocess.run(
        f"rsync -ruv 'root@{ip_address}:~/*' {expandvars(expanduser(destination))}",
        check=True,
        shell=True,
    )


def create_droplet(manager, name, region, size_slug):
    "Makes a new droplet if one doesn't already exist."
    keys = manager.get_all_sshkeys()
    click.secho("Creating droplet", fg="cyan")
    image = manager.get_image(69439535)
    droplet = digitalocean.Droplet(
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


@click.command()
@click.option("-n", "--name", default="downloader")
def destroy_droplet(name):
    "Create Downloader."
    manager = digitalocean.Manager()
    try:
        droplet = next(
            droplet for droplet in manager.get_all_droplets() if droplet.name == name
        )
        click.secho(f"Found droplet at {droplet.ip_address}", fg="magenta", err=True)
    except StopIteration:
        click.secho("Droplet not found.", err=True, fg="red")
        sys.exit(1)
    droplet.destroy()


@click.group()
def group():
    "Control creation and destruction of pirate downloaders"


group.add_command(create_downloader, "create")
group.add_command(destroy_droplet, "destroy")

if __name__ == "__main__":
    group()
