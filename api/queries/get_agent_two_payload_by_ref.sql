SELECT id, run_id, created_at, client_id, payload
FROM agent_two_recommendation_runs
WHERE id = $1::uuid;
