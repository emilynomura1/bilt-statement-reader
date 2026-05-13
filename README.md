# Bilt Statement Reader

This project extracts and categorizes transactions from Bilt credit card PDF statements.

## Features
- Extracts transaction data from PDF statements in `data/input/` using `pdfplumber`.
- Outputs cleaned CSV files to `data/output/`.
- Categorizes transactions by description (e.g., Groceries, Travel, General) using keyword matching.
- Saves parsed results to CSV and categorized results to Excel.
- Prints summary of spend by category for each statement.

## Usage

1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Add your Bilt PDF statements** to `data/input/`.

3. **Extract transactions:**
   ```
   python src/pdf-to-csv.py
   ```
   This will create CSV files in `data/output/`.

4. **Categorize transactions:**
   ```
   python src/budget-categorization.py
   ```
   This will print summaries and save Excel files with budget categories in `data/output/`.

## Customization
- To improve categorization, edit the `categorize_description` function in `src/budget-categorization.py` to add or adjust keywords.
- Budget categories can always be overriden in Excel if `categorize_description` is not flexible enough.
