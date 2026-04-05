# FC Stars⭐ - Management System

풋살팀 FC Stars의 종합 관리 시스템입니다. 일정 관리, 멤버 관리, 통계 분석, 참석자 관리를 하나의 플랫폼에서 제공합니다.

## ✨ 주요 기능

### 📅 일정 보기
- **필터링 기능**: 일정 종류(⚽ Match, 🏃 Practice), 날짜 범위, 상대팀, 장소별 필터링
- **시각적 구분**: 일정 종류별 이모지 표시로 직관적인 구분
- **상세 정보**: 참석자 수, 상대팀 정보, 결과 표시
- **통계 요약**: 매치 수, 연습 수, 총 참석자 수 표시

### ⚽ 일정 관리
- **일정 CRUD**: 일정 추가/수정/삭제 기능
- **상대팀 관리**: 매치 시 상대팀 정보(이름, 실력, 연령대, 매너점수) 관리
- **참석자 관리**: 멤버별 참석 체크 및 성과 기록
- **성과 기록**: 골 ⚽ 및 어시스트 🅰️ 기록 기능
- **실시간 요약**: 참석자 수, 총 골 수, 총 어시스트 수 표시

### 👥 멤버 관리
- **멤버 CRUD**: 멤버 추가/수정/삭제 기능
- **기본 정보**: 이름, 출생년도, 직책 관리
- **게스트 멤버**: 임시 멤버 추가/삭제 기능
- **참석 기록**: 출석일수 자동 관리

### 📊 통계 분석
- **멤버별 통계**: 출석일수, 골 수, 어시스트 수
- **성과 지표**: 경기당 골/어시스트 비율 계산
- **시각화**: 차트로 멤버별 성과 비교
- **종합 랭킹**: 골/어시스트 기준 순위 표시

### 🔧 관리자 메뉴
- **DB 초기화**: 샘플 데이터로 데이터베이스 재구성
- **시스템 정보**: 데이터베이스 현황, 파일 정보 표시
- **안전장치**: 데이터 삭제 전 경고 및 확인 절차

## 🏗️ 시스템 아키텍처

### 기술 스택
- **Frontend**: Streamlit (Python 웹 프레임워크)
- **Backend**: SQLite (관계형 데이터베이스)
- **언어**: Python 3.11+
- **시각화**: Altair (통계 차트)

### 데이터베이스 설계

**Cloud Firestore 마이그레이션 예정** (현재는 관계형 SQL 설계)

#### 엔티티
- **members**: 멤버 정보 (이름, 출생년도, 직책, 출석일수, 골 수, 어시스트 수)
- **schedules**: 일정 정보 (매치/연습 구분, 날짜, 장소, 결과)
- **match_teams**: 상대팀 정보 (이름, 실력, 연령대, 매너점수)
- **schedule_participants**: 일정 참석자 및 성과 기록 (골, 어시스트)

#### 관계
- schedules ↔ match_teams (매치일 경우 1:1)
- schedules ↔ members (N:M, 참석자)
- schedule_participants에 성과 기록 (매치용)

### 파일 구조
```
fc-stars/
├── app.py                 # 메인 애플리케이션
├── database.py            # 데이터베이스 연동 모듈
├── menu/                  # 메뉴 모듈들
│   ├── view.py           # 일정 보기
│   ├── schedule.py       # 일정 관리
│   ├── members.py        # 멤버 관리
│   ├── stats.py          # 통계
│   └── admin.py          # 관리자 메뉴
├── sql/                  # 데이터베이스 관련
│   ├── schema.sql        # 테이블 생성 스크립트
│   ├── sample_data.sql   # 샘플 데이터
│   └── queries.sql       # 유용한 쿼리
├── fc_stars.db           # SQLite 데이터베이스
├── requirements.txt      # 의존성 패키지
└── README.md            # 이 파일
```

## 🚀 설치 및 실행

### 요구사항
- Python 3.11 이상
- pip 패키지 관리자

### 설치 방법
```bash
# 1. 저장소 클론
git clone <repository-url>
cd fc-stars

# 2. 가상환경 생성 (선택사항)
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 데이터베이스 초기화 (선택사항)
# 관리자 메뉴에서 DB 초기화 가능
```

### 실행 방법
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하여 사용 가능합니다.

## 📋 사용 방법

### 1. 일정 보기
- 사이드바에서 "📅 일정 보기" 선택
- 필터 옵션으로 원하는 일정 검색
- 일정 목록에서 상세 정보 확인

### 2. 일정 관리
- "⚽ 일정 관리" 메뉴 선택
- 새 일정 추가 또는 기존 일정 수정
- 참석자 관리에서 골/어시스트 기록

### 3. 멤버 관리
- "👥 멤버 관리"에서 멤버 정보 관리
- 게스트 멤버 임시 추가 가능

### 4. 통계 확인
- "📊 통계" 메뉴에서 멤버별 성과 분석
- 차트로 시각적 비교 가능

### 5. 시스템 관리
- "🔧 관리자" 메뉴에서 DB 초기화
- 시스템 현황 및 파일 정보 확인

## 🔄 버전 히스토리

- **v0.5.0**: 관리자 메뉴 및 DB 초기화 기능 추가
- **v0.4.0**: 어시스트 기능 및 이모지 UI 개선
- **v0.3.0**: 모바일 친화적 UI 및 사이드바 메뉴
- **v0.2.0**: 참석자 관리 및 골 기록 기능
- **v0.1.0**: 기본 일정/멤버 관리 기능

## 🤝 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 📞 문의

프로젝트 관련 문의사항은 이슈를 통해 남겨주세요.