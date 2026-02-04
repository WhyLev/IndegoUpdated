# Changelog - Version 5.8.0

## New Features & Improvements

### 🔄 Enhanced API Connectivity & Reliability

#### Exponential Backoff with Jitter
- **What it is**: Automatic retry mechanism for failed API requests
- **How it works**: 
  - Starts with 1 second delay
  - Exponentially increases: 1s → 2s → 4s → 8s → 16s → 32s (max: 60s)
  - Adds random jitter (50%-100% of calculated delay) to prevent thundering herd
  - Retries up to 3 times by default
- **Benefits**: Handles transient network issues gracefully without overwhelming the API

#### Circuit Breaker Pattern
- **What it is**: Prevents repeated calls to failing APIs
- **How it works**:
  - Tracks consecutive failures
  - Opens circuit after 5 consecutive failures
  - Waits 60 seconds before attempting recovery
  - Half-open state for testing if API is back
- **Benefits**: Saves battery and network bandwidth when API is down

#### Improved Error Handling
- Detailed error messages with request IDs for debugging
- Tracks API request count and error count
- Records last error for troubleshooting
- Circuit breaker state monitoring

#### Increased Timeouts
- Default timeout increased from 30s to 60s
- Better support for slow or congested networks
- Reduces false "offline" states

### 📡 New Sensors

#### Network Signal Sensor
- **Entity**: `sensor.indego_<serial>_network_signal`
- **State**: RSSI value in dBm (e.g., -77 dBm)
- **Attributes**:
  - `mcc`: Mobile Country Code
  - `mnc`: Mobile Network Code
  - `signal_mode`: Current connection mode
  - `network_count`: Number of available networks
  - `last_updated`: Timestamp of last update
- **Update Frequency**: Every 10 minutes
- **Use Cases**:
  - Monitor WiFi/mobile signal strength
  - Troubleshoot connectivity issues
  - Create automations based on signal quality

#### API Health Sensor
- **Entity**: `sensor.indego_<serial>_api_health`
- **State**: Circuit breaker state (`closed`, `open`, `half_open`, or `disabled`)
- **Attributes**:
  - `request_count`: Total API requests made
  - `error_count`: Total API errors encountered
  - `last_error`: Description of the most recent error
  - `circuit_breaker_state`: Current circuit state
  - `circuit_breaker_failures`: Consecutive failure count
- **Update Frequency**: Every 10 minutes
- **Use Cases**:
  - Monitor integration health
  - Get alerts when API has issues
  - Track reliability over time

### 🛠️ Code Quality Improvements

#### Consolidated Codebase
- Removed duplicate `pyIndego` directory
- All code now in `custom_components/indego/pyindego_api/`
- Cleaner, more maintainable structure
- Reduced confusion and sync issues

#### Better Testing
- All 103 existing tests passing
- Updated test imports for new structure
- Added support for testing retry logic

### 📊 Configuration Options

The following can be configured when initializing the client (for advanced users):

```python
IndegoAsyncClient(
    token="...",
    enable_retry=True,          # Enable retry logic (default: True)
    enable_circuit_breaker=True, # Enable circuit breaker (default: True)
)
```

### 🔮 Future Enhancements (Not Yet Implemented)

These are identified areas for future improvement:

1. **Predictive Setup Configuration**: Allow users to configure predictive mowing settings
2. **Configurable Update Intervals**: Let users adjust 10m/24h refresh schedules
3. **Location Tracking Features**: Optional GPS-based features for multi-property owners
4. **Enhanced Operating Data Triggers**: More intelligent refresh based on mower activities

## Technical Details

### Retry Configuration

Default retry configuration:
- Max retries: 3
- Base delay: 1.0 seconds
- Max delay: 60.0 seconds
- Exponential base: 2.0
- Jitter: Enabled

### Circuit Breaker Configuration

Default circuit breaker configuration:
- Failure threshold: 5 consecutive failures
- Recovery timeout: 60 seconds
- Expected exception type: All exceptions

### API Health Metrics

The integration now tracks:
- Total API requests
- Total API errors
- Last error message with timestamp
- Circuit breaker state and failure count

## Migration Notes

### For Users

No action required! This is a drop-in replacement that maintains backward compatibility.

### For Developers

If you're developing custom components based on this code:

1. Import paths have changed:
   - Old: `from pyIndego import IndegoAsyncClient`
   - New: `from custom_components.indego.pyindego_api import IndegoAsyncClient`

2. New properties available:
   - `client.api_health`: Returns dict with API health metrics

3. Test imports need updating:
   - See `tests/test_indego.py` for example

## Breaking Changes

None. All changes are backward compatible.

## Bug Fixes

- Fixed silent failures that previously returned `None` without logging
- Improved error messages for better debugging
- Fixed issue where mower appeared "offline" due to transient network issues

## Performance Improvements

- Reduced unnecessary API calls with circuit breaker
- Better handling of slow networks with increased timeouts
- Exponential backoff prevents API hammering during outages

## Dependencies

No new dependencies added. Uses existing:
- `aiohttp` (already required)
- `asyncio` (Python standard library)
- `random` (Python standard library)

## Acknowledgments

Based on the excellent work by:
- @jm-73
- @eavanvalkenburg  
- @sander1988

And the pyIndego library.
