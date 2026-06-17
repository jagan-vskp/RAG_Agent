# 🛒 Retail Sales Analysis — Superstore Dataset

A beginner-to-intermediate Data Analyst portfolio project that explores sales performance,
profitability, regional trends, and product insights using the popular Superstore dataset.

---

## 📁 Project Structure

```
retail_sales_analysis/
├── data/
│   ├── README.md              # Dataset download instructions
│   └── sample_superstore.csv  # Place the downloaded CSV here
├── notebooks/
│   ├── 01_data_cleaning.ipynb    # Load, inspect & clean the data
│   ├── 02_eda.ipynb              # Exploratory Data Analysis
│   ├── 03_sales_trends.ipynb     # Time-series & trend analysis
│   └── 04_dashboard.ipynb        # KPI summary & final charts
├── src/
│   ├── __init__.py
│   ├── data_loader.py         # Reusable loading & cleaning functions
│   └── visualizations.py      # Reusable chart functions
├── requirements.txt
└── README.md
```

---

## 🎯 Business Questions Answered

1. Which product categories and sub-categories generate the most revenue and profit?
2. Which regions and states are the most and least profitable?
3. How do sales and profit trend over time (monthly/quarterly)?
4. Which customer segments drive the most value?
5. What is the impact of discounts on profit margin?

---

## 🛠️ Tools & Libraries

| Tool | Purpose |
|------|---------|
| Python 3.9+ | Core language |
| pandas | Data loading, cleaning, aggregation |
| NumPy | Numerical operations |
| matplotlib | Static charts |
| seaborn | Statistical visualizations |
| plotly | Interactive charts |
| Jupyter Notebook | Analysis environment |

---

## ⚙️ Setup

### 1. Clone / navigate to this folder
```bash
cd retail_sales_analysis
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download the dataset
See `data/README.md` for instructions.

### 5. Launch Jupyter
```bash
jupyter notebook
```
Open notebooks in order: `01` → `02` → `03` → `04`.

---

## 📊 Key Findings (fill in after completing analysis)

- **Top category by revenue:** _TBD_
- **Least profitable sub-category:** _TBD_
- **Highest profit region:** _TBD_
- **Peak sales month:** _TBD_
- **Discount sweet spot:** _TBD_

---

## 📝 Business Recommendations (fill in after completing analysis)

1. _TBD_
2. _TBD_
3. _TBD_

---

## 📌 Dataset Source

[Superstore Sales Dataset on Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
