# Portfolio Data

## File Format

Portfolio CSV files should have the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `ticker` | string | Stock ticker symbol (e.g., AAPL) |
| `shares` | integer | Number of shares held |
| `cost_basis` | float | Average cost per share in USD |

## Example

```csv
ticker,shares,cost_basis
AAPL,100,150.00
MSFT,50,280.00
TSLA,30,200.00
```

## Sample Portfolio

The included `sample_portfolio.csv` contains 5 holdings across tech and financials:

- **AAPL** — 100 shares @ $150.00 (Apple)
- **MSFT** — 50 shares @ $280.00 (Microsoft)
- **TSLA** — 30 shares @ $200.00 (Tesla)
- **NVDA** — 25 shares @ $450.00 (NVIDIA)
- **JPM** — 40 shares @ $140.00 (JPMorgan Chase)

## Creating Your Own Portfolio

1. Create a new CSV file in this directory
2. Follow the same format (ticker, shares, cost_basis)
3. Update `PORTFOLIO_PATH` in `simple_version.py` to point to your file

## Supported Tickers

The built-in financial data supports: AAPL, MSFT, TSLA, NVDA, JPM, AMZN, GOOGL.

For other tickers, the analysis will use Claude's general knowledge (less precise).
