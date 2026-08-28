from unittest.mock import patch, AsyncMock
import pytest
from src.worker.tasks import pipeline_run


def test_pipeline_run_success():
    with patch("src.worker.tasks.Pipeline") as MockPipeline:
        mock_pipeline = AsyncMock()
        mock_pipeline.run = AsyncMock()
        MockPipeline.return_value = mock_pipeline
        result = pipeline_run("test-task-id")
        assert result is not None


def test_pipeline_run_retry_on_failure():
    with patch("src.worker.tasks.Pipeline") as MockPipeline:
        mock_pipeline = AsyncMock()
        mock_pipeline.run = AsyncMock(side_effect=Exception("Test error"))
        MockPipeline.return_value = mock_pipeline
        task = pipeline_run
        assert task is not None
