--
-- Name: riders; Type: TABLE; Schema: -; Owner: -
--

CREATE TABLE IF NOT EXISTS riders (
    id SERIAL PRIMARY KEY,
    product_id varchar(50) REFERENCES products (product_id) ON DELETE CASCADE,
    rider_name varchar(200),
    rider_type varchar(50),
    annual_fee numeric(5,2),
    features text,
    roll_up_rate numeric(5,2),
    payout_rate numeric(5,2)
);
