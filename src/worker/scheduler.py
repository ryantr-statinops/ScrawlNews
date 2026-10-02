from celery import schedules
from celery.beat import ScheduleEntry, Scheduler

from src.config import settings
from src.config_validation import validate_schedule_times, validate_timezone
from src.repositories.config_repo import ConfigRepository


class ConfigurableScheduler(Scheduler):
    """Beat scheduler that reads the briefing interval from config on each tick.

    Lets ``/settings frequency <hours>`` take effect without restarting beat.
    """

    def get_schedule(self) -> dict:
        config_repo = ConfigRepository(settings.database_url)
        times = config_repo.get("schedule_times") or settings.schedule_times
        timezone = config_repo.get("schedule_timezone") or settings.schedule_timezone
        try:
            validate_schedule_times(times)
            validate_timezone(timezone)
            entries = times.split(",")
        except (TypeError, ValueError):
            entries = settings.schedule_times.split(",")
            timezone = settings.schedule_timezone
        if entries:
            self.app.conf.timezone = timezone
            for index, item in enumerate(entries):
                hour, minute = (int(part) for part in item.split(":", 1))
                self.data[f"pipeline.run.{index}"] = ScheduleEntry(
                    name=f"pipeline.run.{index}",
                    task="pipeline.run",
                    schedule=schedules.crontab(hour=hour, minute=minute, app=self.app),
                )
        else:
            override = config_repo.get("schedule_interval_hours")
            interval_hours = int(override) if override else settings.schedule_interval_hours
            self.data["pipeline.run"] = ScheduleEntry(
                name="pipeline.run",
                task="pipeline.run",
                schedule=schedules.schedule(run_every=max(1, interval_hours) * 3600),
            )
        return self.data
