-- Sample data for FC Stars database

-- Insert sample members
INSERT INTO members (name, birth_year, position, attendance_days, goals, assists) VALUES
('구자인', 1986, '선수', 5, 6, 5),
('박정환', 1986, '선수', 5, 2, 3),
('박준환', 1983, '주장', 5, 5, 4),
('윤여준', 1986, '부주장', 4, 3, 2),
('조한도', 1986, '코치', 2, 0, 0),
('한은주', 1986, '매니저', 4, 1, 1);

-- Insert sample schedules
INSERT INTO schedules (type, date, location, result) VALUES
('training', '2026-04-17', '구리 아천스타디움', NULL),
('match', '2026-04-03', '구리 대복풋살장', 'win'),
('match', '2026-03-16', '언더플레이 풋살파크', 'loss'),
('training', '2026-03-20', '힐링FC풋살장', NULL),
('match', '2026-03-06', '김병지축구클럽 구리점', 'draw');

-- Insert match teams for match schedules
INSERT INTO match_teams (schedule_id, name, skill_level, age_group, manner_score) VALUES
(2, '토탈FC', '중급', '20-30대', 4.2),
(3, '행축즐축', '고급', '30대', 3.8),
(5, '신생팀', '초보', '30대', 4.5);

-- Insert schedule participants

-- Training 1 participants
INSERT INTO schedule_participants (schedule_id, member_id, goals, assists) VALUES
(1, 1, 0, 0), (1, 2, 0, 0), (1, 3, 0, 0), (1, 4, 0, 0), (1, 5, 0, 0), (1, 6, 0, 0);


-- Match 2 participants
INSERT INTO schedule_participants (schedule_id, member_id, goals, assists) VALUES
(2, 1, 0, 0), (2, 2, 0, 0), (2, 3, 0, 0), (2, 4, 0, 0), (2, 6, 0, 0);


-- Match 3 participants
INSERT INTO schedule_participants (schedule_id, member_id, goals, assists) VALUES
(3, 1, 0, 0), (3, 2, 0, 0), (3, 3, 0, 0), (3, 4, 0, 0), (3, 6, 0, 0);

-- Training 4 participants
INSERT INTO schedule_participants (schedule_id, member_id, goals, assists) VALUES
(4, 1, 0, 0), (4, 2, 0, 0), (4, 3, 0, 0), (4, 5, 0, 0);

-- Match 5 participants
INSERT INTO schedule_participants (schedule_id, member_id, goals, assists) VALUES
(5, 1, 0, 0), (5, 2, 0, 0), (5, 3, 0, 0), (5, 4, 0, 0), (5, 6, 0, 0);