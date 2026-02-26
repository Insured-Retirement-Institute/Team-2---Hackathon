-- Example query to fetch policy by policy number
SELECT *
FROM policies
WHERE policy_number = $1;
