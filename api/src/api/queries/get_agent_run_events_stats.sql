SELECT
  COUNT(*)::bigint AS total_runs,
  COUNT(*) FILTER (WHERE success)::bigint AS success_count,
  COUNT(*) FILTER (WHERE agent_id = 'agent_one')::bigint AS agent_one_runs,
  COUNT(*) FILTER (WHERE agent_id = 'agent_two')::bigint AS agent_two_runs,
  COUNT(*) FILTER (WHERE agent_id = 'agent_three')::bigint AS agent_three_runs,
  COUNT(*) FILTER (WHERE agent_id = 'agent_two' AND explanation_summary IS NOT NULL AND explanation_summary != '')::bigint AS agent_two_with_explanation,
  COUNT(*) FILTER (WHERE guardrail_triggered = true)::bigint AS guardrail_triggered_count
FROM hackathon.agent_run_events
WHERE timestamp >= $1::timestamptz AND timestamp <= $2::timestamptz;
