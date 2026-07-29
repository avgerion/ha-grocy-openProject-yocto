# ha-grocy-openProject-yocto

Yocto-based Raspberry Pi 3/4 image implementation that provides:

- Docker runtime on Raspberry Pi
- Grocy container service
- OpenProject container service
- Bonjour/mDNS service announcements for easier Home Assistant onboarding
- Home Assistant custom integration to configure and monitor both services
- **Public access via Home Assistant proxy (NEW)**

The repository layout keeps **Home Assistant integration files at root** and **Yocto assets in `/yocto`**, which is required for custom integration compatibility.

## Quick Start

### For Home Assistant Users

1. **Install the integration:**
   - Copy `/custom_components/home_ops_bridge` to your HA `custom_components` directory
   - Restart Home Assistant
   - Add integration from Settings → Devices & Services

2. **Access remotely with embedded iframes:**
   - Follow the [Setup Guide](SETUP_GUIDE.md) for iframe proxy setup
   - Add custom Lovelace cards to your dashboard
   - Access Grocy and OpenProject through your HA public URL

### For Yocto Builders

1. **Build the image:**
   - Follow Yocto setup instructions below
   - Run `bitbake ha-grocy-openproject-image`

2. **Handle CI/CD:**
   - See [CI/CD Guide](CI_CD_GUIDE.md) for free tier options
   - Recommended: Build locally, publish to GitHub Releases

## Repository Layout

- `/custom_components/home_ops_bridge/` - Home Assistant integration (config flow + zeroconf + proxy + sensors)
- `/custom_components/home_ops_bridge/www/` - Custom Lovelace card components
- `/yocto/` - Yocto config samples and custom layer for the stack

## Features

### Home Assistant Integration

**Configuration:**
- Config flow for Grocy URL, OpenProject URL, optional Grocy API token
- Zeroconf bootstrap (pre-fills discovered host)
- Support for local and remote URLs

**Connectivity Validation:**
- Periodic health checks for both services
- Diagnostic sensors showing status

**Public Access via Proxy (NEW):**
- HTTP proxy endpoints for authenticated users
- Embedded iframe support via custom Lovelace cards
- No additional firewall rules needed
- Full HTTPS and authentication via Home Assistant
- Support for all HTTP methods (GET, POST, PUT, DELETE, PATCH)

**Diagnostic Sensors:**
- Grocy endpoint status
- OpenProject endpoint status
- Overall bridge status

### Yocto Implementation Details

`yocto/layers/meta-ha-grocy-openproject` provides:

- `ha-grocy-openproject-image.bb` image recipe
- `ha-grocy-openproject-stack` recipe:
  - installs Docker Compose stack file
  - installs environment config file
  - installs/auto-enables systemd service to start containers at boot
- `ha-grocy-openproject-avahi` recipe:
  - installs Avahi service announcement file

### Runtime Files Installed by Stack Recipe

- `/usr/share/ha-grocy-openproject/docker-compose.yml`
- `/etc/ha-grocy-openproject/ha-grocy-openproject.env`
- `ha-grocy-openproject.service` (systemd)

Edit `/etc/ha-grocy-openproject/ha-grocy-openproject.env` on device to customize:

- Grocy/OpenProject ports
- image tags
- timezone
- OpenProject hostname
- OpenProject secret key

## Build Instructions

1. Install Yocto prerequisites on Linux host.
2. Fetch layers (`poky`, `meta-openembedded`, `meta-raspberrypi`, `meta-virtualization`).
3. Add this repository layer path to your build setup using:
   - `yocto/conf/bblayers.conf.sample`
   - `yocto/conf/local.conf.sample`
4. Build:

```bash
bitbake ha-grocy-openproject-image
```

See [CI/CD Guide](CI_CD_GUIDE.md) for information about using GitHub Actions (free tier) or self-hosted runners.

## First Boot Behavior

On first boot, the image:

- starts Docker
- starts `ha-grocy-openproject.service`
- launches Grocy and OpenProject containers
- announces `*_ha-grocy-openproject*` over mDNS/Bonjour using Avahi

Default HTTP endpoints:

- Grocy: `http://<device-hostname-or-ip>:9283`
- OpenProject: `http://<device-hostname-or-ip>:8080`

## Home Assistant Integration

Integration domain: `home_ops_bridge`

### Install Integration

1. Copy `/custom_components/home_ops_bridge` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add **Home Ops Bridge** from Integrations.
4. Confirm detected or manual URLs for Grocy/OpenProject.

### Public Access via Proxy

Once the integration is installed, you can access Grocy and OpenProject publicly through your Home Assistant instance:

1. Follow the [Setup Guide](SETUP_GUIDE.md)
2. Add custom Lovelace cards to your dashboard
3. Access through your HA public HTTPS URL

**Architecture:**
- Home Assistant acts as an authenticated proxy
- Requests forwarded to internal Grocy/OpenProject services
- Only authenticated HA users can access
- Encrypted via HA's SSL certificate

**Proxy Endpoints:**
- `/api/home_ops_bridge/grocy_proxy/*` - Forward to Grocy
- `/api/home_ops_bridge/openproject_proxy/*` - Forward to OpenProject

See [Setup Guide](SETUP_GUIDE.md) for detailed instructions.

## Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - How to set up and use the proxy for public access
- **[CI_CD_GUIDE.md](CI_CD_GUIDE.md)** - GitHub Actions and CI/CD options (free tier and beyond)
- **[README.md](README.md)** - This file

## Notes

- This implementation is intended for local/home-lab networks with a public Home Assistant instance.
- For public-facing deployments, always use HTTPS and keep Home Assistant updated.
- Replace `OPENPROJECT_SECRET_KEY_BASE` in the env file before production use.
- The proxy feature requires the custom Lovelace cards to be installed.

## Security Considerations

- All proxy traffic goes through Home Assistant's authentication
- HTTPS is required for remote access (use Nabu Casa or reverse proxy)
- Grocy API token (if configured) is sent with requests from HA server only
- No additional network exposure beyond HA's existing public access

## Version History

- **v0.3.0** - Add public access proxy and custom Lovelace cards
- **v0.2.0** - Initial release with config flow and sensors
- **v0.1.0** - Early development release

