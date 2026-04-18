import sqlite3
from typing import List, Dict, Optional
from repositories.base.post_repository import PostRepository
from settings import SQLITE_DB_PATH


class SQLitePostRepository(PostRepository):
    def _conn(self):
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def list_posts(self, category: str = None) -> List[Dict]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            if category:
                cur.execute("""
                    SELECT 
                        p.id, p.title, p.content, p.author_id, p.category, p.is_pinned,
                        p.created_at, p.updated_at, a.display_name as author_name,
                        COUNT(c.id) as comment_count
                    FROM posts p
                    LEFT JOIN accounts a ON p.author_id = a.id
                    LEFT JOIN post_comments c ON p.id = c.post_id
                    WHERE p.category = ?
                    GROUP BY p.id
                    ORDER BY p.is_pinned DESC, p.created_at DESC
                """, (category,))
            else:
                cur.execute("""
                    SELECT 
                        p.id, p.title, p.content, p.author_id, p.category, p.is_pinned,
                        p.created_at, p.updated_at, a.display_name as author_name,
                        COUNT(c.id) as comment_count
                    FROM posts p
                    LEFT JOIN accounts a ON p.author_id = a.id
                    LEFT JOIN post_comments c ON p.id = c.post_id
                    GROUP BY p.id
                    ORDER BY p.is_pinned DESC, p.created_at DESC
                """)
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_post(self, post_id: str) -> Optional[Dict]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    p.id, p.title, p.content, p.author_id, p.category, p.is_pinned,
                    p.created_at, p.updated_at, a.display_name as author_name
                FROM posts p
                LEFT JOIN accounts a ON p.author_id = a.id
                WHERE p.id = ?
            """, (post_id,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def create_post(self, data: Dict) -> str:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO posts (title, content, author_id, category)
                VALUES (?, ?, ?, ?)
            """, (
                data["title"],
                data["content"],
                data["author_id"],
                data.get("category", "일반")
            ))
            conn.commit()
            return str(cur.lastrowid)
        finally:
            conn.close()

    def update_post(self, post_id: str, data: Dict) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            fields = []
            params = []

            if "title" in data:
                fields.append("title = ?")
                params.append(data["title"])
            if "content" in data:
                fields.append("content = ?")
                params.append(data["content"])
            if "category" in data:
                fields.append("category = ?")
                params.append(data["category"])

            if not fields:
                return

            fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(post_id)

            cur.execute(f"""
                UPDATE posts
                SET {", ".join(fields)}
                WHERE id = ?
            """, params)
            conn.commit()
        finally:
            conn.close()

    def delete_post(self, post_id: str) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM posts WHERE id = ?", (post_id,))
            conn.commit()
        finally:
            conn.close()

    def pin_post(self, post_id: str, is_pinned: bool) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE posts
                SET is_pinned = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (1 if is_pinned else 0, post_id))
            conn.commit()
        finally:
            conn.close()

    def list_comments(self, post_id: str) -> List[Dict]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    c.id, c.post_id, c.author_id, c.content,
                    c.created_at, c.updated_at, a.display_name as author_name
                FROM post_comments c
                LEFT JOIN accounts a ON c.author_id = a.id
                WHERE c.post_id = ?
                ORDER BY c.created_at ASC
            """, (post_id,))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def add_comment(self, post_id: str, comment_data: Dict) -> str:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO post_comments (post_id, author_id, content)
                VALUES (?, ?, ?)
            """, (post_id, comment_data["author_id"], comment_data["content"]))
            conn.commit()
            return str(cur.lastrowid)
        finally:
            conn.close()

    def delete_comment(self, post_id: str, comment_id: str) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM post_comments WHERE id = ? AND post_id = ?", (comment_id, post_id))
            conn.commit()
        finally:
            conn.close()
