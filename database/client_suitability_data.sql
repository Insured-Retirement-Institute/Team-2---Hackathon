--
-- Name: client_suitability_data; Type: TABLE; Schema: -; Owner: -
--
-- Stores client suitability assessment data
-- Maps to SuitabilityData from UI spec
--

CREATE TABLE IF NOT EXISTS client_suitability_data (
    client_id varchar PRIMARY KEY,

    -- Suitability Assessment Fields
    client_objectives text NOT NULL,
    risk_tolerance varchar NOT NULL,
    time_horizon varchar NOT NULL,
    liquidity_needs text NOT NULL,
    tax_considerations text NOT NULL,
    guaranteed_income text NOT NULL,
    rate_expectations text NOT NULL,
    surrender_timeline text NOT NULL,
    living_benefits text[] NOT NULL,  -- Array of strings
    advisor_eligibility text NOT NULL,
    score integer NOT NULL,
    is_prefilled boolean NOT NULL DEFAULT false,

    created_at timestamp DEFAULT now(),
    updated_at timestamp DEFAULT now(),

    -- Foreign key to client_profiles
    FOREIGN KEY (client_id) REFERENCES client_profiles(client_id) ON DELETE CASCADE
);

-- Index for lookups
CREATE INDEX IF NOT EXISTS idx_client_suitability_client_id ON client_suitability_data(client_id);
