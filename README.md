# torrentdoer

Do your torrenting from DigitalOcean!

Sets up a DigitalOcean droplet in your account,
enables transmission-daemin in systemd, and opens up
an SSH tunnel from port 9091 on your machine to the
remote, for easy control.

## Installation

```
python -m pip install torrentdoer
```

## Usage

Just make sure you have an API Access Token from DigitalOcean.
you can either export `$DIGITALOCEAN_ACCESS_TOKEN` or else
pass the token to the `-t/--access-token` command-line option.

### Start Server

```bash
export DIGITALOCEAN_ACCESS_TOKEN='somuchsecret'

torrentdoer create
```

Now go ahead and open up a Transmission Client, pointing it to
localhost:9091.

### Retrieve Files

This will run rsync between the transmission daemon and your local machine.

```bash
torrentdoer retrieve
```

### Remove The Server

Save money by deleting the server when not in use.

```bash
torrentdoer destroy
```

### Open SSH Session To Droplet


```bash
torrentdoer ssh
```

### (Re-)Open SSH Tunnel


```bash
torrentdoer tunnel
```

Have fun!
