--
-- Name: client_suitability_profiles; Type: TABLE; Schema: -; Owner: -
--

CREATE TABLE IF NOT EXISTS client_suitability_profiles (
    client_account_number varchar(20) PRIMARY KEY REFERENCES clients (client_account_number),
    age integer,
    life_stage varchar(50),
    marital_status varchar(50),
    dependents integer,
    risk_tolerance varchar(50),
    investment_experience varchar(50),
    volatility_comfort varchar(50),
    primary_objective varchar(50),
    secondary_objective varchar(50),
    liquidity_importance varchar(50),
    investment_horizon varchar(50),
    withdrawal_horizon varchar(50),
    current_income_need varchar(50),
    annual_income_range varchar(50),
    net_worth_range varchar(50),
    liquid_net_worth_range varchar(50),
    tax_bracket varchar(50),
    retirement_target_year integer,
    state varchar(20),
    citizenship varchar(20),
    advisory_model varchar(50),
    is_fee_based_account boolean
);
