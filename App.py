import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from gspread_dataframe import set_with_dataframe


    # Read database on Google sheet
    ###############################
@st.cache_resource
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

def get_data(sheet_name):
    spreadsheet = access_sheet(sheet_name)
    # Access the first worksheet
    sheet = spreadsheet.get_worksheet(0)
    data = sheet.get_all_values()
    if data:  # check if data is not empty
        header = data[0]  # This will select the first row as your column names.
        values = data[1:]  # This will select everything from the second row onwards as your data.
        df = pd.DataFrame(values, columns=header)
        print(df.columns)
        return df
    else:
        print("The sheet is empty")
        return pd.DataFrame()  # return an empty DataFrame


# data = get_data("test_data_sample.xlsx_gpt-3")

def save_data(sheet_name, data):
  
    sheet = access_sheet(sheet_name).sheet1  # Access the first worksheet
    set_with_dataframe(sheet, data)

# save_data("test_data_sample.xlsx_gpt-3", data)


def create_user_worksheet(user_name):
    # Access the spreadsheet
    spreadsheet = access_sheet("test_data_sample.xlsx_gpt-3")

    # Create a new worksheet for this user
    user_sheet = spreadsheet.add_worksheet(title=user_name, rows="100", cols="20")

    # Load the data from the master spreadsheet
    master_data = get_data("test_data_sample.xlsx_gpt-3")

    # Populate the new worksheet with the data from the master spreadsheet
    set_with_dataframe(user_sheet, master_data)

    print(f"Created and populated worksheet for user: {user_name}")

# create_user_worksheet("M")

# Ask for the user's name at the start of the session
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = st.text_input('Please enter your name to begin')
else:
    # Create a new spreadsheet for this user if it doesn't exist
    access_sheet(st.session_state['user_name'])
        # Create and populate the user's spreadsheet with data from the master spreadsheet
    create_user_worksheet(st.session_state['user_name'])

    # Load the data from the user's spreadsheet
    user_data = get_data(st.session_state['user_name'])
    print(user_data)
    # Display the data to the user
    st.write(user_data)

'''
    st.title("Text Summarization Analysis")

    if 'selected_index' not in st.session_state:
        st.session_state['selected_index'] = 0

    selected_index = st.session_state['selected_index']
    # Check if all texts have been processed
    if selected_index >= len(data):
        st.write("All texts have been processed. Algorithm finished.")
        st.stop()

    st.markdown(f"**Text {selected_index + 1} of {len(data)}**")

    selected_row = data.iloc[selected_index]

    st.markdown(f"**Category**\n\n{selected_row['topic']}")

    st.markdown(f"**Original Text:**\n\n{selected_row['text']}")

    st.markdown(f"**Original Summary:**\n\n{selected_row['original_summary']}")

    st.markdown(f"**Generated Summary:**\n\n{selected_row['generated_summary']}")

    with st.sidebar:
        st.markdown("Select criteria")
        criteria = ['Readability', 'Informativeness', 'Fluency', 'Conciseness', 'Factual correctness']
        criteria_info = {
            'Readability': 'It measures how well the summary is fluent and grammatical.',
            'Informativeness': 'It measures how well the summary contains the gist of the original input.',
            'Fluency': 'It measures how well the summary is consistent with human language habits.',
            'Conciseness': 'It measures whether the summary is simple and easy to understand (less redundancy)',
            'Factual correctness': 'It indicates whether the facts described in the summary are consistent with the original document, which is the most critical factor affecting the usability of the summary.'

        }

        for criterion in criteria:
            if criterion not in st.session_state:
                st.session_state[criterion] = 0

        for criterion in criteria:
            st.session_state[criterion] = st.sidebar.slider(
                criterion,
                0,
                5,
                st.session_state[criterion],
                help=criteria_info[criterion]
            )

    categories = [
        'Undefined',
        'Politik',
        'Wirtschaft',
        'Panorama',
        'Sport',
        'Reise',
        'Auto',
        'Digital',
        'Geld/Finanzen'
    ]

    categories_info = {
        'Undefined': "it's hard to identify",
        'Politik': 'Politische Themen und Entscheidungen, Migration, Asylrecht, Grenzsicherheit, Europäischen Union',
        'Wirtschaft': 'Die wirtschaftliche Aspekte, die Wechselwirkungen zwischen Wirtschaft, Politik und Verbrauchern. Wirtschaftlichen Entscheidungen, Marktbedingungen und politischen Strategien',
        'Panorama': 'Aktuelle Erignisse, Unterhaltungs- & Klatschwert',
        'Sport': 'Sportberichterstattung, Sportarten',
        'Reise': 'Landschaftliche Aspekte, Reisebericht, Reiseempfehlung, Mobilität, Verkehrsmittelnutzung, Tipps und Regeln für Reisen',
        'Auto': 'Automobilindustrie, Nachhaltigkeit, Straßerverkehr, Sicherheit',
        'Digital': 'Technische Innovatonen, Digitale Geräte, Software, Online-Dienste, KI, Nutzung von Technologien',
        'Geld/Finanzen': 'Geldanlagen, Währungskrise, das Verhalten von Menschen im Zusammenhang mit Geld, Inflation, Preisen, Löhnen',
    }

    if 'category' not in st.session_state:
        st.session_state['category'] = categories[0]

    st.session_state['category'] = st.sidebar.radio(
        'Choose a category',
        categories,
        index=categories.index(st.session_state['category'])
    )

    st.sidebar.markdown(categories_info[st.session_state['category']])

    if 'comment' not in st.session_state:
        st.session_state['comment'] = ''

    st.session_state['comment'] = st.sidebar.text_input("Comment", st.session_state['comment'])

    if st.button("Show Additional Information"):
        info_columns = [
            "title",
            "dataset",
            "params",
            "model",
            "temperature",
            "max_tokens",
            "topic",
            "url",
            "date",
            "rouge1_text_to_generated",
            "rouge2_text_to_generated",
            "rougeL_text_to_generated",
            "rouge1_summary_to_generated",
            "rouge2_summary_to_generated",
            "rougeL_summary_to_generated",
            "bert_text_to_generated",
            "bert_summary_to_generated"]

        for column in info_columns:
            if column in selected_row:
                st.write(f"{column}: {selected_row[column]}")

    if st.button("Next"):
        scores = [st.session_state[criterion] for criterion in criteria]
        for i, criterion in enumerate(criteria):
            # UPDATE DATA
            data.at[selected_index, criterion] = scores[i]

        data.at[selected_index, 'Comment'] = st.session_state['comment']
        data.at[selected_index, 'Category'] = st.session_state['category']

        # Add user_id to the row in the DataFrame
        data.at[selected_index, 'User'] = st.session_state['user_id']

        # Save this row of data to the user's own spreadsheet
        save_data(st.session_state['user_id'], data)

        st.session_state['selected_index'] = (selected_index + 1) % len(data)

        for criterion in criteria:
            st.session_state[criterion] = 0
        st.session_state['comment'] = ''
        st.session_state['category'] = categories[0]
        st.experimental_rerun()
'''