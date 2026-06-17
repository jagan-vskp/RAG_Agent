# Dataset Download Instructions

## Superstore Sales Dataset

### Option A — Kaggle (recommended)

1. Go to: https://www.kaggle.com/datasets/vivek468/superstore-dataset-final
2. Click **Download** (requires free Kaggle account)
3. Extract the zip and rename the CSV to `sample_superstore.csv`
4. Place it in this `data/` folder

### Option B — Kaggle CLI

```bash
pip install kaggle
kaggle datasets download -d vivek468/superstore-dataset-final
unzip superstore-dataset-final.zip -d .
mv "Sample - Superstore.csv" sample_superstore.csv
```

### Option C — Tableau Public (alternative source)

The same dataset ships with Tableau Desktop:
- On Mac: `/Users/<you>/Documents/My Tableau Repository/Datasources/`
- On Windows: `Documents\My Tableau Repository\Datasources\`

---

## Dataset Schema

| Column | Type | Description |
|--------|------|-------------|
| Row ID | int | Unique row identifier |
| Order ID | str | Order identifier |
| Order Date | date | Date order was placed |
| Ship Date | date | Date order was shipped |
| Ship Mode | str | Shipping method |
| Customer ID | str | Customer identifier |
| Customer Name | str | Customer full name |
| Segment | str | Customer segment (Consumer/Corporate/Home Office) |
| Country | str | Country |
| City | str | City |
| State | str | State |
| Postal Code | str | Postal code |
| Region | str | Region (East/West/Central/South) |
| Product ID | str | Product identifier |
| Category | str | Product category (Furniture/Office Supplies/Technology) |
| Sub-Category | str | Product sub-category |
| Product Name | str | Product name |
| Sales | float | Revenue from the order line |
| Quantity | int | Number of units ordered |
| Discount | float | Discount applied (0.0–1.0) |
| Profit | float | Profit from the order line |
