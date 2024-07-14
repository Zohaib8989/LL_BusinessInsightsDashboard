# QuickBooks Financial Visualization in Power BI

## Introduction 👋

Welcome to Limitless Life LLC's repository. This project aims to develop a comprehensive financial dashboard using Power BI, extracting and visualizing data from QuickBooks Online to provide valuable insights for informed decision-making.

## Problem Statement 🔍

Many organizations struggle to aggregate and visualize their financial data effectively, leading to missed opportunities for operational improvements and cost savings. This project addresses the need for a centralized dashboard that offers real-time financial insights.

## Deliverables 📦

- Automated data extraction process from QuickBooks Online
- Consolidated CSV files stored in Google Drive
- A comprehensive Power BI dashboard visualizing key financial metrics
- Documentation of the entire process for reproducibility

## Process Guide 📝

### 1. Data Source and Structure 🗂️

#### Link to Google Sheets

- **Limitless Life LLC**
    - **Transactions Cash:** [Link](https://docs.google.com/spreadsheets/d/{SpreadsheetID}/gviz/tq?tqx=out:csv&sheet=Journal)
    - **Transactions Accrual:** [Link](https://docs.google.com/spreadsheets/d/{SpreadsheetID}/gviz/tq?tqx=out:csv&sheet=Journal)
    - **Chart of Accounts Cash:** [Link](https://docs.google.com/spreadsheets/d/{SpreadsheetID}/gviz/tq?tqx=out:csv&sheet=Account_List)
    - **Email Campaign:** [Link](https://docs.google.com/spreadsheets/d/{SpreadsheetID}/gviz/tq?tqx=out:csv&sheet=Campaigns)
- **Info Up LLC**
    - **Transactions Cash:** [Link](https://docs.google.com/spreadsheets/d/{SpreadsheetID}/gviz/tq?tqx=out:csv&sheet={SheetName})
    - **Chart of Accounts:** [Link](https://docs.google.com/spreadsheets/d/{SpreadsheetID}/gviz/tq?tqx=out:csv&sheet={SheetName})


### 2. Data Aggregation Script

Here is the Python code used to combine the data from Google Sheets:

```python
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaIoBaseUpload
import gspread
import pandas as pd
import io

# Define the scope
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Add your credentials
creds = Credentials.from_service_account_file('path/to/your/key.json', scopes=scope)
client = gspread.authorize(creds)

# Google Drive API setup
drive_service = build('drive', 'v3', credentials=creds)

# Folder ID (replace with your folder ID)
folder_id = 'your_folder_id'

# List all files in the folder
results = drive_service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",
    pageSize=1000,
    fields="files(id, name, mimeType)"
).execute()
items = results.get('files', [])

# Process Google Sheets files
dataframes = []

for item in items:
    if item['mimeType'] == 'application/vnd.google-apps.spreadsheet':
        try:
            sheet = client.open_by_key(item['id']).sheet1
            df = pd.DataFrame(sheet.get_all_records())
            dataframes.append(df)
        except Exception as e:
            print(f"An error occurred processing file {item['name']} ({item['id']}): {e}")

# Combine all dataframes into a single one
if dataframes:
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Use an in-memory buffer to save the CSV data
    csv_buffer = io.BytesIO()
    combined_df.to_csv(csv_buffer, index=False, encoding='utf-8')
    csv_buffer.seek(0)
    print("Data combined and saved to an in-memory buffer.")
else:
    print("No Google Sheets files were processed.")

# Check if the combined_data.csv file exists in Google Drive
existing_file_id = None
for item in items:
    if item['name'] == 'combined_data.csv':
        existing_file_id = item['id']
        break

# Upload or update the file on Google Drive
file_metadata = {
    'name': 'combined_data.csv',
    'parents': [folder_id]
}
media = MediaIoBaseUpload(csv_buffer, mimetype='text/csv')

if existing_file_id:
    # Update the existing file
    drive_service.files().update(
        fileId=existing_file_id,
        media_body=media
    ).execute()
    print("File updated on Google Drive with ID:", existing_file_id)
else:
    # Upload as a new file
    drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print("File uploaded to Google Drive")

print("Process complete.")
```


### 3. Data Modelling 📊

The data modeling involved structuring the extracted financial data to ensure accurate relationships between different datasets, facilitating effective analysis and reporting.

### 4. Data Tables 📋

The main data tables include:
- Transactions Table
- Chart of Accounts Table
- Monthly Aggregated Data Table

### 5. DAX Measures & KPIs 🧮

Key measures include:
- Year-to-Date Earnings
- Year-to-Date Spending
- Profit Margin
- Advertisement Spend Percentage
- Burn Rate
- Cash in Hand

### 6. Dashboard Design **🎨**

#### Summary

- **KPIs (DONE)**
    - YTD Earnings
    - YTD Spending
    - Profit Margin
    - Advertisement %
    - Burn Rate
    - Cash in Hand
    - Merchant Reserves
- **Chart 01 (DONE)**
    - Income (Last 12 Months) - Column Chart
    - Income Comparison (Current vs Previous Year) - Line Chart
    - Income vs. Expenses (Last 12 Months) - Column Chart
    - Expenses % (Last 12 Months) - Column Chart
    - Advertisement % (Last 12 Months) - Column Chart
- **Chart 02**
    - Cashflow Over Time (Last 12 Months) - Line Chart
    - Cash Disbursement by Account - Bar Chart
    - Merchant Account Reserves (Last 12 Months) - Column Chart
- **Chart 03**
    - Top 05 Expense Categories (Last 12 Months) - Bar Chart
    - Payroll by Department (Last 12 Months) - Radar Chart
    - Top Income Sources (Last 12 Months) - Donut Chart
- **Chart 04**
    - Summarized Profit and Loss for Last 3 Months - Tabular
    - Bubble Chart comparing Ads and Revenue

#### Profitability

- Runway
- Merchant Fees Percentage
- Merchant Chargeback Percentage

#### Cashflow

Detailed cashflow analysis showing trends and insights over the last 12 months.

#### Merchant Account

Overview of merchant account performance, including reserves and chargeback rates.

#### Email Campaigns

Analysis of email campaign performance and its impact on revenue.

#### Google Ads

Insights on the effectiveness of Google Ads campaigns in driving sales.

### Color Palettes

**Main Theme:**

- **Background:** DARK GRAY
- **Graph Area:** LIGHT GRAY
- **Income:** BLUE JEANS
- **Expenses:** BITTERSWEET
- **Cash Inflow:** MINT
- **Cash Outflow:** GRAPEFRUIT

### Dashboard Design

![Dashboard Design](https://github.com/user-attachments/assets/4896d5d2-7ede-4fa7-b347-d225927f0d11)


## Conclusion & Future Enhancements 🏁

### Conclusions

- The dashboard provides a clear and concise view of financial health.
- Key performance metrics have shown significant improvements.
- Automation has reduced manual effort in data aggregation.
- The client can now make more informed decisions based on real-time data.

### Future Enhancements

- Integration with additional data sources for deeper insights.
- Implementation of predictive analytics for forecasting.
- Development of a mobile-friendly dashboard version.
- Expansion of visualizations to include additional KPIs.

## Contact 📧

For any queries or further information, please contact me at [zohaib8989@gmail.com](mailto:zohaib8989@gmail.com)
