# Local Runner Setup for Yocto Builds

This guide explains how to set up a local machine to build the Yocto image for ha-grocy-openProject for free, without relying on GitHub Actions runners.

## Overview

Building Yocto images requires significant disk space and computational resources. This guide covers setting up a local build environment on WSL (Windows Subsystem for Linux) or native Linux that can produce the `ha-grocy-openproject-image` for Raspberry Pi 3/4.

## System Requirements

### Minimum Hardware
- **CPU**: Dual-core processor (quad-core recommended)
- **RAM**: 8 GB minimum (16 GB recommended for faster builds)
- **Disk Space**: 
  - 80+ GB for Yocto workspace and layers
  - 20+ GB for build artifacts
  - **Total: 100+ GB free space recommended**
- **Network**: Stable internet connection (5+ Mbps)

### Operating Systems Supported

#### Linux (Native)
- Ubuntu 20.04 LTS or later
- Debian 11 or later
- Fedora 35 or later
- openSUSE Leap 15.3 or later
- CentOS 8 or later

#### Windows Subsystem for Linux (WSL)
- WSL2 recommended (WSL1 has performance issues)
- Ubuntu 20.04 or later distro installed in WSL

## Prerequisites

### 1. Install Yocto Build Dependencies

#### On Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    git curl chrpath diffstat gawk \
    sed bzip2 texinfo python3 python3-pip \
    python3-pexpect xz-utils debianutils \
    iputils-ping wget ca-certificates \
    build-essential cpio time rsync \
    bc xterm gcc g++ make \
    lz4 pzstd zstd
```

#### On Fedora
```bash
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y \
    git diffstat texinfo chrpath \
    socat python3 python3-pip \
    python3-pexpect xz which SDL-devel curl \
    lz4 pzstd zstd
```

#### On openSUSE
```bash
sudo zypper install -y \
    git diffstat texinfo chrpath \
    socat python3 python3-pip \
    python3-pexpect xz which cpio \
    curl ca-certificates build-essential \
    lz4 pzstd zstd
```

### 2. Configure System Locale

BitBake requires a UTF-8 locale to be available. This is typically en_US.UTF-8 but C.utf8 is also acceptable.

#### Check Available Locales
```bash
locale -a | grep -i utf
```

#### Generate en_US.UTF-8 (if not available)

On Ubuntu/Debian:
```bash
sudo locale-gen en_US.UTF-8
sudo update-locale LANG=en_US.UTF-8
```

On Fedora/RHEL:
```bash
sudo localedef -i en_US -f UTF-8 en_US.UTF-8
```

**Note for WSL2:** If locale generation fails in WSL2 (common in sandboxed environments), the build scripts will automatically fall back to C.utf8, which is equivalent for build purposes.

### 3. Install Docker and Docker Compose

The build produces a Docker Compose stack, so it's helpful to have Docker available for testing.

#### Docker Installation
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Add user to docker group (requires re-login to take effect)
newgrp docker

# Verify installation
docker --version
docker-compose --version
```

### 4. (WSL Only) Configure WSL2 for Optimal Performance

Edit or create `~/.wslconfig` on Windows:

```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
localhostForwarding=true
```

Restart WSL2:
```bash
# On Windows PowerShell
wsl --shutdown
wsl
```

## Setting Up the Build Environment

### 1. Create Build Workspace

```bash
# Create dedicated workspace directory
mkdir -p ~/yocto-workspace
cd ~/yocto-workspace

# Set environment variable (add to ~/.bashrc to persist)
export YOCTO_WORKSPACE=$HOME/yocto-workspace
```

### 2. Clone the Repository

```bash
cd $YOCTO_WORKSPACE
git clone https://github.com/avgerion/ha-grocy-openProject-yocto.git
cd ha-grocy-openProject-yocto
```

### 3. Fetch Yocto Layers

The build uses standard Yocto layers plus our custom layer. Fetch the required dependencies:

```bash
# Create a layers directory
mkdir -p $YOCTO_WORKSPACE/layers
cd $YOCTO_WORKSPACE/layers

# Clone required Yocto layers
git clone git://git.yoctoproject.org/poky -b kirkstone
git clone https://github.com/openembedded/meta-openembedded.git -b kirkstone
git clone https://github.com/agherzan/meta-raspberrypi.git -b kirkstone
git clone https://github.com/opencontainers/meta-virtualization.git -b kirkstone
```

### 4. Set Up Build Directory

```bash
cd $YOCTO_WORKSPACE

# Create a dedicated build directory
mkdir -p build
cd build

# Initialize the build environment using poky
source ../layers/poky/oe-init-build-env ../build .

# This will create the build/conf directory
```

### 5. Configure Yocto Build

Copy the sample configuration files from the repository:

```bash
cd $YOCTO_WORKSPACE/build/conf

# Copy sample bblayers.conf
cp ../../ha-grocy-openProject-yocto/yocto/conf/bblayers.conf.sample bblayers.conf

# Copy sample local.conf
cp ../../ha-grocy-openProject-yocto/yocto/conf/local.conf.sample local.conf
```

Edit `bblayers.conf` to update layer paths:

```bash
# Open bblayers.conf in editor
nano bblayers.conf
```

Update the paths to match your actual layer directories. Common updates needed:

```bash
# Find these lines and update paths:
${TOPDIR}/../layers/poky/meta
${TOPDIR}/../layers/poky/meta-poky
${TOPDIR}/../layers/meta-openembedded/meta-oe
${TOPDIR}/../layers/meta-openembedded/meta-python
${TOPDIR}/../layers/meta-raspberrypi
${TOPDIR}/../layers/meta-virtualization
${TOPDIR}/../../ha-grocy-openProject-yocto/yocto/layers/meta-ha-grocy-openproject
```

Edit `local.conf` to set build variables:

```bash
nano local.conf
```

Key settings to verify/update:

```bash
# Raspberry Pi 3/4 target
MACHINE = "raspberrypi4"      # or "raspberrypi3" for Pi 3

# Build performance
BB_NUMBER_THREADS = "4"       # Match your CPU cores
PARALLEL_MAKE = "-j 4"        # Match your CPU cores

# Package formats
PACKAGE_CLASSES = "package_ipk"

# Build timezone
DEFAULT_TIMEZONE = "UTC"      # Change as needed

# Image features (optional)
EXTRA_IMAGE_FEATURES = "ssh-server-openssh"
```

## Building the Image

### 1. Start Build Environment

```bash
cd $YOCTO_WORKSPACE/build

# Re-source the build environment if starting a new terminal
source ../layers/poky/oe-init-build-env ../build .
```

### 2. Build the Image

```bash
# Build ha-grocy-openproject-image
bitbake ha-grocy-openproject-image

# This may take 1-4 hours depending on your hardware and internet speed
# Subsequent builds will be faster due to caching
```

### 3. Monitor Build Progress

The first build will:
- Download source files for all recipes (30-60 min)
- Build all dependencies from source
- Create the final image

Progress is shown in the terminal. Key milestones:
```
Parsing recipes...
Building dependencies...
[Progress: 1%, 2%, ...]
Preparing runqueue...
```

### Build Output

After successful build, find artifacts in:

```bash
$YOCTO_WORKSPACE/build/tmp/deploy/images/raspberrypi4/

# Key files:
# - ha-grocy-openproject-image-raspberrypi4.rootfs.wic.bz2  (bootable image)
# - ha-grocy-openproject-image-raspberrypi4.rootfs.tar.gz   (for container builds)
```

## Writing Image to SD Card

### On Linux

```bash
# Insert SD card and identify it (usually /dev/sdb or /dev/sdc)
lsblk

# Decompress and write image (CAUTION: This will erase the SD card)
cd $YOCTO_WORKSPACE/build/tmp/deploy/images/raspberrypi4/

# Backup the device first to verify it's the right one!
sudo dd if=ha-grocy-openproject-image-raspberrypi4.rootfs.wic.bz2 \
        of=/dev/sdX \
        bs=1M status=progress

# Safely eject
sudo eject /dev/sdX
```

### On Windows (with WSL)

```bash
# List disks (PowerShell, as Administrator)
wmic logicaldisk get name

# Or use diskpart
diskpart
list disk

# In WSL, access the disk via /mnt/[drive]/
# (Use with extreme caution - easily corrupts drives)

# Better: Use Raspberry Pi Imager (GUI application) available for Windows
# Download from https://www.raspberrypi.com/software/
```

### Using Balena Etcher (Recommended)

Download [Balena Etcher](https://www.balena.io/etcher/) for your OS:

1. Extract the .wic.bz2 file first:
   ```bash
   bunzip2 ha-grocy-openproject-image-raspberrypi4.rootfs.wic.bz2
   ```

2. Open Balena Etcher
3. Select the resulting `.wic` file
4. Select your SD card
5. Click Flash

## Troubleshooting Build Issues

### Out of Disk Space

```bash
# Check disk usage
df -h $YOCTO_WORKSPACE

# Clean build artifacts (keeps downloaded sources)
cd $YOCTO_WORKSPACE/build
bitbake -c cleanall ha-grocy-openproject-image

# Remove all build cache
rm -rf $YOCTO_WORKSPACE/build/tmp
```

### Out of Memory During Build

Reduce parallel build jobs in `build/conf/local.conf`:

```bash
BB_NUMBER_THREADS = "2"   # Reduce from 4
PARALLEL_MAKE = "-j 2"    # Reduce from 4
```

### Network Issues (Slow Downloads)

```bash
# Retry failed downloads
bitbake ha-grocy-openproject-image -c fetchall

# Once downloads complete, build without network
# (use local mirrors)
```

### Build Hangs or Crashes

```bash
# Resume build from where it stopped
bitbake ha-grocy-openproject-image

# Or start fresh with sanity checks
bitbake ha-grocy-openproject-image -c clean
bitbake ha-grocy-openproject-image
```

### Checking Logs

Build logs are located in:

```bash
# Individual recipe build logs
$YOCTO_WORKSPACE/build/tmp/work/*/ha-grocy-openproject-*/temp/log.do_*

# Full build log
$YOCTO_WORKSPACE/build/tmp/log.do_* (if available)
```

## Post-Build Testing

### 1. Boot the Image

Insert the SD card into your Raspberry Pi and power on. First boot may take 2-3 minutes.

### 2. Access via SSH

Once booted, verify connectivity:

```bash
# Find device on network (adjust hostname as needed)
ping rpi.local
# or
ping 192.168.1.XXX  # Replace with actual IP

# SSH to device
ssh root@rpi.local
# Default password varies; check Yocto configuration

# Or from device's config environment
cat /etc/ha-grocy-openproject/ha-grocy-openproject.env
```

### 3. Verify Services

```bash
# Check systemd service status
systemctl status ha-grocy-openproject.service

# Check Docker containers
docker ps

# View service logs
journalctl -u ha-grocy-openproject.service -f
```

### 4. Access Web Interfaces

- Grocy: `http://rpi.local:9283`
- OpenProject: `http://rpi.local:8080`

## Development Workflow

### Quick Rebuilds (After Code Changes)

If you only modify recipes or layer configuration:

```bash
cd $YOCTO_WORKSPACE/build

# Clean only the image (keeps dependencies)
bitbake -c clean ha-grocy-openproject-image

# Rebuild
bitbake ha-grocy-openproject-image
```

### Modifying Custom Layer

To make changes to `meta-ha-grocy-openproject`:

1. Edit files in `ha-grocy-openProject-yocto/yocto/layers/meta-ha-grocy-openproject/`
2. Run:
   ```bash
   cd $YOCTO_WORKSPACE/build
   bitbake -c clean ha-grocy-openproject-image
   bitbake ha-grocy-openproject-image
   ```

### BitBake Command Reference

```bash
# Fetch all sources
bitbake ha-grocy-openproject-image -c fetchall

# Parse recipes (verify syntax)
bitbake ha-grocy-openproject-image -c parse

# Show build plan without building
bitbake -g ha-grocy-openproject-image

# Build specific recipe
bitbake ha-grocy-openproject-stack

# Clean specific recipe
bitbake -c clean recipe-name

# Show layers
bitbake-layers show-layers

# Show recipes in layer
bitbake-layers show-recipes meta-ha-grocy-openproject
```

## Performance Optimization

### Reduce Build Time

1. **Use shared downloads directory** (across multiple builds):

   ```bash
   # In build/conf/local.conf, add:
   DL_DIR = "${TOPDIR}/../../downloads"
   ```

2. **Enable sstate cache sharing**:

   ```bash
   # In build/conf/local.conf
   SSTATE_DIR = "${TOPDIR}/../../sstate-cache"
   ```

3. **Use prebuilt binaries** (if available):

   ```bash
   # Configure to use binary packages when possible
   PREFERRED_PROVIDER_virtual/kernel = "linux-yocto"
   ```

4. **Parallel jobs on multi-core systems**:

   ```bash
   # In build/conf/local.conf
   BB_NUMBER_THREADS = "8"   # for 8-core CPU
   PARALLEL_MAKE = "-j 8"
   ```

## Running on CI/CD Self-Hosted Runners

Once you have a working local setup, you can export the build environment to a GitHub self-hosted runner:

### Export Build Environment

```bash
# On your local machine
cd $YOCTO_WORKSPACE
tar czf yocto-workspace-backup.tar.gz build/ layers/ downloads/ sstate-cache/

# Transfer to CI runner machine
scp yocto-workspace-backup.tar.gz ci-user@runner-host:/home/ci-user/

# On CI runner, extract
cd /home/ci-user
tar xzf yocto-workspace-backup.tar.gz
```

### Sync with Repository

Each time you update the repository:

```bash
cd $YOCTO_WORKSPACE/ha-grocy-openProject-yocto
git pull origin main
```

## Maintenance

### Update Layers

Periodically update layers to get bug fixes and security updates:

```bash
cd $YOCTO_WORKSPACE/layers

for dir in poky meta-openembedded meta-raspberrypi meta-virtualization; do
    cd $dir
    git fetch origin
    git checkout kirkstone
    cd ..
done
```

### Clean Up Old Build Artifacts

```bash
# Remove old deployment files (keeping latest)
cd $YOCTO_WORKSPACE/build/tmp/deploy/images/raspberrypi4/
rm -f *.wic.bz2.old *.tar.gz.old
```

## Resources and Further Reading

- [Yocto Project Manual](https://docs.yoctoproject.org/)
- [Raspberry Pi Yocto Layer](https://meta-raspberrypi.readthedocs.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Home Assistant Documentation](https://developers.home-assistant.io/)

## Support

For issues specific to this project:

1. Check [README.md](README.md) for project overview
2. Check [CI_CD_GUIDE.md](CI_CD_GUIDE.md) for GitHub Actions setup
3. Open an issue on [GitHub](https://github.com/avgerion/ha-grocy-openProject-yocto/issues)

Include in your issue:
- Your OS and hardware specs
- Step where build failed
- Full error message and logs
- Output of `bitbake --version` and `git --version`
