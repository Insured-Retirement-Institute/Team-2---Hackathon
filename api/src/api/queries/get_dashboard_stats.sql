-- Get dashboard statistics
SELECT
    COUNT(*)::int as total,
    COUNT(*) FILTER (WHERE priority = 'high')::int as high,
    COUNT(*) FILTER (WHERE days_until_renewal <= 30)::int as urgent,
    COALESCE(SUM(CAST(REPLACE(REPLACE(current_value, '$', ''), ',', '') AS numeric)), 0) as "totalValue"
FROM hackathon.alerts
WHERE status IN ('pending', 'reviewed');
