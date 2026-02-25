--
-- AgentTwo: full storable payload per recommendation run (for drill-down from dashboard)
--

CREATE TABLE IF NOT EXISTS agent_two_recommendation_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL,
    client_id VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_agent_two_runs_created_at ON agent_two_recommendation_runs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_two_runs_client_id ON agent_two_recommendation_runs (client_id);
