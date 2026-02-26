-- Snooze an alert for a specified number of days
UPDATE hackathon.alerts
SET
    status = 'snoozed',
    snoozed_until = now() + ($2::integer || ' days')::interval,
    updated_at = now()
WHERE id = $1
RETURNING
    id,
    snoozed_until;
