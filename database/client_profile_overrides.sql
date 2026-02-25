--
-- Name: client_profile_overrides; Type: TABLE; Schema: -; Owner: -
-- Purpose: Store local overrides for client profile data from Sureify
--

CREATE TABLE IF NOT EXISTS client_profile_overrides (
    client_id varchar PRIMARY KEY,
    risk_tolerance varchar,
    investment_objectives text,
    notes text,
    created_at timestamp DEFAULT now(),
    updated_at timestamp DEFAULT now()
);

-- Index for lookups
CREATE INDEX IF NOT EXISTS idx_client_profile_overrides_client_id
    ON client_profile_overrides(client_id);
