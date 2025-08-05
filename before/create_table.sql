-- 기존 quiz_results 테이블에 likes 컬럼 추가
ALTER TABLE quiz_results ADD COLUMN IF NOT EXISTS likes INTEGER DEFAULT 0;

-- 기존 user_likes 테이블이 있다면 삭제
DROP TABLE IF EXISTS user_likes;

-- 좋아요 수 계산을 위한 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_quiz_likes ON quiz_results(likes);

-- 기존 데이터의 likes 컬럼을 0으로 초기화
UPDATE quiz_results SET likes = 0 WHERE likes IS NULL;
