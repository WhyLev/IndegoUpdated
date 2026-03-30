# PyIndego Integration Guide

## Overview

This Home Assistant custom component integrates with Bosch Indego lawn mowers through the `pyIndego` Python library. This document explains where PyIndego is imported and how to modify the integration to use a forked or updated version of PyIndego.

## Where PyIndego is Imported

### 1. Dependency Declaration (manifest.json)

**File:** `custom_components/indego/manifest.json`

```json
{
  "requirements": ["pyIndego==3.2.2", "svgutils==0.3.4"],
  "loggers": ["custom_components.indego", "pyIndego"]
}
```

This is the **primary location** where the PyIndego version is specified. Home Assistant uses this manifest file to install the required dependencies.

### 2. Python Import Locations

#### Main Integration File
**File:** `custom_components/indego/__init__.py:40`
```python
from pyIndego import IndegoAsyncClient
```

This file uses `IndegoAsyncClient` to:
- Create API client instances (line 530)
- Communicate with the Bosch Indego API
- Manage mower state and operations
- Handle data updates

#### Configuration Flow
**File:** `custom_components/indego/config_flow.py:15`
```python
from pyIndego import IndegoAsyncClient
```

This file uses `IndegoAsyncClient` to:
- Validate user credentials during setup (line 160)
- Retrieve available mowers from the Bosch API
- Configure the integration

### 3. Debug Logging Configuration

**File:** `README.md:182`
```yaml
logger:
  logs:
    custom_components.indego: debug
    pyIndego: debug
```

This configuration enables debug logging for the pyIndego library.

## How to Use a Forked PyIndego Version

If you've forked PyIndego and want to use your updated version, follow these steps:

### Method 1: Using a Git Repository (Recommended)

1. **Update the manifest.json file** to point to your forked repository:

```json
{
  "requirements": ["pyIndego @ git+https://github.com/YOUR_USERNAME/pyIndego.git@YOUR_BRANCH"],
  "loggers": ["custom_components.indego", "pyIndego"]
}
```

Replace:
- `YOUR_USERNAME` with your GitHub username
- `YOUR_BRANCH` with the branch name (e.g., `main`, `develop`, or a specific branch)

You can also specify a specific commit:
```json
"requirements": ["pyIndego @ git+https://github.com/YOUR_USERNAME/pyIndego.git@COMMIT_SHA"]
```

### Method 2: Using PyPI (If You Published Your Fork)

If you've published your fork to PyPI under a different name:

```json
{
  "requirements": ["your-pyindego-fork==1.0.0"],
  "loggers": ["custom_components.indego", "your-pyindego-fork"]
}
```

### Method 3: Local Development

For local development and testing:

1. Install your forked PyIndego in development mode:
   ```bash
   pip install -e /path/to/your/pyIndego/fork
   ```

2. Update manifest.json to remove the version constraint temporarily:
   ```json
   {
     "requirements": ["pyIndego"],
     "loggers": ["custom_components.indego", "pyIndego"]
   }
   ```

3. Restart Home Assistant to use your local version.

### Method 4: Using a Specific Version or Tag

If your fork has tagged releases:

```json
{
  "requirements": ["pyIndego @ git+https://github.com/YOUR_USERNAME/pyIndego.git@v4.0.0"],
  "loggers": ["custom_components.indego", "pyIndego"]
}
```

## Important Notes

### No Code Changes Required

**You do NOT need to modify the Python import statements** (`from pyIndego import IndegoAsyncClient`). As long as your fork:
- Maintains the same package name (`pyIndego`)
- Exports `IndegoAsyncClient` in the same way
- Maintains API compatibility

The imports will continue to work without any changes to `__init__.py` or `config_flow.py`.

### Compatibility Considerations

When creating an updated PyIndego version, ensure:

1. **API Compatibility:** The `IndegoAsyncClient` class maintains the same interface:
   - Constructor parameters
   - Public methods
   - Return types
   - Exception handling

2. **Dependencies:** If your fork adds new dependencies, they should be included in your PyIndego package's `setup.py` or `pyproject.toml`.

3. **Breaking Changes:** If you make breaking changes, you'll need to update the integration code in `__init__.py` and `config_flow.py` accordingly.

### Testing Your Changes

1. Update `manifest.json` with your forked PyIndego URL
2. Restart Home Assistant
3. Check logs for any import or runtime errors:
   ```yaml
   logger:
     logs:
       custom_components.indego: debug
       pyIndego: debug
   ```
4. Test the integration functionality:
   - Add a new mower via the UI
   - Verify mower state updates
   - Test mower commands (mow, pause, dock)
   - Check sensor values

## Example: Complete Fork Integration

Here's a complete example of updating the manifest for a forked PyIndego:

**Original manifest.json:**
```json
{
  "domain": "indego",
  "name": "Bosch Indego Mower",
  "config_flow": true,
  "documentation": "https://github.com/sander1988/Indego",
  "dependencies": ["application_credentials"],
  "codeowners": ["@whylev", "@sander1988"],
  "requirements": ["pyIndego==3.2.2", "svgutils==0.3.4"],
  "iot_class": "cloud_push",
  "version": "5.7.8",
  "loggers": ["custom_components.indego", "pyIndego"]
}
```

**Updated manifest.json with forked PyIndego:**
```json
{
  "domain": "indego",
  "name": "Bosch Indego Mower",
  "config_flow": true,
  "documentation": "https://github.com/sander1988/Indego",
  "dependencies": ["application_credentials"],
  "codeowners": ["@whylev", "@sander1988"],
  "requirements": ["pyIndego @ git+https://github.com/YOUR_USERNAME/pyIndego.git@main", "svgutils==0.3.4"],
  "iot_class": "cloud_push",
  "version": "5.7.8",
  "loggers": ["custom_components.indego", "pyIndego"]
}
```

## Troubleshooting

### Issue: Home Assistant doesn't install the new version

**Solution:**
1. Remove the integration
2. Restart Home Assistant
3. Clear Home Assistant's pip cache: `rm -rf /config/deps/`
4. Restart again
5. Reinstall the integration

### Issue: Import errors after updating

**Solution:**
- Verify your fork exports `IndegoAsyncClient` properly
- Check that the package structure matches the original
- Review the pyIndego `__init__.py` to ensure proper exports

### Issue: Runtime errors with the forked version

**Solution:**
- Enable debug logging (see above)
- Check for API compatibility issues
- Verify all methods used by the integration are implemented
- Review the integration's usage of IndegoAsyncClient in `__init__.py:530` and `config_flow.py:160`

## Summary

To use your forked PyIndego version:

1. ✅ **Update manifest.json** - This is the ONLY required change
2. ❌ **Do NOT modify** `__init__.py` imports - They will work automatically
3. ❌ **Do NOT modify** `config_flow.py` imports - They will work automatically
4. ✅ **Maintain API compatibility** - Keep the same `IndegoAsyncClient` interface
5. ✅ **Test thoroughly** - Enable debug logging and verify all functionality

The integration is designed to be flexible with PyIndego versions as long as API compatibility is maintained.
