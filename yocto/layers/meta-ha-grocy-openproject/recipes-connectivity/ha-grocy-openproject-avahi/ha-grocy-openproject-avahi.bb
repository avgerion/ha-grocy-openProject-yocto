SUMMARY = "Avahi service announcements for Grocy/OpenProject bridge"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835c9145a16dbf44f4f302a6f4e7b8b"

SRC_URI = "file://ha-grocy-openproject.service"

S = "${WORKDIR}"

RDEPENDS:${PN} += "avahi-daemon"

FILES:${PN} += "${sysconfdir}/avahi/services/ha-grocy-openproject.service"

do_install() {
    install -d ${D}${sysconfdir}/avahi/services
    install -m 0644 ${WORKDIR}/ha-grocy-openproject.service ${D}${sysconfdir}/avahi/services/ha-grocy-openproject.service
}
