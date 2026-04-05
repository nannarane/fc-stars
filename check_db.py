import sqlite3

conn = sqlite3.connect('fc_stars.db')
cursor = conn.cursor()

# 테이블 목록 확인
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('테이블 목록:', [table[0] for table in tables])

# 멤버 데이터 확인
cursor.execute('SELECT COUNT(*) FROM members')
member_count = cursor.fetchone()[0]
print(f'멤버 수: {member_count}')

# 일정 데이터 확인
cursor.execute('SELECT COUNT(*) FROM schedules')
schedule_count = cursor.fetchone()[0]
print(f'일정 수: {schedule_count}')

# 참석자 데이터 확인
cursor.execute('SELECT COUNT(*) FROM schedule_participants')
participant_count = cursor.fetchone()[0]
print(f'참석자 기록 수: {participant_count}')

# 어시스트 데이터 확인
cursor.execute('SELECT SUM(assists) FROM schedule_participants')
total_assists = cursor.fetchone()[0] or 0
print(f'총 어시스트 수: {total_assists}')

conn.close()