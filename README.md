# Datadog Enhanced

Enhanced Datadog integration for Home Assistant with improved tagging support.

## Features

This integration is based on the official Home Assistant Datadog integration, with the following enhancement:

- **Device Class Tagging**: Automatically adds `entity_type` tags based on the entity's `device_class` attribute (e.g., `temperature`, `humidity`, `battery`)
- **Maintains Compatibility**: All original Datadog integration features remain intact
- **Selective Tagging**: Only adds `entity_type` tag when `device_class` is present

## Example

For a sensor with `device_class: "temperature"`:

**Standard Datadog Integration:**
```
Metric: hass.sensor
Tags: entity:sensor.living_room_temperature
```

**Datadog Enhanced:**
```
Metric: hass.sensor
Tags:
  - entity:sensor.living_room_temperature
  - entity_type:temperature
```

This allows for better filtering and aggregation in Datadog dashboards by entity type across all your sensors.

## Installation

### Manual Installation

1. Copy the `custom_components/datadog_enhanced` folder to your Home Assistant `custom_components` directory:
   ```
   <config_directory>/custom_components/datadog_enhanced/
   ```

2. Restart Home Assistant

3. Add the integration via the UI:
   - Go to **Settings** → **Devices & Services**
   - Click **Add Integration**
   - Search for **Datadog Enhanced**
   - Enter your Datadog Agent host, port, and configuration

### HACS Installation

This integration can be installed via HACS (Home Assistant Community Store):

1. Add this repository as a custom repository in HACS
2. Search for "Datadog Enhanced" in HACS
3. Install and restart Home Assistant
4. Add via UI as described above

## Configuration

Configuration is done through the Home Assistant UI with the same options as the standard Datadog integration:

- **Host**: Hostname or IP address of your Datadog Agent (default: `127.0.0.1`)
- **Port**: Port the Datadog Agent is listening on (default: `8125`)
- **Prefix**: Metric prefix to use (default: `hass`)
- **Rate**: Sample rate of UDP packets (default: `1`)

## Requirements

- Home Assistant 2024.1.0 or newer
- Datadog Agent running and accessible
- Python package: `datadog==0.52.0` (automatically installed)

## Supported Entity Types

The integration will add `entity_type` tags for any entity with a `device_class` attribute, including:

**Sensors:**
- temperature, humidity, battery, power, energy
- pressure, illuminance, signal_strength
- And 50+ more sensor types

**Binary Sensors:**
- door, window, motion, occupancy
- smoke, gas, moisture, etc.

**Other Entities:**
- Any entity type with a `device_class` attribute

## Compatibility

This integration is compatible with:
- All Home Assistant installations (Core, Container, OS, Supervised)
- Datadog Agent v6 and v7
- StatsD protocol

## Development

Based on the official Home Assistant Datadog integration with minimal modifications for enhanced tagging.

## License

Apache License 2.0 - See LICENSE file for details

## Credits

- Original Datadog integration by the Home Assistant team
- Enhanced tagging implementation by Connor Ameres
