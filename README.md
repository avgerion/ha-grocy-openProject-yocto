# ha-grocy-openProject-yocto

Yocto-based Raspberry Pi 3/4 image skeleton that targets:

- Docker runtime
- Grocy server
- OpenProject server
- Easy onboarding with Home Assistant

This repository is structured so the **Home Assistant custom integration remains at repository root** and **Yocto lives in a subdirectory** (`yocto/`), as required by Home Assistant integration conventions.

## Repository layout

- `/custom_components/home_ops_bridge/` - Home Assistant custom integration skeleton
- `/yocto/` - Yocto build skeleton (configs, layer, image recipe)

## Quick start (skeleton)

> This is a starter scaffold, not a fully production-ready build.

1. Install Yocto build prerequisites on your Linux host.
2. Add required upstream layers (for example `poky`, `meta-openembedded`, `meta-raspberrypi`, `meta-virtualization`).
3. Copy sample configs:
   - `yocto/conf/bblayers.conf.sample` -> your build `conf/bblayers.conf`
   - `yocto/conf/local.conf.sample` -> your build `conf/local.conf`
4. Add `meta-ha-grocy-openproject` layer from this repository.
5. Build image:

   ```bash
   bitbake ha-grocy-openproject-image
   ```

## Home Assistant connectivity approach

The included `home_ops_bridge` integration skeleton is designed to evolve toward:

- mDNS/Bonjour (zeroconf) discovery of the Raspberry Pi service endpoint
- Config flow for Grocy/OpenProject URLs and API credentials
- Single integration entry in Home Assistant to connect both services

The Yocto image scaffold includes `avahi-daemon` so device/service discovery can be enabled in future iterations.

## Next implementation steps

- Add concrete Grocy/OpenProject service containers/systemd units in Yocto layer
- Add integration API clients and entity/platform implementations
- Add secure credential storage and diagnostics
