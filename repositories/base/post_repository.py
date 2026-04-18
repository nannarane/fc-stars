from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class PostRepository(ABC):
    @abstractmethod
    def list_posts(self, category: str = None) -> List[Dict]:
        """게시물 목록 조회"""
        pass

    @abstractmethod
    def get_post(self, post_id: str) -> Optional[Dict]:
        """게시물 상세 조회"""
        pass

    @abstractmethod
    def create_post(self, data: Dict) -> str:
        """게시물 생성"""
        pass

    @abstractmethod
    def update_post(self, post_id: str, data: Dict) -> None:
        """게시물 수정"""
        pass

    @abstractmethod
    def delete_post(self, post_id: str) -> None:
        """게시물 삭제"""
        pass

    @abstractmethod
    def pin_post(self, post_id: str, is_pinned: bool) -> None:
        """게시물 공지 고정"""
        pass

    @abstractmethod
    def list_comments(self, post_id: str) -> List[Dict]:
        """댓글 목록 조회"""
        pass

    @abstractmethod
    def add_comment(self, post_id: str, comment_data: Dict) -> str:
        """댓글 추가"""
        pass

    @abstractmethod
    def delete_comment(self, post_id: str, comment_id: str) -> None:
        """댓글 삭제"""
        pass
