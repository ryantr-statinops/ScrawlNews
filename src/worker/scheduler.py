from celery import schedules
from celery.beat import ScheduleEntry, Scheduler

from src.config import settings
from src.repositories.config_repo import ConfigRepository


class ConfigurableScheduler(Scheduler):
    """Beat scheduler that reads the briefing interval from config on each tick.

    Lets ``/settings frequency <hours>`` take effect without restarting beat.
    """

    def get_schedule(self) -> dict:
        config_repo = ConfigRepository(settings.database_url)
        override = config_repo.get("schedule_interval_hours")
        interval_hours = int(override) if override else settings.schedule_interval_hours
        interval_hours = max(1, interval_hours)
        self.data["pipeline.run"] = ScheduleEntry(
            name="pipeline.run",
            task="pipeline.run",
            schedule=schedules.schedule(run_every=interval_hours * 3600),
        )
        return self.data
