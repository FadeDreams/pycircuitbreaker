
### pysafecircuit
This Python module provides a CircuitBreaker class that helps in managing failures and timeouts gracefully using the circuit breaker pattern.

### Overview
The CircuitBreaker class manages three states:

- CLOSED: Normal operation state where calls are allowed.
- OPEN: Circuit is open due to excessive failures, and calls are blocked.
- HALF_OPEN: After a timeout, the circuit allows a limited number of calls to determine if the underlying service is available.
### Dependencies
- threading: For thread synchronization using locks.
- time: For pausing execution between retries.
- datetime and timedelta: For handling timeout calculations.
- typing: For type annotations to specify callback function signatures.

### Example Usage
```py
import time
import random
from datetime import datetime, timedelta
from typing import Callable, Optional
from pysafecircuit import CircuitBreaker

def example_function():
    # Simulate some operation that may fail
    if random.random() < 0.5:
        return Exception("an error occurred")
    return None

def main():
    # Create a new circuit breaker with max_failures=3, timeout=5 seconds, pause_time=1 second, and max_consecutive_successes=2
    cb = CircuitBreaker(max_failures=3, timeout=5, pause_time=1, max_consecutive_successes=2)

    # Set up the callbacks
    cb.set_on_open(lambda: print("Circuit breaker opened!"))
    cb.set_on_close(lambda: print("Circuit breaker closed!"))
    cb.set_on_half_open(lambda: print("Circuit breaker is half-open, trying again..."))

    # Execute the function with circuit breaker protection
    for i in range(20):
        err = cb.execute(example_function)
        if err:
            print(f"Attempt {i+1} failed: {err}")
        else:
            print(f"Attempt {i+1} succeeded")
        time.sleep(1)  # Simulate some delay between attempts

if __name__ == "__main__":
    main()

```
### Features
- State Management: Tracks the state of the circuit (CLOSED, OPEN, HALF_OPEN).
- Callbacks: Allows setting callbacks for when the circuit breaker transitions between states (set_on_open, set_on_close, set_on_half_open).
- Retry Logic: Implements retry logic with configurable parameters (max_failures, timeout, pause_time, max_consecutive_successes).
