-- Complex query with JOINs and CTEs
WITH recent_orders AS (
    SELECT 
        user_id,
        COUNT(*) as order_count,
        SUM(total_amount) as total_spent
    FROM orders 
    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
    HAVING COUNT(*) > 5
),
user_categories AS (
    SELECT 
        user_id,
        CASE 
            WHEN total_spent > 1000 THEN 'Premium'
            WHEN total_spent > 500 THEN 'Standard'
            ELSE 'Basic'
        END as category
    FROM recent_orders
)
SELECT 
    u.id,
    u.name,
    u.email,
    uc.category,
    ro.order_count,
    ro.total_spent,
    p.title as last_purchase
FROM users u
INNER JOIN user_categories uc ON u.id = uc.user_id
INNER JOIN recent_orders ro ON u.id = ro.user_id
LEFT JOIN LATERAL (
    SELECT p.title
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON oi.product_id = p.id
    WHERE o.user_id = u.id
    ORDER BY o.created_at DESC
    LIMIT 1
) p ON TRUE
WHERE u.active = TRUE
ORDER BY ro.total_spent DESC, u.name ASC;