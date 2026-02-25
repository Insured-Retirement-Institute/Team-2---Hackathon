--
-- Responsible AI: unified run events from all agents (agent_one, agent_two, agent_three)
--

CREATE TABLE IF NOT EXISTS agent_run_events (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID NOT NULL UNIQUE,
    timestamp TIMESTAMPTZ NOT NULL,
    agent_id VARCHAR(20) NOT NULL CHECK (agent_id IN ('agent_one', 'agent_two', 'agent_three')),
    run_id VARCHAR(100),
    client_id_scope VARCHAR(200),
    input_summary JSONB DEFAULT '{}',
    success BOOLEAN NOT NULL,
    error_message TEXT,
    explanation_summary TEXT,
    data_sources_used TEXT[],
    choice_criteria TEXT[],
    input_validation_passed BOOLEAN,
    guardrail_triggered BOOLEAN,
    payload_ref UUID REFERENCES agent_two_recommendation_runs(id)
);

CREATE INDEX IF NOT EXISTS idx_agent_run_events_timestamp ON agent_run_events (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_agent_run_events_agent_id ON agent_run_events (agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_run_events_success ON agent_run_events (success);
CREATE INDEX IF NOT EXISTS idx_agent_run_events_client_id_scope ON agent_run_events (client_id_scope);
