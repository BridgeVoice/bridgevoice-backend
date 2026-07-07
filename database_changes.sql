-- XP and Session Tracking
ALTER TABLE users
ADD COLUMN sessions_completed INTEGER DEFAULT 0;

ALTER TABLE users
ADD COLUMN total_xp INTEGER DEFAULT 0;