import time

from src.utils.circuit_breaker import CircuitBreaker, State


def test_initial_state_is_closed():
    cb = CircuitBreaker("test", failure_threshold=3, cooldown_seconds=1)
    assert cb.state == State.CLOSED
    assert cb.allow_request() is True


def test_stays_closed_under_threshold():
    cb = CircuitBreaker("test", failure_threshold=3, cooldown_seconds=1)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == State.CLOSED
    assert cb.allow_request() is True


def test_opens_after_threshold():
    cb = CircuitBreaker("test", failure_threshold=3, cooldown_seconds=60)
    cb.record_failure()
    cb.record_failure()
    cb.record_failure()
    assert cb.state == State.OPEN
    assert cb.allow_request() is False


def test_half_open_after_cooldown():
    cb = CircuitBreaker("test", failure_threshold=2, cooldown_seconds=0.01)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == State.OPEN
    time.sleep(0.02)
    assert cb.state == State.HALF_OPEN
    assert cb.allow_request() is True


def test_closes_on_success_from_half_open():
    cb = CircuitBreaker("test", failure_threshold=2, cooldown_seconds=0.01)
    cb.record_failure()
    cb.record_failure()
    time.sleep(0.02)
    assert cb.state == State.HALF_OPEN
    cb.record_success()
    assert cb.state == State.CLOSED
    assert cb.allow_request() is True


def test_reopens_on_failure_from_half_open():
    cb = CircuitBreaker("test", failure_threshold=2, cooldown_seconds=0.01)
    cb.record_failure()
    cb.record_failure()
    time.sleep(0.02)
    assert cb.state == State.HALF_OPEN
    cb.record_failure()
    assert cb.state == State.OPEN
    assert cb.allow_request() is False


def test_success_resets_failure_count():
    cb = CircuitBreaker("test", failure_threshold=3, cooldown_seconds=1)
    cb.record_failure()
    cb.record_failure()
    cb.record_success()
    assert cb._failure_count == 0
    assert cb.allow_request() is True


def test_reset():
    cb = CircuitBreaker("test", failure_threshold=2, cooldown_seconds=60)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == State.OPEN
    cb.reset()
    assert cb.state == State.CLOSED
    assert cb._failure_count == 0
    assert cb.allow_request() is True


def test_to_dict():
    cb = CircuitBreaker("mybreaker", failure_threshold=5, cooldown_seconds=30)
    d = cb.to_dict()
    assert d["name"] == "mybreaker"
    assert d["state"] == "closed"
    assert d["failure_count"] == 0
    assert d["failure_threshold"] == 5
    assert d["cooldown_seconds"] == 30


def test_to_dict_reflects_state():
    cb = CircuitBreaker("x", failure_threshold=2, cooldown_seconds=60)
    cb.record_failure()
    cb.record_failure()
    d = cb.to_dict()
    assert d["state"] == "open"
    assert d["failure_count"] == 2
