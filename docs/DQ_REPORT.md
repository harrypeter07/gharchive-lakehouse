# DATA QUALITY REPORT

**Generated At**: 2026-10-26T10:28:30.630968+00:00  
**Reconciliation Status**: PASSED (Zero silent drops)

## 1. Mathematical Reconciliation
$$\text{Rows Read} = \text{Rows Kept} + \sum \text{Dropped}$$

| Metric | Row Count | Percentage |
| :--- | :--- | :--- |
| **Total Rows Read** | **3,826,476** | 100.00% |
| **Valid Rows Kept** | **2,057,052** | 53.76% |
| **Total Rows Dropped** | **1,769,424** | 46.24% |

## 2. Drop Breakdown by Reason Code
| Reason Code | Meaning | Dropped Rows | % of Total Read |
| :--- | :--- | :--- | :--- |
| `UNSUPPORTED_TYPE` | Event type not in target lakehouse schema scope. | 906,577 | 23.69% |
| `BOT_ACTOR` | Actor username ends with '[bot]'. | 862,845 | 22.55% |
| `DUPLICATE_EVENT_ID` | Duplicate event_id natural key encountered. | 2 | 0.00% |
