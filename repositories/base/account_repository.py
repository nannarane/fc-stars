from abc import ABC, abstractmethod
from typing import Optional, Dict, List


class AccountRepository(ABC):
    @abstractmethod
    def create_account(self, data: Dict) -> str:
        pass

    @abstractmethod
    def list_accounts(
        self,
        status: Optional[str] = None,
        role: Optional[str] = None,
    ) -> List[Dict]:
        pass

    @abstractmethod
    def get_account_by_email(self, email: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def get_account_by_uid(self, uid: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def approve_account(self, account_id: str, approver_id: str) -> None:
        pass

    @abstractmethod
    def reject_account(self, account_id: str, approver_id: str) -> None:
        pass

    @abstractmethod
    def suspend_account(self, account_id: str, approver_id: str) -> None:
        pass

    @abstractmethod
    def update_last_login(self, account_id: str) -> None:
        pass