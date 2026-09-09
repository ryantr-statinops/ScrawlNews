from src.config import settings
from src.repositories.config_repo import ConfigRepository
from src.worker.celery_app import celery_app
from src.worker.scheduler import ConfigurableScheduler


def make_scheduler():
    return ConfigurableScheduler(app=celery_app, schedule={}, max_interval=300, lazy=True)


def test_scheduler_uses_config_override():
    config_repo = ConfigRepository(settings.database_url)
    config_repo.set("schedule_times", "06:30,18:00")
    scheduler = make_scheduler()
    schedule = scheduler.get_schedule()
    assert set(schedule) == {"pipeline.run.0", "pipeline.run.1"}
    assert schedule["pipeline.run.0"].schedule.hour == {6}
    assert schedule["pipeline.run.0"].schedule.minute == {30}


def test_scheduler_defaults_to_settings():
    scheduler = make_scheduler()
    schedule = scheduler.get_schedule()
    assert set(schedule) == {"pipeline.run.0", "pipeline.run.1", "pipeline.run.2"}
    assert schedule["pipeline.run.0"].schedule.hour == {8}


def test_scheduler_keeps_existing_entries():
    existing = {"other": "entry"}
    scheduler = ConfigurableScheduler(
        app=celery_app, schedule=existing, max_interval=300, lazy=True
    )
    schedule = scheduler.get_schedule()
    assert schedule["other"] == "entry"
    assert "pipeline.run.0" in schedule
