# DOW
A tool to manage on-demand cloud development environments within Digital Ocean. 

[![demo](https://asciinema.org/a/6vyKr0yek5WQesJYgn4MTvR5E.svg)](https://asciinema.org/a/6vyKr0yek5WQesJYgn4MTvR5E?autoplay=1)

## Why
Sometimes you might have a very limited internet bandwidth, but you still need to do the work; you still need to develop that feature for a software, which has a bunch of NPM dependencies, and runs development environment in a multi-docker container setup.

Or sometimes you might want to offload your old MacBook that has only 16GB of RAM, and running your local stack together with Slack, Spotify, Google Meet, Linear, Notion, Discord, VSCode, and other electron apps makes it unbearably slow.

Or maybe the only thing you have with you is an iPad with an SSH client, but you desperately need to fix that bug.

Fear no more. With this tool all bandwidth and computing power you need is for a tiny SSH window to a Digital Ocean droplet.

## How
This tool manages configuration for all your development environments and lets you start and stop them whenever you need them.

A development environment consists of two parts: a volume and a machine. Volume is a block storage that keeps your data, code, configuration, and even some software safe between machine restarts. Machine is a droplet, that provides you with CPU and RAM resources.

Since computing resources are quite expensive, we shut machines down when we don’t need them anymore. While we keep volumes, so we don’t need to reconfigure our development environment again and again every time.

Thanks to the magic of an SSH Agent and its forwarding, from a cloud dev workspace you get access everywhere you already have access from your local machine, including GitHub.

## What you need
- A Digital Ocean account (get one here [https://www.digitalocean.com](https://www.digitalocean.com/) if you still don’t have it)
- A Digital Ocean API key to manage droplets and volumes through their API (get one here https://cloud.digitalocean.com/account/api/tokens)
- A configured SSH key in Digital Ocean (here https://cloud.digitalocean.com/account/security)
- Some money to pay for volume gigabytes and droplet hours
- This tool
- _Optional:_ A configured firewall in Digital Ocean allowing only SSH access (because you don't want script-kiddies messing with your dev environment)

## How to use the tool

### Prerequisites
- Python 3.11 ([pyenv](https://github.com/pyenv/pyenv) is a convenient option)
- [Poetry](https://python-poetry.org/)
- `poetry install` inside the project directory
- Make sure `bin/dow` is on your `$PATH`

### The tool
1. Configure it
    ```
    % dow config token XXXXXXXXXXX
    [+] Token updated
    % dow config region blah
    [+] Region updated
    % dow config firewalls add fbcb7f36-334b-42db-8fb0-0d3f9ffe6277
    [+] Firewall fbcb7f36-334b-42db-8fb0-0d3f9ffe6277 added
2. Create a volume
    ```
    % dow volumes create --name dev --size 20 --fs-type xfs
    POST https://api.digitalocean.com/v2/volumes
    [+] Created volume 'dev'
    % dow volumes list                       
    GET https://api.digitalocean.com/v2/volumes {}
	name       size_gigabytes  fs_type
	dev        20              xfs
    ```
3. Create a machine
    ```
    % dow machines create \
        --name dev \
        --size c-8 \
        --image debian-11-x64 \
        --volume dev \
        --username misha \
        --swapsize 20
    [+] Created machine dev
    % dow machines list
    GET https://api.digitalocean.com/v2/droplets {}
    name   size  image          volume  username  swapsize  status  ip  ports
    dev    c-8   debian-11-x64  dev     misha     20        CONFIG      []
    ```
4. Configure forwarded ports
    ```
    % dow machines ports add --machine dev --port 5432
    [+] Added port '5432' to machine 'dev'
    ```
4. Start the machine
    ```
    % dow machines start dev 
	GET https://api.digitalocean.com/v2/droplets {'name': 'dev'}
	GET https://api.digitalocean.com/v2/volumes {'name': 'dev'}
	[+] Using volume 'dev' (362194ac-9c49-43ac-ad03-016c2b3a8d37)
	GET https://api.digitalocean.com/v2/account/keys {}
	[+] Using SSH keys: ['mbp']
	POST https://api.digitalocean.com/v2/droplets
	[+] Created droplet 111111111
	POST https://api.digitalocean.com/v2/firewalls/362194ac-9c49-43ac-ad03-016c2b3a8d37/droplets
	GET https://api.digitalocean.com/v2/droplets/111111111 {}
	[+] Status 'new', waiting...
	GET https://api.digitalocean.com/v2/droplets/111111111 {}
	[+] Status 'new', waiting...
	GET https://api.digitalocean.com/v2/droplets/111111111 {}
	[+] Status 'active', continuing
	GET https://api.digitalocean.com/v2/droplets/111111111 {}
	[+] Got IP address: XX.XXX.XXX.XX
	[+] Waiting for SSH to become available at XX.XXX.XXX.XX
	[+] Waiting for install log to be ready
	[+] Still waiting...
	[+] Waiting for machine init to complete
	[+] [2023-07-29 16:23:23] apt update
	[+] [2023-07-29 16:23:33] installing basic stuff
	[+] [2023-07-29 16:24:17] generating locale
	[+] [2023-07-29 16:24:19] creating user
	[+] [2023-07-29 16:24:19] mounting volume
	[+] [2023-07-29 16:24:19] creating swapfile
	[+] [2023-07-29 16:24:56] symlinking home
	[+] [2023-07-29 16:24:56] symlink /var/lib/docker
	[+] [2023-07-29 16:24:56] changing user's shell to zsh
	[+] [2023-07-29 16:24:56] preparing to install docker
	[+] [2023-07-29 16:24:56] apt update
	[+] [2023-07-29 16:24:58] installing docker
	[+] [2023-07-29 16:25:17] adding user to docker group
	[+] [2023-07-29 16:25:17] enabling byobu
	[+] [2023-07-29 16:25:17] configuring authorized keys
	[+] [2023-07-29 16:25:17] configuring byobu
	[+] [2023-07-29 16:25:17] starting inactivity check
	[+] Machine 'dev' is ready
	GET https://api.digitalocean.com/v2/droplets {'name': 'dev'}
	[+] To connect: ssh dev-dow
	```
4. Connect
    ```
    % ssh dev-dow
    ```

# ⚠️ Warning
Machines don’t shutdown automatically when idling (yet), so if you want to save some costs, remember to shut them down when you don’t need them anymore.

# Features
- Create named volumes of different sizes, which you can attach to machines
- Create and store configuration of as many cloud development environments as you need locally in a dotfile in TOML format
- Reuse SSH keys from your Digital Ocean account, so you can SSH into machines without any extra hassle
- Configure your preferred username 
- Configure port forwarding per machine
- Pre-configured on a machine:
	- Docker with compose- and buildx plugins
	- Mount-bind of the whole `/home` to your attached volume, so your work is persisted
	- Symlinked `/var/lib/docker` to your attached volume, so you keep docker cache and running containers between machine restarts
- Adding entries to your `~/.ssh/config` for easier access

# Not yet features
- Supporting images other than `debian-11-x64` due to hardcoded `user_data`
- Shutting down machines when idling to save costs


# Alternatives
- [Gitpod](https://www.gitpod.io/)
- [Coder](https://coder.com)
