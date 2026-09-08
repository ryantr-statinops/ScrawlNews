from src.config import settings
from src.repositories.config_repo import ConfigRepository
from src.worker.celery_app import celery_app
from src.worker.scheduler import ConfigurableScheduler


def make_scheduler():
    return ConfigurableScheduler(app=celery_app, schedule={}, max_interval=300, lazy=True)


def test_scheduler_uses_config_override():
    config_repo = ConfigRepository(settings.database_url)
    config_repo.set("schedule_interval_hours", "6")
    scheduler = make_scheduler()
    schedule = scheduler.get_schedule()
    entry = schedule["pipeline.run"]
    from celery.schedules import schedule as interval_schedule

    assert isinstance(entry.schedule, interval_schedule)
    assert entry.schedule.run_every.total_seconds() == 6 * 3600


def test_scheduler_defaults_to_settings():
    scheduler = make_scheduler()
    schedule = scheduler.get_schedule()
    entry = schedule["pipeline.run"]
    assert entry.schedule.run_every.total_seconds() == settings.schedule_interval_hours * 3600


def test_scheduler_keeps_existing_entries():
    from celery.schedules import schedule as interval_schedule

    existing = {"other": "entry"}
    scheduler = ConfigurableScheduler(
        app=celery_app, schedule=existing, max_interval=300, lazy=True
    )
    schedule = scheduler.get_schedule()
    assert schedule["other"] == "entry"
    assert "pipeline.run" in schedule
    assert isinstance(schedule["pipeline.run"].schedule, interval_schedule)
