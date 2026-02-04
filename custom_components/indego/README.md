# Bosch Indego Mower Integration for Home Assistant

This is a custom component for integrating Bosch Indego lawn mowers with Home Assistant.

## Installation

1. Copy the entire `indego` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Add the integration through the Home Assistant UI (Configuration -> Integrations -> Add Integration -> Search for "Bosch Indego Mower")

## Features

This integration provides:
- **Vacuum Entity**: Control your mower like a vacuum cleaner (legacy support)
- **Lawn Mower Entity**: Native lawn mower entity support (Home Assistant 2023.9+)
- **Binary Sensors**: Online status, update available, alerts
- **Sensors**: Battery level, mower state, lawn mowed percentage, runtime, next mowing time, and more

## Integrated PyIndego Library

This custom component now includes the PyIndego library directly in the `pyindego_api` subfolder, so you don't need to install it separately. All dependencies are self-contained within this folder.

### Structure
```
custom_components/indego/
├── pyindego_api/           # Integrated PyIndego API library
│   ├── indego_async_client.py
│   ├── indego_base_client.py
│   ├── indego_client.py
│   ├── const.py
│   ├── helpers.py
│   ├── states.py
│   └── version.py
├── __init__.py             # Integration setup
├── config_flow.py          # Configuration flow
├── api.py                  # OAuth2 session handling
├── vacuum.py               # Vacuum entity
├── lawn_mower.py           # Lawn mower entity
├── binary_sensor.py        # Binary sensors
├── sensor.py               # Sensors
├── const.py                # Constants
└── manifest.json           # Integration manifest
```

## Configuration

This integration uses OAuth2 authentication with Bosch SingleKey ID. You'll need to:
1. Have a Bosch SingleKey ID account with your Indego mower registered
2. Follow the configuration flow in Home Assistant to authenticate

## Support

For issues and support, please visit:
- GitHub Repository: https://github.com/sander1988/Indego
- Home Assistant Community: https://community.home-assistant.io/

## Credits

- Original integration by @sander1988, @eavanvalkenburg, @jm-73
- PyIndego library integrated for standalone usage
