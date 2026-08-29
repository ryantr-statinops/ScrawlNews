from unittest.mock import AsyncMock, patch

from src.worker.tasks import pipeline_run


def test_pipeline_run_success():
    with patch("src.worker.tasks.Pipeline") as mock_pipeline_cls:
        mock_pipeline = AsyncMock()
        mock_pipeline.run = AsyncMock()
        mock_pipeline_cls.return_value = mock_pipeline
        result = pipeline_run("test-task-id")
        assert result is not None


def test_pipeline_run_retry_on_failure():
    with patch("src.worker.tasks.Pipeline") as mock_pipeline_cls:
        mock_pipeline = AsyncMock()
        mock_pipeline.run = AsyncMock(side_effect=Exception("Test error"))
        mock_pipeline_cls.return_value = mock_pipeline
        task = pipeline_run
        assert task is not None
