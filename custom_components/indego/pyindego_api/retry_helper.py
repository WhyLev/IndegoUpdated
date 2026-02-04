"""Retry helper with exponential backoff for API requests."""
import asyncio
import logging
import random
from typing import Callable, Optional, TypeVar, Any

_LOGGER = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """Initialize retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt number.
        
        Args:
            attempt: The attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        if self.jitter:
            # Add jitter: random value between 0.5x and 1.0x of the calculated delay
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay


async def async_retry_with_backoff(
    func: Callable[..., Any],
    *args,
    config: Optional[RetryConfig] = None,
    retry_on_exceptions: tuple = (asyncio.TimeoutError, ConnectionError),
    **kwargs
) -> Optional[Any]:
    """Execute an async function with retry and exponential backoff.
    
    Args:
        func: Async function to execute
        *args: Positional arguments for func
        config: RetryConfig instance (uses default if None)
        retry_on_exceptions: Tuple of exception types to retry on
        **kwargs: Keyword arguments for func
        
    Returns:
        Result from func or None if all retries failed
    """
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(config.max_retries + 1):
        try:
            result = await func(*args, **kwargs)
            
            # If we get here on a retry, log success
            if attempt > 0:
                _LOGGER.info(
                    "Request succeeded after %d retry attempt(s)",
                    attempt
                )
            
            return result
            
        except retry_on_exceptions as exc:
            last_exception = exc
            
            if attempt < config.max_retries:
                delay = config.get_delay(attempt)
                _LOGGER.warning(
                    "Request failed (attempt %d/%d): %s. Retrying in %.2f seconds...",
                    attempt + 1,
                    config.max_retries + 1,
                    str(exc),
                    delay
                )
                await asyncio.sleep(delay)
            else:
                _LOGGER.error(
                    "Request failed after %d attempts: %s",
                    config.max_retries + 1,
                    str(exc)
                )
                
        except Exception as exc:
            # Don't retry on unexpected exceptions
            _LOGGER.error(
                "Request failed with unexpected error: %s",
                str(exc)
            )
            raise
    
    # All retries exhausted
    if last_exception:
        _LOGGER.error(
            "All retry attempts exhausted. Last exception: %s",
            str(last_exception)
        )
    
    return None


class CircuitBreaker:
    """Circuit breaker pattern implementation for API health."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception,
    ):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of consecutive failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type that counts as a failure
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self._failure_count = 0
        self._last_failure_time = None
        self._state = "closed"  # closed, open, half_open
        
    @property
    def state(self) -> str:
        """Get current circuit state."""
        return self._state
    
    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count
        
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit."""
        if self._state != "open":
            return False
            
        if self._last_failure_time is None:
            return False
            
        import time
        time_since_failure = time.time() - self._last_failure_time
        return time_since_failure >= self.recovery_timeout
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result from func
            
        Raises:
            Exception: If circuit is open or function fails
        """
        # Check if we should try to recover
        if self._should_attempt_reset():
            _LOGGER.info("Circuit breaker entering half-open state for recovery attempt")
            self._state = "half_open"
        
        # Reject if circuit is open
        if self._state == "open":
            raise Exception(
                f"Circuit breaker is OPEN. Too many failures "
                f"({self._failure_count}/{self.failure_threshold}). "
                f"Will retry after {self.recovery_timeout} seconds."
            )
        
        try:
            result = await func(*args, **kwargs)
            
            # Success - reset failure count
            if self._failure_count > 0:
                _LOGGER.info(
                    "Circuit breaker recovered after %d failures. Closing circuit.",
                    self._failure_count
                )
            self._failure_count = 0
            self._state = "closed"
            self._last_failure_time = None
            
            return result
            
        except self.expected_exception as exc:
            self._failure_count += 1
            
            import time
            self._last_failure_time = time.time()
            
            if self._failure_count >= self.failure_threshold:
                _LOGGER.error(
                    "Circuit breaker OPENED after %d consecutive failures",
                    self._failure_count
                )
                self._state = "open"
            else:
                _LOGGER.warning(
                    "Circuit breaker failure %d/%d: %s",
                    self._failure_count,
                    self.failure_threshold,
                    str(exc)
                )
                self._state = "closed"
            
            raise
    
    def reset(self):
        """Manually reset the circuit breaker."""
        _LOGGER.info("Circuit breaker manually reset")
        self._failure_count = 0
        self._state = "closed"
        self._last_failure_time = None
