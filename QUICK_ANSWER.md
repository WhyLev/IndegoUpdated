# Quick Answer: PyIndego Integration in Home Assistant

## Where is PyIndego imported?

The integration imports PyIndego in **3 locations**:

### 1. **Dependency Declaration (MOST IMPORTANT)**
**File:** `custom_components/indego/manifest.json` (Line 8)
```json
"requirements": ["pyIndego==3.2.2", "svgutils==0.3.4"]
```
This is where Home Assistant knows which version to install.

### 2. **Main Integration Code**
**File:** `custom_components/indego/__init__.py` (Line 40)
```python
from pyIndego import IndegoAsyncClient
```
Used for all mower operations and API communication.

### 3. **Configuration Flow**
**File:** `custom_components/indego/config_flow.py` (Line 15)
```python
from pyIndego import IndegoAsyncClient
```
Used for validating credentials and discovering mowers during setup.

---

## How to use your forked PyIndego version?

### ✅ What you NEED to change:

**ONLY ONE FILE:** `custom_components/indego/manifest.json`

Change line 8 from:
```json
"requirements": ["pyIndego==3.2.2", "svgutils==0.3.4"]
```

To:
```json
"requirements": ["pyIndego @ git+https://github.com/YOUR_USERNAME/pyIndego.git@YOUR_BRANCH", "svgutils==0.3.4"]
```

Replace:
- `YOUR_USERNAME` with your GitHub username
- `YOUR_BRANCH` with your branch name (e.g., `main`, `develop`)

### ❌ What you DON'T need to change:

- ❌ **NO changes** to `__init__.py`
- ❌ **NO changes** to `config_flow.py`
- ❌ **NO changes** to import statements

The imports will automatically use your forked version!

---

## Complete Example

### Original manifest.json:
```json
{
  "domain": "indego",
  "name": "Bosch Indego Mower",
  "requirements": ["pyIndego==3.2.2", "svgutils==0.3.4"],
  "loggers": ["custom_components.indego", "pyIndego"]
}
```

### Updated for YOUR fork:
```json
{
  "domain": "indego",
  "name": "Bosch Indego Mower",
  "requirements": ["pyIndego @ git+https://github.com/YOUR_USERNAME/pyIndego.git@main", "svgutils==0.3.4"],
  "loggers": ["custom_components.indego", "pyIndego"]
}
```

---

## Installation Steps

1. Fork the PyIndego repository on GitHub
2. Make your changes to PyIndego
3. Fork THIS repository (the integration)
4. Edit `custom_components/indego/manifest.json` with your PyIndego fork URL
5. Install your forked integration in Home Assistant
6. Restart Home Assistant

That's it! Home Assistant will now use YOUR version of PyIndego.

---

## Important Notes

### API Compatibility
Your PyIndego fork MUST maintain compatibility:
- Keep the `IndegoAsyncClient` class
- Keep the same method signatures
- Keep the same return types

If you change the API, you'll also need to update `__init__.py` and `config_flow.py`.

### Specific Commit or Tag
You can also point to a specific commit or tag:

```json
// Specific commit:
"requirements": ["pyIndego @ git+https://github.com/YOUR_USERNAME/pyIndego.git@abc123def"]

// Specific tag:
"requirements": ["pyIndego @ git+https://github.com/YOUR_USERNAME/pyIndego.git@v4.0.0"]
```

---

## Need More Details?

See the complete guide: [PYINDEGO_INTEGRATION_GUIDE.md](PYINDEGO_INTEGRATION_GUIDE.md)

Includes:
- Detailed explanations of all import locations
- Multiple installation methods
- Troubleshooting guide
- Testing procedures
- Compatibility considerations
