-- Dismiss an alert
UPDATE hackathon.alerts
SET
    status = 'dismissed',
    updated_at = now()
WHERE id = $1
RETURNING id;
