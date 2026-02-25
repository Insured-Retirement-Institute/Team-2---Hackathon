--
-- Name: products; Type: TABLE; Schema: -; Owner: -
--

CREATE TABLE IF NOT EXISTS products (
    product_id varchar(50) PRIMARY KEY,
    carrier varchar(100),
    product_name varchar(200),
    product_type varchar(20),
    issue_year integer,
    available_states text,
    guaranteed_minimum_rate numeric(5,2),
    current_fixed_rate numeric(5,2),
    m_e_fee numeric(5,2),
    administrative_fee numeric(8,2),
    fund_expenses numeric(5,2),
    cdsc_years integer,
    surrender_schedule text,
    free_withdrawal_percent numeric(5,2),
    minimum_premium numeric(12,2),
    maximum_premium numeric(12,2),
    age_min integer,
    age_max integer,
    bonus_rate numeric(5,2),
    liquidity_features text,
    key_benefits text,
    suitable_for text,
    competitive_advantages text,
    risk_profile varchar(20),
    is_new_product boolean,
    has_license boolean,
    has_appointment boolean,
    has_training boolean,
    can_sell boolean,
    compliance_notes text,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
