--
-- AgentOne: book of business with notifications per policy (full JSON snapshot per run)
--

CREATE TABLE IF NOT EXISTS agent_one_book_of_business (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    customer_identifier VARCHAR(200) NOT NULL,
    payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_agent_one_bob_created_at ON agent_one_book_of_business (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_one_bob_customer ON agent_one_book_of_business (customer_identifier);
