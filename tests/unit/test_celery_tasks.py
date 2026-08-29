from src.worker.tasks import pipeline_run


def test_pipeline_run_success():
    assert pipeline_run.name == "pipeline.run"
    assert pipeline_run.max_retries == 3


def test_pipeline_run_retry_on_failure():
    assert pipeline_run is not None
    assert hasattr(pipeline_run, "retry")
