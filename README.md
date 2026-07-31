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

1. **Install the integration via HACS (Recommended):**
   - Go to **Settings → Devices & Services → Custom Repositories**
   - Add: `https://github.com/avgerion/ha-grocy-openProject-yocto` as **Integration**
   - In **HACS → Integrations**, search for and install **Home Ops Bridge**
   - Restart Home Assistant
   - Add integration from **Settings → Devices & Services**

2. **Access remotely with embedded iframes:**
   - Follow the [Setup Guide](SETUP_GUIDE.md) for iframe proxy setup
   - Add custom Lovelace cards to your dashboard
   - Access Grocy and OpenProject through your HA public URL

### For Yocto Builders

1. **Build the image locally:**
   - See [Local Runner Setup Guide](LOCAL_RUNNER_SETUP.md) for detailed instructions
   - Requires Linux or WSL with 100+ GB disk space
   - Typical build time: 1-4 hours depending on hardware

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

## Building the Yocto Image

Complete build instructions for local and CI/CD environments are available in:

- **[LOCAL_RUNNER_SETUP.md](LOCAL_RUNNER_SETUP.md)** - Step-by-step guide for building locally on WSL or Linux
- **[CI_CD_GUIDE.md](CI_CD_GUIDE.md)** - Using GitHub Actions or self-hosted runners

Quick overview:

1. Install Yocto build dependencies on Linux or WSL
2. Fetch Yocto layers (poky, meta-openembedded, meta-raspberrypi, meta-virtualization)
3. Add this repository's layer path to your Yocto configuration
4. Run `bitbake ha-grocy-openproject-image`

**Disk Space Required**: 100+ GB free space
**Build Time**: 1-4 hours depending on hardware

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

### Install Integration (Recommended: HACS)

**Option 1: Install via HACS (Recommended)**

1. Open Home Assistant and go to **Settings → Devices & Services → Custom Repositories**
2. Add this repository: `https://github.com/avgerion/ha-grocy-openProject-yocto`
3. Select **Integration** as the category
4. Click **Create Repository**
5. Go to **HACS → Integrations**
6. Search for **Home Ops Bridge**
7. Click **Install**
8. Restart Home Assistant
9. Add **Home Ops Bridge** from **Settings → Devices & Services → Integrations**
10. Confirm detected or manual URLs for Grocy/OpenProject

**Option 2: Manual Installation**

1. Copy `/custom_components/home_ops_bridge` into your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add **Home Ops Bridge** from **Settings → Devices & Services → Integrations**
4. Confirm detected or manual URLs for Grocy/OpenProject

**HACS Benefits:**
- ✅ Automatic updates when new versions are released
- ✅ Version tracking and rollback support
- ✅ One-click installation and removal
- ✅ Integration appears in HACS dashboard

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
- **[LOCAL_RUNNER_SETUP.md](LOCAL_RUNNER_SETUP.md)** - Complete guide to build the Yocto image locally on WSL or Linux (free tier)
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

