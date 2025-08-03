-- PostgreSQL-specific features
SELECT 
    id,
    name,
    metadata -> 'profile' ->> 'age' as age,
    tags @> ARRAY['vip'] as is_vip,
    ARRAY[email, phone] as contact_methods,
    JSONB_EXTRACT_PATH(preferences, 'notifications', 'email') as email_notifications,
    created_at AT TIME ZONE 'UTC' as created_utc,
    ROW_NUMBER() OVER (
        PARTITION BY status 
        ORDER BY created_at DESC
    ) as status_rank
FROM users 
WHERE metadata ? 'profile'
  AND tags && ARRAY['active', 'verified']
  AND created_at >= NOW() - INTERVAL '1 year';