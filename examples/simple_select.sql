-- Simple SELECT query
SELECT id, name, email, created_at
FROM users
WHERE active = TRUE
  AND created_at > '2023-01-01'
ORDER BY created_at DESC
LIMIT 100;