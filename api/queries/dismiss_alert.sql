-- Dismiss an alert
UPDATE renewal_alerts
SET
    status = 'dismissed',
    updated_at = now()
WHERE id = $1
RETURNING id;
