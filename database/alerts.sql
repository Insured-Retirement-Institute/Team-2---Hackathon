--
-- Name: alerts; Type: TABLE; Schema: -; Owner: -
--

CREATE TABLE IF NOT EXISTS alerts (
    id varchar PRIMARY KEY,
    customer_identifier varchar,  -- Agent 1 customer identifier (links to client_profiles)
    policy_id varchar NOT NULL,
    client_name varchar NOT NULL,
    carrier varchar NOT NULL,
    renewal_date varchar NOT NULL,
    days_until_renewal integer NOT NULL,
    current_rate varchar,
    renewal_rate varchar,
    current_value varchar NOT NULL,
    is_min_rate boolean DEFAULT false,
    priority varchar NOT NULL CHECK (priority IN ('high', 'medium', 'low')),
    has_data_exception boolean DEFAULT false,
    missing_fields text[],
    status varchar NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'snoozed', 'dismissed')),
    alert_type varchar NOT NULL CHECK (alert_type IN ('replacement_recommended', 'replacement_opportunity', 'missing_info', 'suitability_review', 'income_planning')),
    alert_types varchar[],
    alert_description text NOT NULL,
    alert_detail jsonb,  -- Store full Agent 1 PolicyOutput as JSON
    agent_data jsonb,  -- Store complete Agent 1 BookOfBusinessOutput
    created_at timestamp DEFAULT now(),
    updated_at timestamp DEFAULT now(),
    snoozed_until timestamp
);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_priority ON alerts(priority);
CREATE INDEX IF NOT EXISTS idx_alerts_carrier ON alerts(carrier);
CREATE INDEX IF NOT EXISTS idx_alerts_policy_id ON alerts(policy_id);
CREATE INDEX IF NOT EXISTS idx_alerts_customer_identifier ON alerts(customer_identifier);
