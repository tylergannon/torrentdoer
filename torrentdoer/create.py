"Create Droplet"
import subprocess
import time
import toml

import click
import digitalocean
from click_conf_file import conf_option

from .constants import ACCESS_TOKEN
from .droplet_helper import (
    find_droplet_by_name,
    DropletNotFound,
    ansible_playbook,
    in_tempdir,
    expandall,
)
from .ssh import wait_for_ssh, make_tunnel


@click.command("create")
@click.option("-n", "--droplet-name", default="downloader")
@click.option("-r", "--region", default="sfo2")
@click.option("-s", "--size-slug", default="s-1vcpu-1gb")
@click.option("-c", "--connect", type=bool, default=False)
@click.option("-T", "--tunnel", type=bool, default=True)
@click.option("-i", "--image", default="centos-8-x64")
@click.option("-t", "--access-token", type=str, envvar=ACCESS_TOKEN, show_envvar=True)
@click.option("-p", "--transmission-port", default=9091)
@conf_option(app_name="torrentdoer", send_param=True)
def create_downloader(  # pylint: disable=R0913
    droplet_name,
    region,
    size_slug,
    connect,
    access_token,
    image,
    tunnel,
    transmission_port,
    config,
):
    "Create Downloader."
    try:
        droplet = find_droplet_by_name(droplet_name, access_token)
        click.secho(
            f"Found droplet at {droplet.ip_address}",
            fg="magenta",
            err=True,
        )
    except DropletNotFound:
        droplet = create_droplet(droplet_name, region, size_slug, access_token, image)
        wait_for_ssh(droplet.ip_address)
    configure_droplet_ansible(droplet.ip_address)
    if tunnel:
        make_tunnel(droplet.ip_address, transmission_port)
    if connect:
        subprocess.run("ssh root@" + droplet.ip_address, shell=True, check=True)
    # click.secho("\nssh root@" + droplet.ip_address, fg="magenta")
    config["ip_address"] = droplet.ip_address
    with open(expandall("~/.torrentdoerrc"), "w") as rcfile:
        toml.dump(config, rcfile)
    click.secho("Done.", fg="magenta", err=True)


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


def configure_droplet_ansible(ip_address):
    "Execute ansible"

    with in_tempdir():
        with open("hosts.cfg", "w") as hosts:
            hosts.write(f"[downloaders]\n{ip_address}\n")
        with open("playbook.yml", "w") as playbook:
            playbook.write(PLAYBOOK)
        with open("settings.json", "w") as settings_json:
            settings_json.write(SETTINGS_JSON)
        ansible_playbook("hosts.cfg", "playbook.yml")


PLAYBOOK = """
- hosts: downloaders
  tasks:
    - name: Install epel
      dnf:
        name:
          - epel-release
        state: latest
    - name: Install transmission-daemon and tmux
      dnf:
        name:
          - tmux
          - transmission-daemon
        state: latest
    - name: Set up Transmission Daemon
      systemd:
        name: transmission-daemon
        state: started
        enabled: yes
    - name: Ensure Directories Exist
      file:
        path: /var/lib/transmission/{item}
        state: directory
        mode: '0755'
        owner: transmission
      loop:
        - Downloads
        - ActiveDownloads
      notify:
        - Restart Transmission
    - name: Copy Settings.json
      copy:
        src: settings.json
        dest: /var/lib/transmission/.config/transmission-daemon/settings.json
        owner: transmission
        mode: '0644'
        force: no
      notify:
        - Restart Transmission
  handlers:
    - name: Restart Transmission
      systemd:
        name: transmission-daemon
        state: restarted
  remote_user: root
"""


SETTINGS_JSON = """
{
    "alt-speed-down": 50,
    "alt-speed-enabled": false,
    "alt-speed-time-begin": 540,
    "alt-speed-time-day": 127,
    "alt-speed-time-enabled": false,
    "alt-speed-time-end": 1020,
    "alt-speed-up": 50,
    "bind-address-ipv4": "0.0.0.0",
    "bind-address-ipv6": "::",
    "blocklist-enabled": false,
    "blocklist-url": "http://www.example.com/blocklist",
    "cache-size-mb": 4,
    "dht-enabled": true,
    "download-dir": "/var/lib/transmission/Downloads",
    "download-queue-enabled": true,
    "download-queue-size": 5,
    "encryption": 1,
    "idle-seeding-limit": 30,
    "idle-seeding-limit-enabled": false,
    "incomplete-dir": "/var/lib/transmission/ActiveDownloads",
    "incomplete-dir-enabled": false,
    "lpd-enabled": false,
    "message-level": 1,
    "peer-congestion-algorithm": "",
    "peer-id-ttl-hours": 6,
    "peer-limit-global": 200,
    "peer-limit-per-torrent": 50,
    "peer-port": 51413,
    "peer-port-random-high": 65535,
    "peer-port-random-low": 49152,
    "peer-port-random-on-start": false,
    "peer-socket-tos": "default",
    "pex-enabled": true,
    "port-forwarding-enabled": true,
    "preallocation": 1,
    "prefetch-enabled": true,
    "queue-stalled-enabled": true,
    "queue-stalled-minutes": 30,
    "ratio-limit": 2,
    "ratio-limit-enabled": false,
    "rename-partial-files": true,
    "rpc-authentication-required": false,
    "rpc-bind-address": "0.0.0.0",
    "rpc-enabled": true,
    "rpc-host-whitelist": "",
    "rpc-host-whitelist-enabled": true,
    "rpc-password": "{e46622e81d6587df0cf3dfc64cb5b236a52cdcce01mb8oZr",
    "rpc-port": 9091,
    "rpc-url": "/transmission/",
    "rpc-username": "",
    "rpc-whitelist": "127.0.0.1,::1",
    "rpc-whitelist-enabled": true,
    "scrape-paused-torrents-enabled": true,
    "script-torrent-done-enabled": false,
    "script-torrent-done-filename": "",
    "seed-queue-enabled": false,
    "seed-queue-size": 10,
    "speed-limit-down": 100,
    "speed-limit-down-enabled": false,
    "speed-limit-up": 100,
    "speed-limit-up-enabled": false,
    "start-added-torrents": true,
    "trash-original-torrent-files": false,
    "umask": 18,
    "upload-slots-per-torrent": 14,
    "utp-enabled": true
}

"""
