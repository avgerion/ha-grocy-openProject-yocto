# ha-grocy-openProject-yocto

Yocto-based Raspberry Pi 3/4 image implementation that provides:

- Docker runtime on Raspberry Pi
- Grocy container service
- OpenProject container service
- Bonjour/mDNS service announcements for easier Home Assistant onboarding
- Home Assistant custom integration to configure and monitor both services

The repository layout keeps **Home Assistant integration files at root** and **Yocto assets in `/yocto`**, which is required for custom integration compatibility.

## Repository layout

- `/custom_components/home_ops_bridge/` - Home Assistant integration (config flow + zeroconf + status sensors)
- `/yocto/` - Yocto config samples and custom layer for the stack

## Yocto implementation details

### Included Yocto layer

`yocto/layers/meta-ha-grocy-openproject` provides:

- `ha-grocy-openproject-image.bb` image recipe
- `ha-grocy-openproject-stack` recipe:
  - installs Docker Compose stack file
  - installs environment config file
  - installs/auto-enables systemd service to start containers at boot
- `ha-grocy-openproject-avahi` recipe:
  - installs Avahi service announcement file

### Runtime files installed by the stack recipe

- `/usr/share/ha-grocy-openproject/docker-compose.yml`
- `/etc/ha-grocy-openproject/ha-grocy-openproject.env`
- `ha-grocy-openproject.service` (systemd)

Edit `/etc/ha-grocy-openproject/ha-grocy-openproject.env` on device to customize:

- Grocy/OpenProject ports
- image tags
- timezone
- OpenProject hostname
- OpenProject secret key

## Build instructions

1. Install Yocto prerequisites on Linux host.
2. Fetch layers (`poky`, `meta-openembedded`, `meta-raspberrypi`, `meta-virtualization`).
3. Add this repository layer path to your build setup using:
   - `yocto/conf/bblayers.conf.sample`
   - `yocto/conf/local.conf.sample`
4. Build:

```bash
bitbake ha-grocy-openproject-image
```

## First boot behavior

On first boot, the image:

- starts Docker
- starts `ha-grocy-openproject.service`
- launches Grocy and OpenProject containers
- announces `*_ha-grocy-openproject*` over mDNS/Bonjour using Avahi

Default HTTP endpoints:

- Grocy: `http://<device-hostname-or-ip>:9283`
- OpenProject: `http://<device-hostname-or-ip>:8080`

## Home Assistant integration

Integration domain: `home_ops_bridge`

Features implemented:

- Config flow for Grocy URL, OpenProject URL, optional Grocy API token
- Zeroconf bootstrap (pre-fills discovered host)
- Connectivity validation against:
  - `GET <grocy_url>/api/system/info`
  - `GET <openproject_url>/api/v3`
- Diagnostic sensors:
  - Grocy endpoint status
  - OpenProject endpoint status
  - Overall bridge status

### Install integration in Home Assistant

1. Copy `/custom_components/home_ops_bridge` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add **Home Ops Bridge** from Integrations.
4. Confirm detected or manual URLs for Grocy/OpenProject.

## Notes

- This implementation is intended for local/home-lab networks.
- Replace `OPENPROJECT_SECRET_KEY_BASE` in the env file before production use.
