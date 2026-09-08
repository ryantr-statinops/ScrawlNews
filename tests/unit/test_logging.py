import json
import logging

from src.utils.logging import setup_logging


def test_json_formatter_emits_valid_json(capfd):
    setup_logging("DEBUG")
    logger = logging.getLogger("test_json")
    logger.info("hello")
    out = capfd.readouterr().out
    record = json.loads(out)
    assert record["level"] == "INFO"
    assert record["logger"] == "test_json"
    assert record["msg"] == "hello"
    assert "ts" in record


def test_json_formatter_includes_run_id_and_stage(capfd):
    setup_logging("DEBUG")
    logger = logging.getLogger("test_ctx")
    logger.info("step", extra={"run_id": "abc-123", "stage": "fetch"})
    record = json.loads(capfd.readouterr().out)
    assert record["run_id"] == "abc-123"
    assert record["stage"] == "fetch"


def test_json_formatter_includes_exception(capfd):
    setup_logging("DEBUG")
    logger = logging.getLogger("test_exc")
    try:
        raise ValueError("boom")
    except ValueError:
        logger.exception("caught")
    record = json.loads(capfd.readouterr().out)
    assert record["level"] == "ERROR"
    assert "ValueError" in record["exc"]


def test_json_formatter_omits_optional_fields_when_absent(capfd):
    setup_logging("DEBUG")
    logger = logging.getLogger("test_no_ctx")
    logger.info("plain")
    record = json.loads(capfd.readouterr().out)
    assert "run_id" not in record
    assert "stage" not in record
    assert "exc" not in record
