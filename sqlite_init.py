from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from settings import APP_ENV, SQLITE_DB_PATH, SQLITE_SCHEMA_PATH, SQLITE_SEED_PATH


DEV_ENVS = {"dev", "development", "test"}
EXPECTED_TABLES = {
    "accounts",
    "members",
    "schedules",
    "match_teams",
    "schedule_participants",
}


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _read_sql_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")
    return path.read_text(encoding="utf-8")


def _get_existing_tables(conn: sqlite3.Connection) -> set[str]:
    cur = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        """
    )
    return {row["name"] for row in cur.fetchall()}


def _is_database_initialized(conn: sqlite3.Connection) -> bool:
    existing_tables = _get_existing_tables(conn)
    return EXPECTED_TABLES.issubset(existing_tables)


def init_database(
    db_path: Path = SQLITE_DB_PATH,
    schema_path: Path = SQLITE_SCHEMA_PATH,
    *,
    verbose: bool = True,
) -> None:
    """
    SQLite DB 파일과 스키마를 초기화합니다.
    DB 파일이 없으면 생성되고, 있더라도 schema.sql을 안전하게 적용합니다.
    """
    db_path = Path(db_path)
    schema_path = Path(schema_path)

    db_path.parent.mkdir(parents=True, exist_ok=True)

    schema_sql = _read_sql_file(schema_path)

    with _connect(db_path) as conn:
        conn.executescript(schema_sql)
        conn.commit()

    if verbose:
        print(f"[DB] initialized: {db_path}")


def ensure_database_initialized(
    db_path: Path = SQLITE_DB_PATH,
    schema_path: Path = SQLITE_SCHEMA_PATH,
    *,
    verbose: bool = True,
) -> None:
    """
    SQLite 파일이 없거나, 파일은 있지만 스키마가 없는 경우 초기화합니다.
    """
    db_path = Path(db_path)

    if not db_path.exists():
        if verbose:
            print(f"[DB] database file not found. creating: {db_path}")
        init_database(db_path=db_path, schema_path=schema_path, verbose=verbose)
        return

    with _connect(db_path) as conn:
        if not _is_database_initialized(conn):
            if verbose:
                print("[DB] schema not found. initializing database...")
            init_database(db_path=db_path, schema_path=schema_path, verbose=verbose)
        else:
            if verbose:
                print("[DB] database already initialized")


def load_sample_data(
    db_path: Path = SQLITE_DB_PATH,
    seed_path: Path = SQLITE_SEED_PATH,
    *,
    force: bool = False,
    verbose: bool = True,
) -> None:
    """
    샘플 데이터를 로드합니다.
    force=False: 데이터가 이미 있으면 스킵
    force=True : 기존 데이터 삭제 후 재삽입
    """
    db_path = Path(db_path)
    seed_path = Path(seed_path)

    if not seed_path.exists():
        raise FileNotFoundError(f"Seed SQL file not found: {seed_path}")

    seed_sql = _read_sql_file(seed_path)

    with _connect(db_path) as conn:
        if not force and _is_database_initialized(conn):
            # 적어도 하나의 핵심 테이블에 데이터가 있으면 스킵
            cur = conn.execute("SELECT 1 FROM members LIMIT 1")
            if cur.fetchone() is not None:
                if verbose:
                    print("[DB] sample data already exists. skipping.")
                return

        if force:
            conn.executescript(
                """
                DELETE FROM schedule_participants;
                DELETE FROM match_teams;
                DELETE FROM accounts;
                DELETE FROM members;
                DELETE FROM schedules;

                DELETE FROM sqlite_sequence
                WHERE name IN (
                    'schedule_participants',
                    'match_teams',
                    'accounts',
                    'members',
                    'schedules'
                );
                """
            )

        conn.executescript(seed_sql)
        conn.commit()

    if verbose:
        print(f"[DB] sample data loaded: {seed_path}")


def initialize_dev_database(
    *,
    reset: bool = False,
    seed: bool = True,
    verbose: bool = True,
) -> None:
    """
    앱 시작 시 호출하는 최종 진입점입니다.
    - dev/test 환경에서만 동작
    - reset=True면 DB를 비우고 다시 생성
    - reset=False면 없을 때만 생성
    """
    if APP_ENV.lower() not in DEV_ENVS:
        if verbose:
            print(f"[DB] skipped because APP_ENV={APP_ENV}")
        return

    if reset:
        db_path = Path(SQLITE_DB_PATH)
        if db_path.exists():
            db_path.unlink()
            if verbose:
                print(f"[DB] deleted existing database: {db_path}")

        init_database(verbose=verbose)
        if seed:
            load_sample_data(force=True, verbose=verbose)
        return

    ensure_database_initialized(verbose=verbose)

    if seed:
        load_sample_data(force=False, verbose=verbose)


if __name__ == "__main__":
    initialize_dev_database(reset=False, seed=True, verbose=True)