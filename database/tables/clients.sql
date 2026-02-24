--
-- Name: clients; Type: TABLE; Schema: -; Owner: -
--

CREATE TABLE IF NOT EXISTS clients (
    client_account_number varchar(20) PRIMARY KEY,
    client_name varchar(100) NOT NULL,
    process_dt TIMESTAMPTZ DEFAULT NOW()
);
