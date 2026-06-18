# Linear Model - Week 04

## Overview
This notebook demonstrates foundational linear model techniques applied to customer churn prediction using the Telco Customer Churn dataset.

## Dataset
- **Source**: Telco Customer Churn dataset
- **Size**: 7,043 customers × 21 features
- **Target**: `Churn` (binary classification: Yes/No)

## Key Features
- Customer demographics (gender, age, dependents)
- Service subscriptions (internet, phone, streaming, security)
- Billing information (monthly charges, total charges, contract type)

## Contents

### Data Exploration & Preprocessing
- Load and inspect dataset structure with pandas
- Identify and handle missing values in `TotalCharges` column (11 NaN values)
- Convert `TotalCharges` from object type to numeric (float64)
- Encode target variable `Churn` to binary format (Yes=1, No=0)

### Key Observations
- **Dataset Size**: 7,043 rows × 21 columns
- **Data Quality**: No null values after preprocessing
- **Distributions**: Right-skewed patterns observed in tenure and monthly charges
- **Valid Records**: 7,032 samples for modeling (11 new customers with $0 total charges)
- **Numeric Summary**:
  - Tenure: mean=32.37 months, range 0-72 months
  - Monthly Charges: mean=$64.76, range $18.25-$118.75
  - Senior Citizen: 16.2% of customer base

## Learning Objectives
- Understand foundational data preprocessing for linear models
- Explore feature distributions and data quality assessment
- Handle missing values and type conversions
- Prepare classification datasets for machine learning

## Technologies
- **Language**: Python 3
- **Libraries**: pandas, numpy, scikit-learn
- **Environment**: Google Colab
- **Format**: Jupyter Notebook

## Files
- `Linear_model_Bikal.ipynb` - Main notebook with exploratory analysis and preprocessing

## Author
Bikal | Fuse AI Fellowship - Week 04
