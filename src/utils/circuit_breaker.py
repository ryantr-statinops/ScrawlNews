import logging
import time
from enum import Enum

logger = logging.getLogger(__name__)


class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """In-memory circuit breaker for external service calls.

    States:
        CLOSED   — normal operation, calls pass through.
        OPEN     — failures exceeded threshold; calls blocked until cooldown expires.
        HALF_OPEN — cooldown elapsed; one probe call allowed.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        cooldown_seconds: float = 60.0,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self._state = State.CLOSED
        self._failure_count = 0
        self._last_failure_time: float = 0.0

    @property
    def state(self) -> State:
        if self._state == State.OPEN:
            if time.monotonic() - self._last_failure_time >= self.cooldown_seconds:
                self._state = State.HALF_OPEN
        return self._state

    def allow_request(self) -> bool:
        current = self.state
        if current == State.CLOSED:
            return True
        if current == State.HALF_OPEN:
            return True
        return False

    def record_success(self) -> None:
        if self._state in (State.HALF_OPEN, State.OPEN):
            logger.info("Circuit breaker %s closed — probe succeeded", self.name)
        self._state = State.CLOSED
        self._failure_count = 0

    def record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.monotonic()
        if self._failure_count >= self.failure_threshold:
            if self._state != State.OPEN:
                logger.warning(
                    "Circuit breaker %s open — %d consecutive failures",
                    self.name,
                    self._failure_count,
                )
            self._state = State.OPEN

    def reset(self) -> None:
        self._state = State.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "cooldown_seconds": self.cooldown_seconds,
        }
