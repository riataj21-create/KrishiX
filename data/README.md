# Data Ingestion Scripts

This directory contains scripts for ingesting real market price data from government and open data sources.

## Purpose

- Transform and load government APMC market data
- Normalize external data into the schema
- Validate data quality
- Update market_prices table regularly

## Phases

**Phase 8+:** Data ingestion pipeline implementation

### Planned Data Sources

1. **Government APMC Data**
   - Indian Ministry of Agriculture & Farmers Welfare
   - State APMC websites

2. **Open Data**
   - Agricultural prices database
   - Market information APIs

## Structure (Future)

```
data/
├── etl/
│   ├── apmc_importer.py
│   ├── transformer.py
│   └── validator.py
├── sources/
│   ├── sample_prices.csv
│   └── markets_reference.csv
└── logs/
    └── ingestion.log
```

## Usage (Future)

```bash
python data/etl/apmc_importer.py --source government --date 2025-01-15
```

---

**Note**: Currently using sample data from `database/sample_data.sql`
