from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class MemberRepository(ABC):
    @abstractmethod
    def list_members(self) -> List[Dict]:
        pass

    @abstractmethod
    def get_member(self, member_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def create_member(self, data: Dict) -> str:
        pass

    @abstractmethod
    def update_member(self, member_id: str, data: Dict) -> None:
        pass

    @abstractmethod
    def delete_member(self, member_id: str) -> None:
        pass

    @abstractmethod
    def add_guest_member(self, name: str, position: str = "게스트") -> str:
        pass

    @abstractmethod
    def delete_guest_member(self, member_id: str) -> None:
        pass