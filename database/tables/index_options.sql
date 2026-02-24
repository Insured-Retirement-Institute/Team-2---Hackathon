--
-- Name: index_options; Type: TABLE; Schema: -; Owner: -
--

CREATE TABLE IF NOT EXISTS index_options (
    id SERIAL PRIMARY KEY,
    product_id varchar(50) REFERENCES products (product_id) ON DELETE CASCADE,
    index_name varchar(100),
    strategy varchar(100),
    current_value numeric(6,2),
    floor numeric(6,2)
);
