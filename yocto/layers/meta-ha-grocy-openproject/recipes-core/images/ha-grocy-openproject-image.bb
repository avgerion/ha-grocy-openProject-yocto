SUMMARY = "Raspberry Pi image with Docker, Grocy and OpenProject stack"
LICENSE = "MIT"

require recipes-core/images/core-image-minimal.bb

IMAGE_FEATURES += "ssh-server-openssh"

IMAGE_INSTALL:append = " \
    docker \
    docker-compose \
    avahi-daemon \
    python3 \
    ha-grocy-openproject-stack \
    ha-grocy-openproject-avahi \
"
