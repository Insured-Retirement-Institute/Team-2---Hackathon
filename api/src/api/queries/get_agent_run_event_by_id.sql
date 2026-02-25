SELECT id, event_id, timestamp, agent_id, run_id, client_id_scope, input_summary,
       success, error_message, explanation_summary, data_sources_used, choice_criteria,
       input_validation_passed, guardrail_triggered, payload_ref
FROM agent_run_events
WHERE event_id = $1::uuid;
