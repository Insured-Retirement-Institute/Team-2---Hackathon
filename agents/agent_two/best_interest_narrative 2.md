# Best Interest Summary Narrative (Generated)

Generated from Opportunity Generator with mocked data and `agents/sample_changes.json` (client 1001). Uses "opportunities presented" and human-readable data sources (no internal names like sureify_products, db_suitability).

When the front-end sends **customer selection** in the same JSON payload (see `customerSelection` below), the narrative and summary contextualize the customer's choice: they state which product(s) the customer selected from the opportunities presented, and that context is included in the Prudential Standards, Conflict Management, Transparency, and Documentation sections, and in the e-app `selected_products`.

**Front-end JSON shape for customer selection (optional):**
```json
{
  "customerSelection": {
    "selectedProductIds": ["product-uuid-1", "product-uuid-2"],
    "notes": "Customer preferred 5-year term for liquidity.",
    "selectedAt": "2025-02-25T18:00:00Z"
  }
}
```

---

## Prudential Standards

Reasonable diligence was applied to the customer's financial situation, needs, and objectives. Client profile characteristics used to justify the assessment: risk tolerance: Conservative; time horizon: 5-10 years; liquidity needs: Low -- has separate emergency fund covering 12 months of expenses; objectives: Supplement Social Security with guaranteed income; preserve assets for estate; financial objectives: Supplement Social Security with guaranteed income; preserve assets for estate; distribution plan: Systematic withdrawals beginning at age 67; expected holding period: 10+ years; gross income: 85000; household net worth: 650000; household liquid assets: 250000; tax bracket: 22%. Available products were investigated from the available product catalog, client suitability profile. Explicit comparative analysis was performed using criteria: risk tolerance, time horizon, liquidity needs, financial objectives, expected holding period. Summary: Opportunity Generator produced 3 opportunities presented from the available product catalog, contextualized using: risk tolerance, time horizon, liquidity needs, financial objectives, expected holding period. Input sections received: suitability, clientGoals, clientProfile.

---

## Conflict Management

Material conflicts of interest are identified in firm disclosures. Compensation structures (commission, fee) are disclosed; conflicts are eliminated where possible or disclosed in writing. The opportunities presented were generated using the client profile characteristics above and product data; no conflict incentivized the selection of a particular product.

---

## Transparency

Conflicts of interest and compensation are disclosed in writing before the transaction. Product alternatives considered are reflected in the opportunities presented and reasons to switch (pros/cons). The client profile characteristics that justify the assessment (risk tolerance: Conservative, time horizon: 5-10 years, liquidity needs: Low -- has separate emergency fund covering 12 months of expenses, objectives: Supplement Social Security with guaranteed income; preserve assets for estate, financial objectives: Supplement Social Security with guaranteed income; preserve assets for estate, distribution plan: Systematic withdrawals beginning at age 67...) are documented in merged_profile_summary. Product risks and features (rate, term, surrender period, free withdrawal, guaranteed minimum) are included for each opportunity with match_reason explaining fit to the client's profile.

---

## Documentation

Customer information gathered and analysis performed are documented in merged_profile_summary and input_summary, including the client profile characteristics that justify the assessment: risk tolerance: Conservative, time horizon: 5-10 years, liquidity needs: Low -- has separate emergency fund covering 12 months of expenses, objectives: Supplement Social Security with guaranteed income; preserve assets for estate, financial objectives: Supplement Social Security with guaranteed income; preserve assets for estate, distribution plan: Systematic withdrawals beginning at age 67, expected holding period: 10+ years, gross income: 85000, household net worth: 650000, household liquid assets: 250000, tax bracket: 22%. The basis for the opportunities presented is documented in explanation (summary, data_sources_used, choice_criteria) and in each opportunity's match_reason. Alternatives considered are reflected in the product set and reasons_to_switch. Records supporting compliance (run_id, timestamp, payload) are retained; minimum 6-year retention applies per firm policy. Customer acknowledgment of the opportunities presented and conflicts is obtained at point of sale (e-app flow).

---

## Ongoing Duty

Firm will monitor customer accounts and the opportunities presented for continued suitability; review changing circumstances and market conditions; update the opportunities presented when customer profile characteristics change; and conduct periodic compliance reviews of firm-wide practices.
