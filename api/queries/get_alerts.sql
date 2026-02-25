-- Get all renewal alerts with optional filters
SELECT
    id,
    policy_id as "policyId",
    client_name as "clientName",
    carrier,
    renewal_date as "renewalDate",
    days_until_renewal as "daysUntilRenewal",
    current_rate as "currentRate",
    renewal_rate as "renewalRate",
    current_value as "currentValue",
    is_min_rate as "isMinRate",
    priority,
    has_data_exception as "hasDataException",
    missing_fields as "missingFields",
    status,
    alert_type as "alertType",
    alert_types as "alertTypes",
    alert_description as "alertDescription"
FROM alerts
WHERE
    ($1::varchar IS NULL OR status = $1)
    AND ($2::varchar IS NULL OR priority = $2)
    AND ($3::varchar IS NULL OR carrier = $3)
    AND (status != 'snoozed' OR snoozed_until IS NULL OR snoozed_until < now())
ORDER BY
    CASE priority
        WHEN 'high' THEN 1
        WHEN 'medium' THEN 2
        WHEN 'low' THEN 3
    END,
    days_until_renewal ASC;
