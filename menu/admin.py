import streamlit as st
import sqlite3
import os
from database import get_schedules_with_details, get_members

def show_admin_menu():
    st.header("🔧 관리자 메뉴")
    st.markdown("시스템 관리 및 유지보수 기능")

    # 경고 메시지
    st.warning("⚠️ **주의**: 아래 기능들은 시스템 데이터를 변경할 수 있습니다. 신중하게 사용하세요.")

    # DB 초기화 섹션
    st.subheader("🗃️ 데이터베이스 관리")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 데이터베이스 초기화")
        st.markdown("현재 데이터베이스를 삭제하고 샘플 데이터로 재구성합니다.")
        st.markdown("**주의**: 모든 기존 데이터가 삭제됩니다!")

        if st.button("🔄 DB 초기화 실행", type="primary", key="init_db"):
            with st.spinner("데이터베이스를 초기화하는 중..."):
                try:
                    init_database()
                    st.success("✅ 데이터베이스가 성공적으로 초기화되었습니다!")
                    st.info("🔄 페이지를 새로고침하여 변경사항을 확인하세요.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 초기화 실패: {e}")

        st.markdown("---")
        st.markdown("### 참가자 성과 초기화")
        st.markdown("모든 멤버의 출석일수, 골, 어시스트와 일정별 참가자의 골/어시스트를 0으로 초기화합니다.")

        if st.button("🧹 참가자 성과 초기화", type="secondary", key="reset_participant_stats"):
            with st.spinner("참가자 성과를 초기화하는 중..."):
                try:
                    reset_participant_stats()
                    st.success("✅ 모든 참가자 성과가 초기화되었습니다!")
                    st.info("🔄 페이지를 새로고침하여 변경사항을 확인하세요.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 초기화 실패: {e}")

    with col2:
        st.markdown("### 데이터베이스 정보")
        try:
            # 현재 데이터베이스 정보 표시
            conn = sqlite3.connect('fc_stars.db')
            cursor = conn.cursor()

            # 테이블 목록
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            st.write(f"**테이블 수**: {len(tables)}")
            st.write("**테이블 목록**:")
            for table in tables:
                if table[0] != 'sqlite_sequence':
                    st.write(f"- {table[0]}")

            # 데이터 수량
            cursor.execute('SELECT COUNT(*) FROM members')
            member_count = cursor.fetchone()[0]
            st.write(f"**멤버 수**: {member_count}")

            cursor.execute('SELECT COUNT(*) FROM schedules')
            schedule_count = cursor.fetchone()[0]
            st.write(f"**일정 수**: {schedule_count}")

            cursor.execute('SELECT COUNT(*) FROM schedule_participants')
            participant_count = cursor.fetchone()[0]
            st.write(f"**참석 기록 수**: {participant_count}")

            conn.close()

        except Exception as e:
            st.error(f"데이터베이스 정보 조회 실패: {e}")

    # 시스템 정보 섹션
    st.subheader("ℹ️ 시스템 정보")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 현재 상태")
        try:
            schedules_data = get_schedules_with_details()
            members_data = get_members()

            st.metric("등록된 일정", len(schedules_data))
            st.metric("등록된 멤버", len(members_data))

            # 최근 일정
            if schedules_data:
                recent_schedule = max(schedules_data, key=lambda x: x['date'])
                st.write(f"**최근 일정**: {recent_schedule['date']} - {recent_schedule['location']}")

        except Exception as e:
            st.error(f"상태 조회 실패: {e}")

    with col2:
        st.markdown("### 데이터 파일")
        db_path = 'fc_stars.db'
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / 1024  # KB 단위
            st.metric("DB 파일 크기", f"{db_size:.1f} KB")
            st.write(f"**파일 경로**: {os.path.abspath(db_path)}")
        else:
            st.error("데이터베이스 파일을 찾을 수 없습니다.")

def init_database():
    """데이터베이스를 초기화하고 샘플 데이터를 삽입합니다."""
    db_path = 'fc_stars.db'

    # 기존 데이터베이스 삭제
    if os.path.exists(db_path):
        os.remove(db_path)
        print('기존 데이터베이스 파일 삭제됨')

    # 새 데이터베이스 생성 및 스키마 적용
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    schema_path = os.path.join(os.path.dirname(__file__), '..', 'sql', 'schema.sql')
    schema_path = os.path.normpath(schema_path)
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    schema_statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
    for statement in schema_statements:
        if not statement.startswith('--'):
            cursor.execute(statement)

    conn.commit()
    print('데이터베이스 스키마 생성 완료')

    # 샘플 데이터 파일로 데이터 삽입
    sample_path = os.path.join(os.path.dirname(__file__), '..', 'sql', 'sample_data.sql')
    sample_path = os.path.normpath(sample_path)
    with open(sample_path, 'r', encoding='utf-8') as f:
        sample_sql = f.read()

    sample_sql = '\n'.join(
        line for line in sample_sql.splitlines()
        if not line.strip().startswith('--')
    )
    sample_statements = [stmt.strip() for stmt in sample_sql.split(';') if stmt.strip()]
    for statement in sample_statements:
        cursor.execute(statement)

    conn.commit()
    print('샘플 데이터 삽입 완료')

    conn.close()
    print('데이터베이스 초기화 및 데이터 구성 완료!')

def reset_participant_stats():
    """모든 참가자의 출석일수, 골, 어시스트와 일정별 성과를 초기화합니다."""
    db_path = 'fc_stars.db'
    if not os.path.exists(db_path):
        raise FileNotFoundError('데이터베이스 파일을 찾을 수 없습니다.')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('UPDATE members SET attendance_days = 0, goals = 0, assists = 0')
    cursor.execute('UPDATE schedule_participants SET goals = 0, assists = 0')

    conn.commit()
    conn.close()
