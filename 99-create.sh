#!/bin/bash -eu

source _base.sh

set -o pipefail

readonly DROPLET_NAME='dev'
readonly USERNAME=misha
readonly DROPLET_IMAGE="debian-11-x64"
readonly DROPLET_SIZE="s-4vcpu-8gb"
# readonly DROPLET_SIZE='s-1vcpu-512mb-10gb'
readonly DROPLET_SIZE="s-4vcpu-8gb-amd"
readonly VOLUME_NAME='workspace'

function fetch_ssh_keys() {
  ./01-ssh-keys.sh | jq -r '.ssh_keys[].id'
}

function create_droplet() {
  local name=$1
  local user_data=$2

  log "creating droplet"

  local result="$(./droplets-create.sh \
    name="${name}" \
    size="${DROPLET_SIZE}" \
    region="${DO_REGION}" \
    image="${DROPLET_IMAGE}" \
    ssh_keys:="$(jo -a $(fetch_ssh_keys))" \
    user_data="${user_data}" \
    volumes:="$(jo -a "${VOLUME_ID}")")"
  local droplet_id="$(echo "${result}" | jq '.droplet.id')"

  if [[ "${droplet_id}" == "null" ]]; then
    log "failed to create droplet:\n ${result}"
    exit 1
  fi

  echo "${droplet_id}"
}

function droplet_network() {
  local droplet_id=$1

  ./droplets-get.sh "${droplet_id}" |
    jq --raw-output '.droplet.networks.v4[] | select(.type == "public") | .ip_address'
}

function add_firewall() {
  local droplet_id=$1

  log "adding firewall"

  ./02-add-droplets-to-firewall.sh "${FIREWALL_ID}" "${droplet_id}"
}

function droplet_status() {
  local droplet_id=$1

  ./droplets-get.sh "${droplet_id}" |
    jq --raw-output '.droplet.status' |
    tr -d $'\n'
}

function wait_until_active() {
  local droplet_id=$1

  log "waiting until droplet ${droplet_id} is active"

  while true; do
    STATUS="$(droplet_status "${droplet_id}")"
    log "status: ${STATUS}"

    if [[ "${STATUS}" == "active" ]]; then
      break
    fi

    sleep 5
  done
}

function volume_name() {
  local volume_id=$1

  ./volumes-get.sh "${volume_id}" |
    jq --raw-output '.volume.name'
}

function ssh_into() {
  local ip_addr=$1
  shift

  ssh \
    -o UserKnownHostsFile=/tmp/test \
    -o StrictHostKeyChecking=no \
    "root@${ip_addr}" \
    "$@"
}

function wait_until_inited() {
  local ip_addr=$1
  local install_log=$2

  log "waiting until droplet ${ip_addr} is inited"

  while true; do
    line="$(ssh_into "${ip_addr}" "tail -n 1 ${install_log}")"

    if [[ "done" == "${line}" ]]; then
      break
    fi

    echo "${line}"

    sleep 1
  done
}

function wait_until_connectable() {
  local ip_addr=$1

  while true; do
    log "waiting until droplet ${ip_addr} is connectable"

    if ssh_into "${ip_addr}" "true"; then
      break
    fi

    sleep 1
  done
}

function wait_until_log_is_ready() {
  local ip_addr=$1
  local install_log=$2

  while true; do
    log "waiting until log is ready"

    if ssh_into "${ip_addr}" "test -f ${install_log}"; then
      break
    fi

    sleep 0.5
  done
}

readonly VOLUME_NAME="$(volume_name "${VOLUME_ID}")"
readonly INSTALL_LOG="/tmp/install-log"

readonly USER_DATA=$(
  cat <<EOF
#!/bin/bash

function log() {
  local msg=\$1

  echo "[\$(date -u '+%Y-%m-%d %H:%M:%S')] \$msg" >> "${INSTALL_LOG}"
}

log "apt update"
apt update
log "installing basic stuff"
apt install --yes \
  sudo \
  zsh \
  git \
  stow \
  byobu \
  curl \
  htop \
  ca-certificates \
  gnupg \
  lsb-release \
  rsync \
  jo \
  jq \
  ripgrep \
  ncdu

log "creating swapfile"
dd if=/dev/zero of=/var/swapfile bs=1M count=16k status=progress
chmod 600 /var/swapfile
mkswap /var/swapfile
swapon /var/swapfile
echo '/var/swapfile none swap defaults 0 0' | sudo tee -a /etc/fstab

log "generating locale"
echo 'en_US.UTF-8 UTF-8' | sudo tee -a /etc/locale.gen
locale-gen

log "creating user"
useradd ${USERNAME}
usermod --append --groups sudo ${USERNAME}
echo '${USERNAME} ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/91-${USERNAME}

log "mounting volume"
mkdir -p /mnt/${VOLUME_NAME}
chown ${USERNAME}: /mnt/${VOLUME_NAME}
chmod 755 /mnt/${VOLUME_NAME}
mount -o discard,defaults,noatime /dev/disk/by-id/scsi-0DO_Volume_${VOLUME_NAME} /mnt/${VOLUME_NAME}
echo '/dev/disk/by-id/scsi-0DO_Volume_${VOLUME_NAME} /mnt/${VOLUME_NAME} ext4 defaults,nofail,discard 0 0' | sudo tee -a /etc/fstab

log "symlinking home"
mkdir -p /mnt/${VOLUME_NAME}/home/${USERNAME}
chown ${USERNAME}: /mnt/${VOLUME_NAME}/home/${USERNAME}
rm -rf /home
ln -s /mnt/${VOLUME_NAME}/home /home

log "symlink /var/lib/docker"
mkdir -p /mnt/${VOLUME_NAME}/var_lib_docker
rm -rf /var/lib/docker
ln -s /mnt/${VOLUME_NAME}/var_lib_docker /var/lib/docker

log "changing user's shell to zsh"
chsh -s \$(command -v zsh) ${USERNAME}

log "preparing to install docker"
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=\$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
\$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
log "apt update"
apt update
log "installing docker"
apt install --yes \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-compose-plugin \
  docker-buildx-plugin

log "adding user to docker group"
usermod --append --groups docker ${USERNAME}

log "enabling byobu"
sudo --user ${USERNAME} byobu-enable

log "configuring authorized keys"
mkdir -p /home/${USERNAME}/.ssh
cp /root/.ssh/authorized_keys /home/${USERNAME}/.ssh/
chown --recursive ${USERNAME}: /home/${USERNAME}/.ssh

log "configuring byobu"
mkdir -p /home/${USERNAME}/.byobu
cat <<BYOBU > /home/${USERNAME}/.byobu/keybindings.tmux
unbind-key -n C-a
set -g prefix ^A
set -g prefix2 F12
bind b send-prefix
BYOBU

touch /home/${USERNAME}/.byobu/.welcome-displayed

echo "done" >> "${INSTALL_LOG}"
EOF
)

DROPLET_ID="$(create_droplet "${DROPLET_NAME}" "${USER_DATA}")"
readonly DROPLET_ID

log "droplet created: ${DROPLET_ID}"

add_firewall "${DROPLET_ID}"

wait_until_active "${DROPLET_ID}"
IP_ADDR="$(droplet_network "${DROPLET_ID}")"
readonly IP_ADDR
log "got ip: ${IP_ADDR}"

wait_until_connectable "${IP_ADDR}"
wait_until_log_is_ready "${IP_ADDR}" "${INSTALL_LOG}"
wait_until_inited "${IP_ADDR}" "${INSTALL_LOG}"

log "connect: ssh -A ${USERNAME}@${IP_ADDR}"
