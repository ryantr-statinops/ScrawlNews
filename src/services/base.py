from abc import ABC, abstractmethod
from typing import Any


class BaseService(ABC):
    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the service logic."""
        pass
