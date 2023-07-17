import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from gspread_dataframe import set_with_dataframe


# Read database on Google sheet
###############################

def access_sheet(sheet_name):
    '''
    Access or create a Google Sheets document.
    '''
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes = scope)
    gc = gspread.authorize(credentials)

    # Attempt to open an existing sheet, if it doesn't exist, create a new one
    try:
        sheet = gc.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        sheet = gc.create(sheet_name)

    print("Accessed file:", sheet_name)
    return sheet

# access_sheet("test_data_sample.xlsx_gpt-3")

# access master spreadsheet and worksheet
def get_data(sheet_name, worksheet_name):
    spreadsheet = access_sheet(sheet_name)
    # Access the specific worksheet
    try:
        sheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        print(f"No worksheet named {worksheet_name} in the spreadsheet.")
        return pd.DataFrame()  # return an empty DataFrame if the worksheet is not found

    data = sheet.get_all_values()
    if data:  # check if data is not empty
        header = data[0]  # This will select the first row as your column names.
        values = data[1:]  # This will select everything from the second row onwards as your data.
        df = pd.DataFrame(values, columns=header)
        # print(df.columns)
        return df
    else:
        print(f"The worksheet {worksheet_name} is empty.")
        return pd.DataFrame()  # return an empty DataFrame if the data is empty

# data = get_data("test_data_sample.xlsx_gpt-3", "ü")
# print(data)

def save_data(sheet_name, data):
    sheet = access_sheet(sheet_name) # Access the first worksheet
    set_with_dataframe(sheet, data)

# save_data("test_data_sample.xlsx_gpt-3", data)
def create_user_worksheet(user_name):
    # Access the spreadsheet
    spreadsheet = access_sheet("test_data_sample.xlsx_gpt-3")

    # Check if a worksheet with this user's name already exists
    try:
        user_sheet = spreadsheet.worksheet(user_name)
        print(f"Worksheet for user: {user_name} already exists")
    except gspread.WorksheetNotFound:
        # If not, create a new worksheet for this user
        user_sheet = spreadsheet.add_worksheet(title=user_name, rows="100", cols="20")

        # Load the data from the master spreadsheet
        master_data = get_data("test_data_sample.xlsx_gpt-3", "masterworksheet")  # assuming "Master" is your master worksheet name

        # Populate the new worksheet with the data from the master spreadsheet
        set_with_dataframe(user_sheet, master_data)

        print(f"Created and populated worksheet for user: {user_name}")

    # Now that the user worksheet is populated, get the data from it
    user_data = get_data("test_data_sample.xlsx_gpt-3", user_name)
    print(user_data)
    # Return the user data
    return user_data

# create_user_worksheet("Marusya4")

### INITIATE STREAMLIT
st.write("Please provide your name:")

user_name = st.text_input('Enter your name')  # Creates a text input box

if user_name:
    st.write(f"Welcome, {user_name}. Creating your worksheet...")
    # create_user_worksheet(user_name)

    if 'user_name' not in st.session_state:
        st.session_state['user_name'] = user_name
        print(st.session_state['user_name'])

    if st.button('Start'):
            # Load user data
        user_data = create_user_worksheet(user_name)
        st.dataframe(user_data)

else:
    st.write("Waiting for user name...")