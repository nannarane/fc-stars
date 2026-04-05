-- Useful queries for FC Stars database

-- Get all members with their stats
SELECT name, position, attendance_days, goals,
       ROUND(goals * 1.0 / NULLIF(attendance_days, 0), 2) as goals_per_match
FROM members
ORDER BY goals DESC;

-- Get upcoming schedules
SELECT s.date, s.type, s.location,
       CASE WHEN s.type = 'match' THEN mt.name ELSE 'N/A' END as opponent,
       COUNT(sp.member_id) as participants
FROM schedules s
LEFT JOIN match_teams mt ON s.id = mt.schedule_id
LEFT JOIN schedule_participants sp ON s.id = sp.schedule_id
WHERE s.date >= DATE('now')
GROUP BY s.id, s.date, s.type, s.location, mt.name
ORDER BY s.date;

-- Get match results with team details
SELECT s.date, s.location, mt.name as opponent,
       s.result, mt.skill_level, mt.age_group, mt.manner_score,
       SUM(sp.goals) as total_goals
FROM schedules s
JOIN match_teams mt ON s.id = mt.schedule_id
LEFT JOIN schedule_participants sp ON s.id = sp.schedule_id
WHERE s.type = 'match'
GROUP BY s.id, s.date, s.location, mt.name, s.result, mt.skill_level, mt.age_group, mt.manner_score
ORDER BY s.date DESC;

-- Get member participation and goals by schedule
SELECT m.name, s.date, s.type, s.location,
       CASE WHEN s.type = 'match' THEN mt.name ELSE 'Training' END as opponent_team,
       sp.goals
FROM members m
JOIN schedule_participants sp ON m.id = sp.member_id
JOIN schedules s ON sp.schedule_id = s.id
LEFT JOIN match_teams mt ON s.id = mt.schedule_id
ORDER BY s.date DESC, m.name;

-- Get training attendance summary
SELECT s.date, s.location, COUNT(sp.member_id) as attendees,
       GROUP_CONCAT(m.name) as participant_names
FROM schedules s
LEFT JOIN schedule_participants sp ON s.id = sp.schedule_id
LEFT JOIN members m ON sp.member_id = m.id
WHERE s.type = 'training'
GROUP BY s.id, s.date, s.location
ORDER BY s.date DESC;

-- Update member attendance and goals after a match
-- (Example: increment attendance for participants in schedule_id = 1)
UPDATE members
SET attendance_days = attendance_days + 1,
    goals = goals + COALESCE((
        SELECT sp.goals
        FROM schedule_participants sp
        WHERE sp.member_id = members.id AND sp.schedule_id = 1
    ), 0)
WHERE id IN (
    SELECT member_id
    FROM schedule_participants
    WHERE schedule_id = 1
);