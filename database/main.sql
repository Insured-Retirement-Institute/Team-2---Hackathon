--
-- pgschema database dump
--

-- Dumped from database version PostgreSQL 17.6
-- Dumped by pgschema version 1.2.0


\i clients.sql
\i client_suitability_profiles.sql
\i contract_summary.sql
\i products.sql
\i index_options.sql
\i riders.sql
\i agent_two_recommendation_runs.sql
\i agent_one_book_of_business.sql
\i agent_run_events.sql

CREATE TABLE llm_converstations (
    id BIGINT BY DEFAULT AS IDENTITY PRIMARY KEY,
    session_id BIGINT,
    data JSONB,
    create_dt TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    update_dt TIMESTAMPTZ DEFAULT NOW() NOT NULL
)
