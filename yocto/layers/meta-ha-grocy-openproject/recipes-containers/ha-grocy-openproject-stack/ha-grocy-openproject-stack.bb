SUMMARY = "Runtime stack for Grocy and OpenProject containers"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835c9145a16dbf44f4f302a6f4e7b8b"

SRC_URI = " \
    file://docker-compose.yml \
    file://ha-grocy-openproject.env \
    file://ha-grocy-openproject.service \
"

S = "${WORKDIR}"

inherit systemd

RDEPENDS:${PN} += "docker bash"

SYSTEMD_SERVICE:${PN} = "ha-grocy-openproject.service"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"

FILES:${PN} += " \
    ${systemd_system_unitdir}/ha-grocy-openproject.service \
    ${datadir}/ha-grocy-openproject/docker-compose.yml \
    ${sysconfdir}/ha-grocy-openproject/ha-grocy-openproject.env \
"

do_install() {
    install -d ${D}${datadir}/ha-grocy-openproject
    install -d ${D}${sysconfdir}/ha-grocy-openproject
    install -d ${D}${systemd_system_unitdir}

    install -m 0644 ${WORKDIR}/docker-compose.yml ${D}${datadir}/ha-grocy-openproject/docker-compose.yml
    install -m 0640 ${WORKDIR}/ha-grocy-openproject.env ${D}${sysconfdir}/ha-grocy-openproject/ha-grocy-openproject.env
    install -m 0644 ${WORKDIR}/ha-grocy-openproject.service ${D}${systemd_system_unitdir}/ha-grocy-openproject.service
}
