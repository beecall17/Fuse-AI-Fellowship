# Market Segmentation: Finding Structure in Customer Behavior
## Project Overview

This project aims to segment customers based on their purchasing behavior using various clustering algorithms. The main objective is to identify distinct customer groups to enable targeted marketing strategies and enhance business decision-making. We apply K-Means, Hierarchical Clustering (with various linkages and variants), DBSCAN, and HDBSCAN, followed by thorough validation and business interpretation of the resulting segments.

## Dataset

The analysis uses the **[UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)** dataset, specifically transaction data from `Year 2010-2011`. This dataset contains transactional records of a UK-based online retail store. Key columns include `InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, and `Country`.

## Methodology

### 1. Environment Setup

The project utilizes Python with standard data science libraries:
-   `pandas`, `numpy`: Data manipulation.
-   `matplotlib`, `seaborn`: Data visualization.
-   `sklearn.preprocessing.StandardScaler`: Feature scaling.
-   `sklearn.cluster` (KMeans, AgglomerativeClustering, DBSCAN, Birch), `hdbscan`: Clustering algorithms.
-   `scipy.cluster.hierarchy`: Dendrogram visualization.
-   `sklearn.metrics`: Cluster validation (silhouette_score, davies_bouldin_score, calinski_harabasz_score).
-   `sklearn.neighbors.NearestNeighbors`: For DBSCAN parameter estimation.

### 2. Data Loading & Initial Exploration

The `online_retail_II.xlsx` file was loaded, revealing:
-   **Shape**: 541,910 records, 8 features.
-   **Missing Values**: Approximately 25% of `Customer ID` and 0.26% of `Description` were missing.
-   **Anomalies**: Presence of negative `Quantity` (returns/cancellations) and negative `Price`.
-   **Geographic Distribution**: ~91% of transactions from the United Kingdom.

### 3. Data Cleaning

To prepare the data for analysis, the following steps were taken:
-   **Removed rows with missing `Customer ID`**: Essential for customer-centric analysis.
-   **Removed cancelled transactions**: Invoices starting with 'C' were removed to avoid skewing monetary calculations.
-   **Removed negative `Quantity` and `Price`**: Ensuring only valid purchases. Prices of zero (promotional items) were retained.
-   **Parsed `InvoiceDate`**: Ensured correct datetime format.
-   **Created `TotalPrice`**: Calculated as `Quantity * Price`.
-   **Removed duplicate rows**.

After cleaning, the dataset contained 392,733 records, with 149,177 rows removed.

### 4. Feature Engineering (RFM + Basket Average)

Customer-level features were engineered:
-   **Recency**: Days since the customer's last purchase (relative to one day after the latest transaction date).
-   **Frequency**: Number of unique transactions (invoices) per customer.
-   **Monetary**: Total spend by the customer.
-   **Basket Average**: Average quantity of items per invoice per customer.

These features were aggregated into a `customer_df`.

### 5. Feature Distribution & Transformation

All engineered features were highly right-skewed and non-normal, indicating significant outliers. After evaluating raw, log-transformed, outlier-capped, and combined approaches, **log transformation (`np.log1p`)** was chosen. This method effectively compresses extreme values while preserving their relative magnitude, which is crucial for identifying high-value customer segments without diluting valuable information, making the distributions more suitable for distance-based clustering algorithms.


### 6. Feature Scaling

`StandardScaler` was applied to the log-transformed features. This is essential for distance-based algorithms to ensure all features contribute equally to distance calculations, preventing features with larger numerical ranges from dominating the clustering process.

### 7. Clustering Algorithms Applied

#### a. K-Means Clustering
-   **Optimal `k`**: The Elbow Method suggested `k=4`, while the Silhouette Score peaked at `k=2`. `k=4` was chosen to provide more granular customer segments, balancing statistical indication with business needs.
-   **Initialization Stability**: K-Means++ demonstrated slightly better stability compared to random initialization, especially for distinct cluster structures.
-   **Mini-Batch K-Means Comparison**: Mini-Batch K-Means was significantly faster (approx. 16x) but yielded a slightly lower Silhouette Score and only moderate agreement (Adjusted Rand Score: 0.4396) with K-Means++, indicating a trade-off between speed and cluster fidelity.

#### b. Hierarchical Clustering
-   **Dendrogram Analysis**: A dendrogram (Ward linkage on a sample) indicated 4 distinct clusters with a cut at a distance of ~20.
-   **Linkage Methods Comparison**: Ward linkage produced the most balanced and interpretable clusters, despite not always having the highest Silhouette Score. Single and Average linkages resulted in highly imbalanced clusters, while Complete linkage also showed significant imbalance.
-   **Variants Comparison**: BIRCH (standalone and combined with Agglomerative) and K-Neighbors Graph variants offered speed improvements but resulted in lower Silhouette Scores and different cluster structures compared to standard Ward linkage.

#### c. DBSCAN Clustering
-   **Epsilon Estimation**: A K-Distance plot (with `min_samples=8`) suggested an optimal epsilon (`eps`) between 0.5-0.7.
-   **Parameter Experimentation**: `eps=0.6` and `min_samples=5` were selected as the optimal balance, yielding 3 main clusters (plus noise) with 2.9% noise.
-   **Noise Analysis**: DBSCAN's noise points (`-1` label) were found to represent a distinct segment of "lost loyal high spenders"—customers with high historical spend but high recency, requiring specific business attention.

  #### d. HDBSCAN Clustering
-   **Parameter Experimentation**: `min_cluster_size=5` and `min_samples=5` were chosen to identify 3 clusters, accumulating 6.5% noise.
-   **Noise Analysis**: Similar to DBSCAN, HDBSCAN's noise points also represented "lost loyal high spenders," although with slightly lower average monetary and recency values, possibly due to HDBSCAN's ability to handle varying densities, which can result in more nuanced noise identification. HDBSCAN showed a more balanced proportional distribution among clusters compared to DBSCAN, unlocking the possibility of looking at feature combinations differently.

## Key Findings & Business Implications

The K-Means model with 4 clusters revealed the following customer segments, offering actionable insights for targeted marketing:

### Cluster Profiles

-   **Cluster 0 — At-Risk Dormant**
    -   **Profile**: Customers with high recency (~179 days), low frequency (~1.44), and low monetary value (~$233.74). These are customers who haven't purchased for a long time and have historically spent little.
    -   **Marketing Action**: Targeted discounts or coupons to re-engage them. Implement sales and advertisement campaigns to bring them back.

-   **Cluster 1 — Spender, Lost Loyal**
    -   **Profile**: High-spending customers (~$1089.41 monetary value, ~$432.22 average basket) who have not visited the business for a considerable period (~120 days), but historically showed moderate frequency (~1.99).
    -   **Marketing Action**: Personalized retention efforts, such as direct outreach (email/phone calls), exclusive offers, and genuine feedback collection to understand reasons for inactivity. These customers represent significant untapped potential.

-   **Cluster 2 — High Spender, Loyalist**
    -   **Profile**: The most valued customers: low recency (~20 days), very high frequency (~12.20), and extremely high monetary value (~$7185.81). They visit regularly and spend significantly.
    -   **Marketing Action**: Acknowledge and reward their loyalty through incentive programs (e.g., loyalty points, premium memberships, high-quality free gifts on large purchases). The focus should be on maintaining engagement and appreciation, rather than simple discounts.

-   **Cluster 3 — Average, Loyalist**
    -   **Profile**: Loyal customers who visit often (~24 days recency, ~3.39 frequency) but have an average spend (~$797.53 monetary, ~$139.31 average basket).
    -   **Marketing Action**: Discounts or coupons can encourage higher frequency and potentially increase their average basket size. General promotional campaigns can be effective for this segment.

### Executive Summary

Our analysis successfully grouped customers into four distinct segments using K-Means clustering. This segmentation provides a granular view of customer behavior, highlighting various opportunities for strategic intervention. The identification of 'Spender, Lost Loyal' customers (Cluster 1) is particularly crucial, indicating a segment of high-value individuals who require bespoke retention strategies to win them back. For our 'High Spender, Loyalist' customers (Cluster 2), the most valuable segment, continuous engagement and appreciation through exclusive rewards are key to fostering long-term loyalty beyond mere transactional incentives. The 'At-Risk Dormant' (Cluster 0) and 'Average, Loyalist' (Cluster 3) segments can benefit from more traditional promotional efforts, such as discounts and coupons, aimed at re-engagement and increasing purchase frequency/volume, respectively. By tailoring marketing efforts to these specific segments, the business can optimize resource allocation, enhance customer satisfaction, and ultimately drive sustainable growth.

## Hypothesis Testing / Failure Log Summary

The project involved rigorous hypothesis testing to validate assumptions and decisions at various stages:

-   **H1: Feature Distribution**: Confirmed that raw features were highly skewed and non-normal, necessitating log transformation.
-   **H2: Optimal K Selection**: Observed a conflict between Elbow (K=4) and Silhouette (K=2) methods, resolved by prioritizing business needs for more granular segments (K=4).
-   **H3: Initialization Stability**: K-Means++ generally showed higher stability than random initialization.
-   **H4: Convergence Speed vs. Cluster Fidelity**: Mini-Batch K-Means was significantly faster but with a slight trade-off in Silhouette Score and moderate agreement (Adjusted Rand Score: 0.4396) compared to K-Means++.
-   **H5: Hierarchical Clustering Variants**: Optimized variants (BIRCH, K-Graph) were faster but yielded lower cluster quality (Silhouette Scores) and different structures compared to standard Agglomerative Ward.
-   **H6: Hierarchical Linkage Method Performance**: Ward linkage provided the most balanced and interpretable clusters, outperforming highly imbalanced results from Single, Average, and Complete linkages.
-   **H7: Comparative Actionability of K-Means vs. Hierarchical Ward Cluster Profiles**: Hierarchical Ward offered slightly more nuanced separation for 'lost loyal, high spender' segments, but K-Means provided strong overall segmentation.
-   **H8: Constant vs. Variable Density Adaptation (DBSCAN vs. HDBSCAN)**: DBSCAN with chosen parameters performed better than HDBSCAN for this dataset in terms of less noise, faster execution, and better Davies-Bouldin Index, despite HDBSCAN's theoretical advantage for varying densities.
-   **H9: Noise Profiling as a Business Segment**: Confirmed that noise points from density-based clustering represented a distinct, high-value segment (e.g., "lost loyal high spenders") rather than random errors, requiring specific business attention.

This systematic validation process ensured that model parameters and choices were robust and aligned with the project's objectives.

## How to Run

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```
2.  **Download the dataset**: Obtain `online_retail_II.xlsx` from the [UCI Online Retail II dataset page](https://archive.ics.uci.edu/dataset/502/online+retail+ii) and place it in the same directory as the notebook.
3.  **Install dependencies**:
    ```bash
    pip install pandas numpy scikit-learn matplotlib seaborn scipy hdbscan xlrd openpyxl
    ```
4.  **Open the Jupyter Notebook**: Launch Jupyter Lab or Jupyter Notebook and open `your_notebook_name.ipynb`.
5.  **Run all cells**: Execute the cells sequentially to reproduce the analysis and results.

6.  
