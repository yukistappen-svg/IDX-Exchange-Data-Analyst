# Weeks 2–3: Exploratory Data Analysis (EDA)

During Weeks 2–3, I conducted exploratory data analysis on the MLS real estate transaction dataset using Python, Pandas, Matplotlib, and Seaborn. The original dataset contained **615,707 records across 28 CSV files**, of which **414,054 records (67.25%)** were classified as residential properties. I filtered the dataset to focus on residential transactions and evaluated missing values, numeric distributions, and potential outliers.

The analysis revealed that the **average closing price was approximately $1.19 million**, compared with a median of **$823,000**, indicating a right-skewed housing price distribution. Similarly, the average Days on Market was **37.36 days**, while the median was only **18 days**, suggesting that a smaller number of properties experienced substantially longer selling periods. I also examined living area, lot size, bedrooms, bathrooms, listing prices, and construction year using descriptive statistics, histograms, and boxplots.

Missing value analysis showed that key transaction variables were largely complete, while several less relevant fields had substantial missingness. Using an extended IQR method, I identified extreme observations in housing prices, lot sizes, and other numeric variables for further investigation rather than automatically removing them.

**Key Outcome:** The EDA established a clearer understanding of housing market characteristics, identified potential data quality issues, and produced a filtered residential dataset of **414,054 records** for the subsequent data cleaning and preparation phase in Weeks 4–5.
