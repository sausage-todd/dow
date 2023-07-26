function log() {
  local msg="$1"

  echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] $msg" >> "${INSTALL_LOG}"
}

log "apt update"
apt update
log "installing basic stuff"
apt install --yes \
  sudo \
  zsh \
  stow \
  byobu \
  curl \
  ca-certificates \
  gnupg \
  lsb-release \
  rsync \
  gcc \
  inetutils-telnet \
  build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev curl \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

log "generating locale"
echo 'en_US.UTF-8 UTF-8' | sudo tee -a /etc/locale.gen
locale-gen

log "creating user"
useradd "${USERNAME}"
usermod --append --groups sudo "${USERNAME}"
echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/91-${USERNAME}"

log "mounting volume"
mkdir -p "/mnt/${VOLUME_NAME}"
chown "${USERNAME}": "/mnt/${VOLUME_NAME}"
chmod 755 "/mnt/${VOLUME_NAME}"
mount -o discard,defaults,noatime "/dev/disk/by-id/scsi-0DO_Volume_${VOLUME_NAME}" "/mnt/${VOLUME_NAME}"
echo "/dev/disk/by-id/scsi-0DO_Volume_${VOLUME_NAME} /mnt/${VOLUME_NAME} ext4 defaults,nofail,discard 0 0" | sudo tee -a /etc/fstab

log "creating swapfile"
readonly SWAPFILE="/var/swapfile"
dd if=/dev/zero of="${SWAPFILE}" bs=1M count="${SWAPSIZE}k" status=progress
chmod 600 "${SWAPFILE}"
mkswap "${SWAPFILE}"
swapon "${SWAPFILE}"
echo "${SWAPFILE} none swap defaults 0 0" | sudo tee -a /etc/fstab

log "symlinking home"
mkdir -p "/mnt/${VOLUME_NAME}/home/${USERNAME}"
chown "${USERNAME}:" "/mnt/${VOLUME_NAME}/home/${USERNAME}"
rm -rf /home
mkdir -p /home
mount -o bind "/mnt/${VOLUME_NAME}/home" /home

log "symlink /var/lib/docker"
mkdir -p "/mnt/${VOLUME_NAME}/var_lib_docker"
rm -rf /var/lib/docker
ln -s "/mnt/${VOLUME_NAME}/var_lib_docker" /var/lib/docker

log "changing user's shell to zsh"
chsh -s "$(command -v zsh)" "${USERNAME}"

log "preparing to install docker"
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

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
usermod --append --groups docker "${USERNAME}"

log "enabling byobu"
sudo --user "${USERNAME}" byobu-enable

log "configuring authorized keys"
mkdir -p "/home/${USERNAME}/.ssh"
cp /root/.ssh/authorized_keys "/home/${USERNAME}/.ssh/"
chown --recursive "${USERNAME}:" "/home/${USERNAME}/.ssh"

log "configuring byobu"
mkdir -p "/home/${USERNAME}/.byobu"
cat <<BYOBU > "/home/${USERNAME}/.byobu/keybindings.tmux"
unbind-key -n C-a
set -g prefix ^A
set -g prefix2 F12
bind b send-prefix
BYOBU

touch "/home/${USERNAME}/.byobu/.welcome-displayed"

log "starting inactivity check"
cat <<INACTIVITY > "/usr/local/bin/inactivity.sh"
#!/bin/bash -eu

function number_of_connections() {
  w --no-header | awk '{print \$3}' | grep -E '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | wc -l
}

LAST_ACTIVITY_TS="\$(date +%s)"

while true; do
  TS="\$(date +%s)"
  if [[ "\$(number_of_connections)" -gt 0 ]]; then
    LAST_ACTIVITY_TS="\${TS}"
  fi
  INACTIVITY="\$((TS - LAST_ACTIVITY_TS))"
  printf "%s\t%s\n" "\${TS}" "\${INACTIVITY}" > /tmp/inactivity
  sleep 1
done
INACTIVITY
nohup bash "/usr/local/bin/inactivity.sh" &>/dev/null &

echo "done" >> "${INSTALL_LOG}"
