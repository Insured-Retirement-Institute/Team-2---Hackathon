SELECT id, event_id, timestamp, agent_id, run_id, client_id_scope, input_summary,
       success, error_message, explanation_summary, data_sources_used, choice_criteria,
       input_validation_passed, guardrail_triggered, payload_ref
FROM hackathon.agent_run_events
WHERE ($1::text IS NULL OR agent_id = $1)
  AND ($2::timestamptz IS NULL OR timestamp >= $2)
  AND ($3::timestamptz IS NULL OR timestamp <= $3)
  AND ($4::boolean IS NULL OR success = $4)
  AND ($5::text IS NULL OR client_id_scope = $5)
ORDER BY timestamp DESC
LIMIT $6 OFFSET $7;
