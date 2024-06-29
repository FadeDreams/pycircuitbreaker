
import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Optional

class CircuitBreakerState:
    CLOSED = 'closed'
    OPEN = 'open'
    HALF_OPEN = 'half_open'

class CircuitBreaker:
    def __init__(self, max_failures: int, timeout: float, pause_time: float, max_consecutive_successes: int):
        self._lock = threading.Lock()
        self.state = CircuitBreakerState.CLOSED
        self.consecutive_failures = 0
        self.total_failures = 0
        self.total_successes = 0
        self.max_failures = max_failures
        self.timeout = timeout
        self.open_timeout = datetime.min
        self.pause_time = pause_time
        self.consecutive_successes = 0
        self.max_consecutive_successes = max_consecutive_successes
        self.on_open: Optional[Callable[[], None]] = None
        self.on_close: Optional[Callable[[], None]] = None
        self.on_half_open: Optional[Callable[[], None]] = None

    def execute(self, fn: Callable[[], Optional[Exception]]) -> Optional[Exception]:
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if datetime.now() > self.open_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    if self.on_half_open:
                        self.on_half_open()
                else:
                    return Exception("circuit breaker is open")

            if self.state == CircuitBreakerState.HALF_OPEN:
                err = fn()
                if err is None:
                    self.consecutive_successes += 1
                    self.total_successes += 1
                    if self.consecutive_successes >= self.max_consecutive_successes:
                        self.reset()
                else:
                    self.trip()
                time.sleep(self.pause_time)
                return err

            err = fn()
            if err is None:
                self.reset()
                self.total_successes += 1
            else:
                self.consecutive_failures += 1
                self.total_failures += 1
                if self.consecutive_failures >= self.max_failures:
                    self.trip()
            return err

    def trip(self):
        self.state = CircuitBreakerState.OPEN
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.open_timeout = datetime.now() + timedelta(seconds=self.timeout)
        if self.on_open:
            self.on_open()

    def reset(self):
        self.state = CircuitBreakerState.CLOSED
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        if self.on_close:
            self.on_close()

    def set_on_open(self, callback: Callable[[], None]):
        self.on_open = callback

    def set_on_close(self, callback: Callable[[], None]):
        self.on_close = callback

    def set_on_half_open(self, callback: Callable[[], None]):
        self.on_half_open = callback
