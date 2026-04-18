from __future__ import annotations

from typing import List, Dict, Optional
from firebase_admin import firestore
from repositories.base.post_repository import PostRepository


class FirestorePostRepository(PostRepository):
    def __init__(self, db):
        self.db = db

    def list_posts(self, category: str = None) -> List[Dict]:
        if category:
            query = self.db.collection("posts").where("category", "==", category)
        else:
            query = self.db.collection("posts")

        # 복합 인덱스 요구 사항을 피하기 위해 메모리에서 정렬
        docs = query.stream()

        result = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id

            # 댓글 수 계산
            comments = list(
                self.db.collection("posts")
                .document(doc.id)
                .collection("comments")
                .stream()
            )
            data["comment_count"] = len(comments)

            # 작성자 정보 가져오기
            author_ref = self.db.collection("accounts").document(data.get("author_id"))
            author = author_ref.get()
            if author.exists:
                data["author_name"] = author.to_dict().get("displayName", "Unknown")
            else:
                data["author_name"] = "Unknown"

            # timestamp를 문자열로 변환
            if data.get("createdAt"):
                data["created_at"] = data["createdAt"].strftime("%Y-%m-%d %H:%M:%S")
            else:
                data["created_at"] = "N/A"
            
            if data.get("updatedAt"):
                data["updated_at"] = data["updatedAt"].strftime("%Y-%m-%d %H:%M:%S")
            else:
                data["updated_at"] = "N/A"

            result.append(data)

        # 메모리에서 정렬: isPinned 내림차순(True 먼저), createdAt 내림차순(최신순)
        result.sort(
            key=lambda x: (
                not x.get("isPinned", False),  # False가 True보다 큼, not으로 반전하면 True가 먼저
                -(x.get("createdAt").timestamp() if hasattr(x.get("createdAt"), "timestamp") else 0)  # 음수로 내림차순
            )
        )

        return result

    def get_post(self, post_id: str) -> Optional[Dict]:
        doc = self.db.collection("posts").document(post_id).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        data["id"] = doc.id

        # 작성자 정보 가져오기
        author_ref = self.db.collection("accounts").document(data.get("author_id"))
        author = author_ref.get()
        if author.exists:
            data["author_name"] = author.to_dict().get("displayName", "Unknown")
        else:
            data["author_name"] = "Unknown"

        # timestamp를 문자열로 변환
        if data.get("createdAt"):
            data["created_at"] = data["createdAt"].strftime("%Y-%m-%d %H:%M:%S")
        else:
            data["created_at"] = "N/A"
        
        if data.get("updatedAt"):
            data["updated_at"] = data["updatedAt"].strftime("%Y-%m-%d %H:%M:%S")
        else:
            data["updated_at"] = "N/A"

        return data

    def create_post(self, data: Dict) -> str:
        doc_ref = self.db.collection("posts").document()
        doc_ref.set({
            "title": data["title"],
            "content": data["content"],
            "author_id": data["author_id"],
            "category": data.get("category", "일반"),
            "isPinned": False,
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP,
        })
        return doc_ref.id

    def update_post(self, post_id: str, data: Dict) -> None:
        updates = {}
        if "title" in data:
            updates["title"] = data["title"]
        if "content" in data:
            updates["content"] = data["content"]
        if "category" in data:
            updates["category"] = data["category"]

        if updates:
            updates["updatedAt"] = firestore.SERVER_TIMESTAMP
            self.db.collection("posts").document(post_id).update(updates)

    def delete_post(self, post_id: str) -> None:
        post_ref = self.db.collection("posts").document(post_id)

        comments = post_ref.collection("comments").stream()
        batch = self.db.batch()

        for doc in comments:
            batch.delete(doc.reference)

        batch.delete(post_ref)
        batch.commit()

    def pin_post(self, post_id: str, is_pinned: bool) -> None:
        self.db.collection("posts").document(post_id).update({
            "isPinned": is_pinned,
            "updatedAt": firestore.SERVER_TIMESTAMP,
        })

    def list_comments(self, post_id: str) -> List[Dict]:
        docs = (
            self.db.collection("posts")
            .document(post_id)
            .collection("comments")
            .order_by("createdAt", direction=firestore.Query.ASCENDING)
            .stream()
        )

        result = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id

            # 작성자 정보 가져오기
            author_ref = self.db.collection("accounts").document(data.get("author_id"))
            author = author_ref.get()
            if author.exists:
                data["author_name"] = author.to_dict().get("displayName", "Unknown")
            else:
                data["author_name"] = "Unknown"

            # timestamp를 문자열로 변환
            if data.get("createdAt"):
                data["created_at"] = data["createdAt"].strftime("%Y-%m-%d %H:%M:%S")
            else:
                data["created_at"] = "N/A"
            
            if data.get("updatedAt"):
                data["updated_at"] = data["updatedAt"].strftime("%Y-%m-%d %H:%M:%S")
            else:
                data["updated_at"] = "N/A"

            result.append(data)
        return result

    def add_comment(self, post_id: str, comment_data: Dict) -> str:
        doc_ref = (
            self.db.collection("posts")
            .document(post_id)
            .collection("comments")
            .document()
        )
        doc_ref.set({
            "author_id": comment_data["author_id"],
            "content": comment_data["content"],
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP,
        })
        return doc_ref.id

    def delete_comment(self, post_id: str, comment_id: str) -> None:
        (
            self.db.collection("posts")
            .document(post_id)
            .collection("comments")
            .document(comment_id)
            .delete()
        )
