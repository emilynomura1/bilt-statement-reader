import os
import glob
import pandas as pd

# Simple keyword-based categorization
categories = ["Groceries", "Travel", "Eating Out", "Auto", "General"]
def categorize_description(desc):
    desc = desc.lower()
    if any(word in desc for word in ['grocery', 'market', 'supermarket', 'whole foods', 'trader joe', 'safeway', 'qfc', 'wal-mart', 'sfc']):
        return 'Groceries'
    elif any(word in desc for word in ['flight', 'airlines', 'uber', 'lyft', 'hotel', 'travel', 'alaska', 'delta', 'united', 'hawaiian', 'american', 'frontier', 'southwest', 'jetblue', 'hyatt', 'hilton', 'marriott', 'airalo', 'airbnb']):
        return 'Travel'
    elif any(word in desc for word in ['restaurant', 'cafe', 'starbucks', 'chipotle', 'eatery', 'dining', 'burger', 'coffee']):
        return 'Eating Out'
    elif any(word in desc for word in ['gas', 'shell', 'chevron', 'auto', 'oil change', 'aaa', 'vioc']):
        return 'Auto'
    elif any(word in desc for word in ['bilt housing', 'bilt rent']):
        return 'Bills'
    else:
        return 'General'

output_dir = os.path.join(os.path.dirname(__file__), '../data/output')
csv_files = glob.glob(os.path.join(output_dir, '*.csv'))

all_dfs = []
for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    if 'Description' in df.columns and 'Amount' in df.columns:
        df['Budget Category'] = df['Description'].apply(categorize_description)
        # Ensure Amount is numeric
        df['Amount'] = pd.to_numeric(df['Amount'].replace('[^\d.-]', '', regex=True), errors='coerce')
        all_dfs.append(df)
        # Print summary for this CSV
        print(f"Summary for {os.path.basename(csv_file)}:")
        print(df.groupby('Budget Category', as_index=False)['Amount'].sum())

        # Print descriptions by category to better understand categorization
        # Add keywords to categorize_description() to improve accuracy
        # for cat in categories:
        #     print(f"Descriptions categorized as '{cat}':")
        #     cat_descs = df[df['Budget Category'] == cat]['Description']
        #     for desc in cat_descs:
        #         print(f"- {desc}")

        print("-"*40)
    else:
        print('No valid CSV files with Description and Amount columns found.')