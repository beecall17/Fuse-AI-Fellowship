
---

## Overall Repository contains



# Pandas Data Cleaning & Analysis Projects

This repository contains two Jupyter notebooks that demonstrate real‑world data cleaning and exploratory analysis using **pandas**, **matplotlib**, and **seaborn**.

## 📁 Folder: `Pandas [Data cleaning Learning]`


`Credit Card Fraud/Credit Card Fraud Data Cleaning & Analysis.ipynb` 

Full data cleaning pipeline on a highly imbalanced credit card fraud dataset. Covers missing data (MCAR/MAR), imputation strategies, outlier detection (global vs. grouped IQR), and business insights. |

`Stock Analysis/Stock Analysis (AAPL vs MSFT).ipynb`

Time‑series analysis of two tech stocks. Computes returns, rolling volatility, beta, and implements a simple volatility mean‑reversion trading signal. Demonstrates look‑ahead bias prevention. |

## 🔧 Key Techniques

- Vectorised operations (avoiding row‑by‑row loops)
- Handling missing data with domain‑aware imputation
- Rolling windows and time series resampling
- Outlier detection using IQR (global and group‑wise)
- Cumulative returns and log‑return additivity

## 🚀 Getting Started

Clone the repository and install the required libraries:

```bash
pip install pandas numpy matplotlib seaborn yfinance