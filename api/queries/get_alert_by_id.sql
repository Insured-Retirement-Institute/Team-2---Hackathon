-- Get a single alert by ID with full details
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
    alert_description as "alertDescription",
    alert_detail
FROM renewal_alerts
WHERE id = $1;
