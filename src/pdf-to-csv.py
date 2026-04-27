import pandas as pd
import pdfplumber
import glob
import os
import re

output_dir = os.path.join(os.path.dirname(__file__), '../data/output')
os.makedirs(output_dir, exist_ok=True)

pdf_files = glob.glob(os.path.join(os.path.dirname(__file__), '../data/input/*.pdf'))

for pdf_path in pdf_files:
	print(f"Processing {pdf_path} ...")
	try:
		with pdfplumber.open(pdf_path) as pdf:
			text = ""
			for i in range(1, len(pdf.pages)):
				page_text = pdf.pages[i].extract_text()
				if page_text:
					cleaned_lines = []
					for line in page_text.split('\n'):
						l = line.strip()
						# Remove obvious headers or footers
						if (
							l.startswith('Cardless Inc.') or
							l.startswith('issued by') or
							l.startswith('Page') or
							re.search(r'Page \d+ of', l) or
							re.search(r'@', l) or
							re.search(r'Bilt', l, re.IGNORECASE) and re.search(r'Card', l, re.IGNORECASE)
						):
							continue
						cleaned_lines.append(line)
					page_text_cleaned = '\n'.join(cleaned_lines)
					text += page_text_cleaned + "\n"

		# Find the Transactions section
		lines = [line.strip() for line in text.split('\n') if line.strip()]
		# Find the start and end of the Transactions section
		start_idx = None
		end_idx = None
		for idx, line in enumerate(lines):
			if line.lower() == 'transactions':
				start_idx = idx
			if 'total new charges in this period' in line.lower() and start_idx is not None and end_idx is None:
				end_idx = idx
				break
		if start_idx is None or end_idx is None or end_idx <= start_idx:
			print(f"Could not find Transactions section in {pdf_path}")
			continue
		section_lines = lines[start_idx+1:end_idx]
		# Try to find a header line
		header_idx = None
		for idx, line in enumerate(section_lines):
			if len(re.split(r'\s{2,}', line)) >= 3:
				header_idx = idx
				break
		data = []
		if header_idx is not None:
			header_line = section_lines[header_idx]
			headers = re.split(r'\s{2,}', header_line)
			headers = headers[:3]
			for line in section_lines[header_idx+1:]:
				cols = re.split(r'\s{2,}', line)
				if len(cols) >= 3:
					row = dict(zip(headers, cols[:3]))
					data.append(row)
				elif data:
					data[-1][headers[1]] += ' ' + line
		else:
			# Fallback: parse lines with date and amount pattern
			date_pattern = r'(\d{2}/\d{2}/\d{4}|[A-Z][a-z]{2} \d{1,2}, \d{4})'
			amount_pattern = r'(-?\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
			transaction_re = re.compile(rf'^{date_pattern}\s+(.+?)\s+{amount_pattern}$')
			for line in section_lines:
				m = transaction_re.match(line)
				if m:
					date, desc, amount = m.groups()
					data.append({'Date': date, 'Description': desc, 'Amount': amount})
				elif data:
					data[-1]['Description'] += ' ' + line
		if not data:
			print(f"No transactions parsed in {pdf_path}")
			continue
		df = pd.DataFrame(data)
		# Standardize column names
		col_map = {}
		for c in df.columns:
			cl = c.lower()
			if 'date' in cl:
				col_map[c] = 'Date'
			elif 'desc' in cl:
				col_map[c] = 'Description'
			elif 'amount' in cl:
				col_map[c] = 'Amount'
			else:
				col_map[c] = c
		df = df.rename(columns=col_map)
		base_name = os.path.splitext(os.path.basename(pdf_path))[0]
		output_csv = os.path.join(output_dir, f'{base_name}_transactions.csv')
		df.to_csv(output_csv, index=False)
		print(f"Transactions data saved to {output_csv}")
	except Exception as e:
		print(f"Error processing {pdf_path}: {e}")