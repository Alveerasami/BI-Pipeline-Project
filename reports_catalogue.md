# Reports Catalogue

A living catalogue of reports produced from the `Reporting` warehouse schema,
maintained so users and managers can find what already exists before
requesting a new report, and so data relationships stay documented as the
warehouse grows.

| Report Name | Purpose | Presentation Type | Query Type | Source Table(s) | Refresh | Owner |
|---|---|---|---|---|---|---|
| Incident Register | Full record-level list for casework/audit | Table | Simple | `Reporting.CrimeReports` | Daily | BI Analyst |
| Incident Volume & Outcome Rate | Monitors service performance by category | Table | Combined (CTE + JOIN) | `Reporting.CrimeReports` | Daily | BI Analyst |
| Category by Location Matrix | Identifies hotspot locations for service planning | Crosstab | Merged (PIVOT) | `Reporting.CrimeReports` | Daily | BI Analyst |
| Incidents by Category (Chart) | Dashboard visual / management pack | Chart | Simple (aggregate) | `Reporting.CrimeReports` | Daily | BI Analyst |
| Data Quality Trend | Evidence for inspections; tracks source data health over time | Table / Chart | Simple | `Reporting.DataQualityLog` | Per pipeline run | BI Analyst |

## Data relationships

```
Staging.CrimeReports (raw landing)
        |
        |  usp_LoadCrimeReports (CTE clean + MERGE)
        v
Reporting.CrimeReports (clean, reporting-ready)
        |
        +--> Incident Register
        +--> Incident Volume & Outcome Rate
        +--> Category by Location Matrix
        +--> Incidents by Category (Chart)

Reporting.DataQualityLog (one row per pipeline run)
        +--> Data Quality Trend report
```

- `Reporting.CrimeReports.PersistentId` is the natural key used for
  deduplication and for matching incoming staged records to existing ones
  in the MERGE statement.
- `Reporting.DataQualityLog` is independent of `Reporting.CrimeReports` -
  it's a run-level audit log, not joined to record-level data, so quality
  trends can be reported even if downstream tables are later restructured.

## Maintenance notes

- New reports should be added to this catalogue before being shared with
  users, with their source table(s) and refresh cadence recorded.
- If a report's source table changes (e.g. a new column, a renamed field),
  this catalogue and the data relationships diagram above should be updated
  in the same change.
