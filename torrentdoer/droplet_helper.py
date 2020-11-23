"Droplet Helper Funs"
import subprocess
from contextlib import contextmanager
from os import chdir, getcwd
from os.path import dirname, expanduser, expandvars, join
from sys import executable
from tempfile import TemporaryDirectory

from digitalocean import Droplet, Manager

ANSIBLE = join(dirname(executable), "ansible-playbook")


class DropletNotFound(Exception):
    "Droplet Not Found Error"


def expandall(string):
    "Expand user home and env vars in string"
    return expanduser(expandvars(string))


def find_droplet_by_name(droplet_name: str, access_token: str) -> Droplet:
    """
    Find droplet by name.  Finds the first one by name, I think from
    any project.

    :param droplet_name: The name of the droplet to find.
    :param manager: A Manager object to use.

    """
    manager = Manager(token=access_token)

    try:
        return next(
            droplet
            for droplet in manager.get_all_droplets()
            if droplet.name == droplet_name
        )
    except StopIteration:
        raise DropletNotFound(f"Droplet {droplet_name} not found.") from None


def rsync(source, dest):
    "Runs rsync in a subprocess"
    subprocess.run(
        f"rsync -ruv '{source}' '{dest}' --exclude '*.part'", check=True, shell=True
    )


def ansible_playbook(inventory_file, playbook_path):
    "Call ansible-playbook with inventory and playbook files."
    subprocess.run(
        f"{ANSIBLE} -i {inventory_file} -u root {playbook_path}",
        shell=True,
        check=True,
    )


@contextmanager
def in_tempdir():
    "Change to a temporary directory and then back again"
    go_back_to = getcwd()
    with TemporaryDirectory() as tempdir:
        chdir(tempdir)
        try:
            yield tempdir
        finally:
            chdir(go_back_to)
