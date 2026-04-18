from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class ScheduleRepository(ABC):
    @abstractmethod
    def list_schedules(self) -> List[Dict]:
        pass

    @abstractmethod
    def get_schedule(self, schedule_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def create_schedule(self, data: Dict) -> str:
        pass

    @abstractmethod
    def update_schedule(self, schedule_id: str, data: Dict) -> None:
        pass

    @abstractmethod
    def delete_schedule(self, schedule_id: str) -> None:
        pass

    @abstractmethod
    def get_match_team(self, schedule_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def set_match_team(self, schedule_id: str, team_data: Dict) -> None:
        pass

    @abstractmethod
    def delete_match_team(self, schedule_id: str) -> None:
        pass

    @abstractmethod
    def list_participants(self, schedule_id: str) -> List[Dict]:
        pass

    @abstractmethod
    def set_participants(self, schedule_id: str, participants: List[Dict]) -> None:
        pass

    @abstractmethod
    def add_participant(self, schedule_id: str, member_id: str, goals: int = 0, assists: int = 0) -> None:
        pass

    @abstractmethod
    def remove_participant(self, schedule_id: str, member_id: str) -> None:
        pass