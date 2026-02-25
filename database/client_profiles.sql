--
-- Name: client_profiles; Type: TABLE; Schema: -; Owner: -
--
-- Stores client comparison parameters (financial profile data)
-- Maps to ComparisonParameters from UI spec
--

CREATE TABLE IF NOT EXISTS client_profiles (
    client_id varchar PRIMARY KEY,
    client_name varchar NOT NULL,

    -- Profile
    resides_in_nursing_home varchar CHECK (resides_in_nursing_home IN ('yes', 'no')),
    has_long_term_care_insurance varchar CHECK (has_long_term_care_insurance IN ('yes', 'no')),
    has_medicare_supplemental varchar CHECK (has_medicare_supplemental IN ('yes', 'no')),

    -- Financial
    gross_income varchar,
    disposable_income varchar,
    tax_bracket varchar,
    household_liquid_assets varchar,
    monthly_living_expenses varchar,
    total_annuity_value varchar,
    household_net_worth varchar,

    -- Anticipated Changes
    anticipate_expense_increase varchar CHECK (anticipate_expense_increase IN ('yes', 'no')),
    anticipate_income_decrease varchar CHECK (anticipate_income_decrease IN ('yes', 'no')),
    anticipate_liquid_asset_decrease varchar CHECK (anticipate_liquid_asset_decrease IN ('yes', 'no')),

    -- Objectives & Planning
    financial_objectives text,
    distribution_plan text,
    owned_assets text,
    time_to_first_distribution varchar,
    expected_holding_period varchar,
    source_of_funds text,
    employment_status text,
    apply_to_means_tested_benefits varchar CHECK (apply_to_means_tested_benefits IN ('yes', 'no')),

    created_at timestamp DEFAULT now(),
    updated_at timestamp DEFAULT now()
);

-- Index for lookups
CREATE INDEX IF NOT EXISTS idx_client_profiles_client_name ON client_profiles(client_name);
