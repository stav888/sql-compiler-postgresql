-- Simpler complex query for testing
WITH recent_orders AS (
    SELECT 
        user_id,
        COUNT(*) as order_count,
        SUM(total_amount) as total_spent
    FROM orders 
    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
    HAVING COUNT(*) > 5
)
SELECT 
    u.id,
    u.name,
    u.email,
    ro.order_count,
    ro.total_spent
FROM users u
INNER JOIN recent_orders ro ON u.id = ro.user_id
WHERE u.active = TRUE
ORDER BY ro.total_spent DESC, u.name ASC;