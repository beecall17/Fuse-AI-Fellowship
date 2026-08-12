# Stock Analysis: AAPL vs MSFT – Returns, Volatility, Beta, and Trading Signal

## 📌 Overview

This notebook performs a quantitative analysis of two major tech stocks – Apple (AAPL) and Microsoft (MSFT) – over a 4‑year period (2020–2023).  
It demonstrates core financial analytics concepts using **pandas**, **numpy**, **matplotlib**, and **yfinance**.

**Concepts covered:**
- Log returns vs. simple returns – additivity & cumulative performance
- Rolling volatility (20‑day and 50‑day) and annualisation
- Rolling beta (relative risk compared to a benchmark)
- Simple mean‑reversion trading signal based on volatility
- Look‑ahead bias prevention using `shift()`

## 📊 Data

- **Source:** Yahoo Finance (via `yfinance`)
- **Tickers:** AAPL (Apple Inc.), MSFT (Microsoft Corp.)
- **Period:** `2020-01-01` to `2024-01-01` (daily data)
- **Columns used:** `Close` price only (adjusted close)

## 🧪 Analysis Steps

1. **Data Preparation**  
   - Download and merge both stocks on the date index.
   - No missing values; first row yields `NaN` returns as expected.

2. **Returns & Cumulative Performance**  
   - Compute daily simple returns (`pct_change`) and log returns (`np.log(price / price.shift(1))`).
   - Verify that `exp(cumsum(log_return)) - 1` equals the cumulative simple return (additivity property).
   - Interpret the advantages of log returns for multi‑period calculations.

3. **Rolling Volatility & Annualisation**  
   - 20‑day and 50‑day rolling standard deviation of daily log returns.
   - Annualised volatility = daily volatility × √252.

4. **Rolling Beta (Relative Risk)**  
   - 60‑day rolling covariance (AAPL, MSFT) divided by 60‑day rolling variance of MSFT.
   - Plot beta over time with a horizontal line at 1.0.
   - Interpretation: beta > 1 means AAPL is more volatile relative to MSFT.

5. **Trading Signal – Volatility Mean‑Reversion**  
   - Signal = 1 if yesterday’s 20‑day volatility < yesterday’s 60‑day median volatility.
   - Shift the signal by 1 day to avoid look‑ahead bias.
   - Calculate strategy returns and compare cumulative returns with buy‑and‑hold.

6. **Visualisations**  
   - Twin‑axis plot of AAPL price vs. annualised 20‑day volatility.
   - Beta over time.
   - Cumulative returns: strategy vs. buy‑and‑hold.

## 📈 Key Findings

- Log returns and simple returns are nearly identical for small daily moves, but log returns are additive over time.
- The volatility mean‑reversion strategy avoided some large drawdowns (e.g., early 2020, mid‑2022) and **outperformed buy‑and‑hold** over the full period (approx. 150% vs. 110% cumulative return).
- Beta varied significantly; AAPL was more volatile than MSFT during certain periods (e.g., July 2022).

## 🛠️ Requirements

- Python 3.8+
- pandas, numpy, matplotlib, seaborn, yfinance

Install dependencies:
```bash
pip install pandas numpy matplotlib seaborn yfinance
```
## 🚀 How to Run
1. Clone the repository.

2. Run the notebook cell‑by‑cell (an active internet connection is required for yfinance to download data).

3. The notebook will automatically download the latest price data for the specified period.

## ⚠️ Notes
* The trading signal is for educational purposes only – not financial advice.

* Past performance does not guarantee future results.

## 📚 References
* Yahoo Finance API – yfinance

* Pandas Documentation – Rolling windows

* Volatility Mean‑Reversion Strategies – Academic literature

## 📝 Future Improvements
* Add transaction costs and slippage to the backtest.

* Test the strategy on other asset classes (ETFs, commodities).

* Incorporate a stop‑loss mechanism.

* Compare with a simple moving average crossover strategy.