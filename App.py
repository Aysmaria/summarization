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
    Access the Google's spreadsheet.
    '''
    # From local computer
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes = scope)
    gc = gspread.authorize(credentials)
    try:
        # Try to open the sheet
        sheet = gc.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        # If the sheet doesn't exist, create it
        sh = gc.create(sheet_name)
        sheet = gc.open(sheet_name)
    return sheet.sheet1  # Access the first worksheet in the spreadsheet


'''
@st.cache_data
def get_data():
        
        
        sheet = access_sheet('Test')
        data = sheet.get_all_values()
        df = pd.DataFrame(data[1:],
                          columns=['text', 'original_summary', 'topic', 'title', 'dataset_name', 'generated_summary',
                                   'params', 'bert_score_text_generated_summary',
                                   'bert_score_summary_generated_summary', 'rouge1_scores_text_generated_summary',
                                   'rouge1_scores_summary_generated_summary', 'rouge2_scores_text_generated_summary',
                                   'rouge2_scores_summary_generated_summary', 'rougeL_scores_text_generated_summary',
                                   'rougeL_scores_summary_generated_summary', 'model_name', 'Readability',
                                   'Informativeness', 'Fluency', 'Conciseness', 'Factual correctness'])

        # df['new_column_name'] = None
        print(df)
        # set_with_dataframe(sheet, df)
        return df
'''


def get_data():
    '''
    Read the data from the Google sheet
    Returns
    -------
    df : Pandas dataframe
    '''
    sheet = access_sheet('Test')
    data = sheet.get_all_values()
    header = data[0]  # This will select the second row as your column names.
    values = data[1:]  # This will select everything from the third row onwards as your data.
    df = pd.DataFrame(values, columns=header)

    print(df.columns)
    return df


def save_data(sheet_name, data):
    '''
    Save the data to a Google sheet.
    '''
    sheet = access_sheet(sheet_name)
    set_with_dataframe(sheet, data)

'''
def load_data(file_path):
    return pd.read_excel(file_path)


def save_data(file_path, data):
    data.to_excel(file_path, index=False)
'''

# data = get_data('test_params_combos.xlsx')
data = get_data()

# Ask for the user's name at the start of the session
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = st.text_input('Please enter your name to begin')
    # Prevent the rest of the app from running until the user_id is set
    if st.session_state['user_id'] == '':
        st.stop()


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
        # SAVE DATA AFTER EACH UPDATE
        # save_data('Test', data)
    # Update the data
    data.at[selected_index, 'Comment'] = st.session_state['comment']
    data.at[selected_index, 'Category'] = st.session_state['category']
    data.at[selected_index, 'User'] = st.session_state['user_id']

    # Save the data to the sheet named after the user
    save_data(st.session_state['user_id'], data)

    # Add user_id to the row in the DataFrame
    data.at[selected_index, 'User'] = st.session_state['user_id']
    save_data('Test', data)  # 'Test' should be the name of your Google Spreadsheet.


    st.session_state['selected_index'] = (selected_index + 1) % len(data)

    for criterion in criteria:
        st.session_state[criterion] = 0
    st.session_state['comment'] = ''
    st.session_state['category'] = categories[0]
    st.experimental_rerun()