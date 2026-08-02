# Public Access to Grocy and OpenProject via Home Assistant

This guide explains how to access your Grocy and OpenProject interfaces publicly through your Home Assistant instance using embedded iframes.

## Architecture

```
Public Internet (HTTPS)
    ↓
Home Assistant (authenticated user session)
    ↓
HTTP Proxy Endpoints
    ↓
Grocy/OpenProject Containers (internal network)
```

**Key Security Features:**
- Only authenticated HA users can access
- HA's built-in SSL/HTTPS encryption
- Proxy runs on the same device as HA
- No additional ports or firewall rules needed

## How It Works

1. User logs into Home Assistant via public HTTPS URL
2. User adds custom cards to their HA dashboard
3. Custom cards load Grocy/OpenProject UIs via embedded iframes
4. Iframes make HTTP requests to Home Ops Bridge proxy endpoints
5. Proxy endpoints forward requests to internal Grocy/OpenProject services
6. Responses are returned through the authenticated HA session

## Prerequisites

- Home Assistant instance with public HTTPS access
- **Home Ops Bridge integration** installed via:
  - **HACS (Recommended)**: See [README.md](README.md) for HACS installation instructions
  - **Manual**: Copy `/custom_components/home_ops_bridge` to your `custom_components` directory
- User logged into Home Assistant

## Setup Instructions

### 1. Install the Home Ops Bridge Integration

**Option 1: Via HACS (Recommended)**

1. Open Home Assistant → **Settings → Devices & Services → Custom Repositories**
2. Add: `https://github.com/avgerion/ha-grocy-openProject-yocto` as **Integration**
3. Click **HACS → Integrations**
4. Search for **Home Ops Bridge**
5. Click **Install**
6. Restart Home Assistant
7. Go to **Settings → Devices & Services → Integrations**
8. Click **Create Automation**
9. Search for **Home Ops Bridge**
10. Enter your Grocy and OpenProject URLs
11. Confirm

**Option 2: Manual Installation**

Follow the standard installation in your Home Assistant instance:

1. Go to Settings → Devices & Services → Integrations
2. Click "Create Automation"
3. Search for "Home Ops Bridge"
4. Enter your Grocy and OpenProject URLs
5. Confirm

### 2. Add Custom Lovelace Cards

#### Copy Card Files

Copy the custom card JavaScript files to your Home Assistant `www` directory:

```bash
# Copy grocy card
cp custom_components/home_ops_bridge/www/grocy-card.js /path/to/ha/config/www/

# Copy openproject card  
cp custom_components/home_ops_bridge/www/openproject-card.js /path/to/ha/config/www/
```

#### Register Resources in Lovelace

Add the following to your Lovelace dashboard configuration (via UI or YAML):

**Via YAML:**

1. Go to Settings → Dashboards → Select your dashboard
2. Click the three-dot menu → Edit dashboard
3. Click the three-dot menu again → Raw configuration editor
4. Add to the resource section:

```yaml
resources:
  - url: /local/grocy-card.js
    type: module
  - url: /local/openproject-card.js
    type: module
```

**Via UI:**

1. Settings → Dashboards → Select dashboard
2. Edit dashboard
3. Bottom-right → Manage resources
4. Click "Create resource"
5. URL: `/local/grocy-card.js`, Type: `module`
6. Repeat for `openproject-card.js`

### 3. Add Cards to Dashboard

1. Edit your dashboard
2. Click "Add card"
3. Scroll down to "Custom cards"
4. Select "Grocy Iframe" or "OpenProject Iframe"

#### Card Configuration

**Grocy Card:**
```yaml
type: custom:grocy-iframe-card
title: Grocy
height: 800
```

**OpenProject Card:**
```yaml
type: custom:openproject-iframe-card
title: OpenProject
height: 900
```

**Optional Parameters:**
- `title` - Display title (default: "Grocy" or "OpenProject")
- `height` - iframe height in pixels (default: 800)

### 4. Access Remotely

Once configured:

1. Navigate to your HA instance remotely via HTTPS
2. Log in with your HA credentials
3. Navigate to the dashboard with the embedded cards
4. Grocy and OpenProject will load within the dashboard

## Proxy Endpoints

The integration exposes two proxy endpoints:

- `/api/home_ops_bridge/grocy_proxy/*` - Proxies to Grocy service
- `/api/home_ops_bridge/openproject_proxy/*` - Proxies to OpenProject service

**Endpoint Details:**
- Require Home Assistant authentication
- Support all HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Preserve request/response headers (except hop-by-hop headers)
- Support file uploads/downloads
- Handle websockets (when applicable)

### Direct Endpoint Access

You can also access the proxy endpoints directly for API calls:

```bash
# Get Grocy API info
curl -H "Authorization: ******" \
  https://<your-ha-domain>/api/home_ops_bridge/grocy_proxy/api/system/info
```

## Authentication & Security

### User Permissions

All users with access to the dashboard can access Grocy and OpenProject through the embedded cards.

### Grocy API Token (Optional)

If you've configured a Grocy API token in the Home Ops Bridge integration:

1. Open Settings → Devices & Services → Home Ops Bridge
2. Select Options
3. Enter your Grocy API token (if needed)

The token will be automatically included in requests to Grocy.

## Troubleshooting

### Cards Don't Load

**Check:**
1. Card JavaScript files are in `/config/www/`
2. Resources are registered in Lovelace configuration
3. Integration is properly configured with correct URLs
4. You're logged into Home Assistant

**Browser Console:**
- Open browser dev tools (F12)
- Check Console tab for errors
- Check Network tab to see proxy requests

### Grocy/OpenProject Returns "Offline"

**Check:**
1. Go to Settings → Devices & Services
2. Find "Home Ops Bridge"
3. Check if sensor shows "online" status
4. Verify URLs are correct in integration options
5. Check Home Assistant logs for errors

**Enable Debug Logging:**

Add to `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.home_ops_bridge: debug
    custom_components.home_ops_bridge.proxy: debug
```

### CORS Errors in Console

The proxy handles CORS headers automatically. If you see errors:

1. Check network request headers in browser dev tools
2. Verify integration is running correctly
3. Check Home Assistant logs for proxy errors

### Slow Performance

**Factors:**
- Network latency between HA and services
- Service performance
- Browser performance

**Optimization:**
- Ensure services (Grocy, OpenProject) are responsive
- Check network connectivity on HA device
- Consider iframe height to reduce rendering overhead

## Advanced Usage

### Embedding in Automations

You can use proxy endpoints in Home Assistant automations or scripts:

```yaml
service: home_ops_bridge.grocy_proxy
data:
  method: GET
  path: /api/system/info
```

### Direct iframe in Custom Cards

If you want to create your own custom card:

```html
<iframe 
  src="/api/home_ops_bridge/grocy_proxy/"
  sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-cookies"
></iframe>
```

### Backend Integration

Use the Home Ops Bridge proxy in template sensors:

```yaml
template:
  - sensor:
      - name: "Grocy Status"
        unique_id: grocy_status
        unit_of_measurement: "items"
        state: "{{ states('sensor.home_ops_bridge_grocy') }}"
```

## Performance Considerations

### Resource Usage

The proxy adds minimal overhead:
- Small memory footprint per request
- Streaming response handling
- Connection pooling via aiohttp

### Rate Limiting

Currently no rate limiting is implemented. For production use, consider:
- Adding rate limiting in reverse proxy (nginx)
- Implementing request throttling in integration
- Monitoring for unusual activity

### Caching

Responses are not cached by the proxy. Caching strategies:
- Browser cache (handled by HTTP headers)
- HTTP caching headers from origin services
- CDN (not applicable for local services)

## Limitations

1. **WebSocket Support**: Full WebSocket forwarding is not currently implemented
2. **File Upload Size**: Limited by Home Assistant's request size limits
3. **Concurrent Requests**: Handled by Home Assistant's async architecture
4. **Service Availability**: Proxy is only available when HA is running

## Future Enhancements

Potential improvements for future versions:
- [ ] WebSocket forwarding for real-time features
- [ ] Request rate limiting and throttling
- [ ] Caching layer for frequently accessed resources
- [ ] Request/response logging for debugging
- [ ] Performance metrics and monitoring
- [ ] Multi-tenancy support
- [ ] Per-service access control

## Support & Troubleshooting

For issues:

1. Check integration status in HA
2. Review Home Assistant logs
3. Check browser console for JavaScript errors
4. Verify network connectivity
5. Open an issue on GitHub with:
   - Home Assistant version
   - Integration version
   - Error logs
   - Steps to reproduce

## See Also

- [Home Ops Bridge Integration](../README.md)
- [Home Assistant Documentation](https://www.home-assistant.io/)
- [Grocy Documentation](https://github.com/grocy/grocy)
- [OpenProject Documentation](https://www.openproject.org/docs)
