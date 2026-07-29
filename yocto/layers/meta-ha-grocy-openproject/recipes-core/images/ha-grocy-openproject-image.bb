SUMMARY = "Raspberry Pi image with Docker, Grocy and OpenProject scaffold"
LICENSE = "MIT"

require recipes-core/images/core-image-minimal.bb

IMAGE_FEATURES += "ssh-server-openssh"

IMAGE_INSTALL:append = " \
    docker \
    docker-compose \
    avahi-daemon \
    python3 \
"
