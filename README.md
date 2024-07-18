# Business Insights Dashboard

## Introduction 👋

This project aims to develop a comprehensive financial dashboard using Power BI, extracting and visualizing data from QuickBooks Online and several other sources like Google AdSpend, Google Sheets, etc to provide valuable insights for informed decision-making.

## Problem Statement 🔍

The client was struggling to have a single source of truth to monitor the financial matrices from several different data sources. This project addresses the need to have a centralized Dashboard that offers key financial KPIs & insights for the client to make timely and efficient decisions.

## Deliverables 📦

- Combining the monthly csv files extracted from QuickBooks Online in Google Drive into combined.csv and upload that to the same Google Drive folder using a Python script
- Get the Email Campaign Data maintained in a Google Sheet and link it with Power BI
- Fetch data from Google Ad into Power BI to visualize
- Get data from several Merchant Accounts to be visualized in Power BI
- Create a comprehensive Financial Dashboard in Power BI visualizing all the key financial metrics
- Documentation of the entire process for reproducibility

## Process Guide 📝

### 1. Data Source and Structure 🗂️

#### Data Aggregation Script

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

#### Link to Google Sheets

- Combined csv was then linked to Power BI using
- Get Data >> Web
- https://docs.google.com/spreadsheets/d/{SpreadsheetID}/gviz/tq?tqx=out:csv&sheet=SheetName
   - SpreadSheetID is the specific portion of the csv URL
   - Name is the Tab Name from the Google Sheet

### 2. Data Modelling 📊

The data modeling involved structuring the extracted financial data to ensure accurate relationships between different datasets, facilitating effective analysis and reporting.

![image](https://github.com/user-attachments/assets/03f3f874-d141-489d-ab96-bb7e8aab5fa9)


### 3. Data Tables 📋

The main data tables include:
- CalendarTable (Contains the Dat hierarchy)
- ChartOfAccounts (Contains the Chart of Accounts from QuickBooks Online)
- JournalEntries (Contain all the Journal Entries merged into a single csv via python)

### 4. DAX Measures & KPIs 🧮

#### Summary Tab

Key measures include:
- YTD Income

``` DAX
YTDIncome = 
    ABS(
        CALCULATE(
            SUM(JournalEntries[Debit]) - SUM(JournalEntries[Credit]), // Calculate net income (Debit - Credit)
            FILTER(
                ChartOfAccounts,
                ChartOfAccounts[Classification] = "Income" // Filter to include only income accounts
            ),
            FILTER(
                CalenderTable,
                CalenderTable[Date] >= EOMONTH(TODAY(), -MONTH(TODAY())) + 1 && // From the first day of the current year
                CalenderTable[Date] <= EOMONTH(TODAY(), -1) // Until the last day of the previous month
            )
        )
    )
```

- Last12Months Income

``` DAX
12MonthsIncome = 
    ABS(
        CALCULATE(
            SUM(JournalEntries[Debit]) - SUM(JournalEntries[Credit]), // Calculate net income (Debits - Credits)
            FILTER(
                ChartOfAccounts,
                ChartOfAccounts[Classification] = "Income" // Filter to include only income accounts
            ),
            FILTER(
                CalenderTable,
                CalenderTable[Date] >= EOMONTH(TODAY(), -13) + 1 && // From the first day of 12 months ago
                CalenderTable[Date] <= EOMONTH(TODAY(), -1) + 1 // Until the last day of the previous month
            )
        )
    ) // Return the absolute value of the calculated income over the last 12 months
```

- Burn Rate

``` DAX
BurnRate = 
    DIVIDE(
        CALCULATE(
            SUM(JournalEntries[Debit]) - SUM(JournalEntries[Credit]),
            FILTER(
                ChartOfAccounts,
                ChartOfAccounts[Classification] = "Expense" // to filter the transaction just for expecount
            ),
            FILTER(
                CalenderTable,
                CalenderTable[Date] >= EOMONTH(TODAY(), -4) + 1 && // to calculate from first day of third last month
                CalenderTable[Date] < EOMONTH(TODAY(), -1) + 1 // to calculate until last day of previous month
            )
        ),
        3
    )
```
  
- Runway

``` DAX
Runway = 
    FORMAT(
        DIVIDE(
            _CashMeasures[CashBalance],
            [BurnRate]
        ),
        "###,##0.0"
    ) & " Months"
```

- Cash Running Balance

``` DAX
CashBalance = 
CALCULATE(
    // Calculate the net sum of Debit and Credit for Bank accounts
    CALCULATE(
        SUM(JournalEntries[Debit]) - SUM(JournalEntries[Credit]),
        FILTER(
            ChartOfAccounts, 
            // Filter for accounts of type "Bank"
            ChartOfAccounts[Type] = "Bank"
        )
    ),
    // Filter dates to consider only those that are on or after the selected date
    FILTER(
        ALLSELECTED('CalenderTable'[Date]),
        ISONORAFTER('CalenderTable'[Date], MAX('CalenderTable'[Date]), DESC)
    )
)
```
- Greetings

``` DAX
GreetingMessage = 
    VAR CurrentHour = HOUR(NOW())
    RETURN
    SWITCH(
        TRUE(),
        CurrentHour < 12, "Good Morning Erik 🌤️",
        CurrentHour < 18, "Good Afternoon Erik 🌞",
        "Good Evening Erik 🌙"
    )

```

- Snapshot of all the Measures

![image](https://github.com/user-attachments/assets/a5156170-697a-471b-b05f-695b598ff01f)


### 5. Dashboard Design **🎨**

#### Desktop Design & Layout

![Dashboard Design](https://github.com/user-attachments/assets/4896d5d2-7ede-4fa7-b347-d225927f0d11)

#### Mobile Design & Layout

![image](https://github.com/user-attachments/assets/547827fc-9872-4085-98a6-cdf4461a8c7f)

#### Color Palettes

![Color Pallets](https://github.com/user-attachments/assets/095019ff-25f4-40de-bccd-f41e3454c025)

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
