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
        header = data[0]  # This will select the first row as column names.
        values = data[1:]  # This will select everything from the second row onwards as data.
        df = pd.DataFrame(values, columns=header)
        return df
    else:
        print(f"The worksheet {worksheet_name} is empty.")
        return pd.DataFrame()  # return an empty DataFrame if the data is empty

# data = get_data("test_data_sample.xlsx_gpt-3", "ü")
# print(data)


def save_data(sheet_name, worksheet_name, data):
    # Access the Google Sheets document
    spreadsheet = access_sheet(sheet_name)

    # Access the specific worksheet
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        # If the worksheet does not exist, create it
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows="1", cols="1")

    # Clear all the data before writing new
    worksheet.clear()

    # Write the DataFrame to the worksheet
    set_with_dataframe(worksheet, data)
# save_data("test_data_sample.xlsx_gpt-3", data)

def create_user_worksheet(user_name):
    # Access the spreadsheet
    spreadsheet = access_sheet("sorted_param_search_gpt_param_search")

    # Load the data from the master spreadsheet
    master_data = get_data("sorted_param_search_final_gpt_param_search", "Master")  # assuming "Master" is your master worksheet name
    ### sort texts
    # master_data = master_data.sort_values(by='text')
    # print(master_data)
    # Get the number of rows and columns in the master data
    num_rows = len(master_data)
    num_cols = len(master_data.columns)

    # Check if a worksheet with this user's name already exists
    try:
        user_sheet = spreadsheet.worksheet(user_name)
        print(f"Worksheet for user: {user_name} already exists")
    except gspread.WorksheetNotFound:
        # If not, create a new worksheet for this user with the same number of rows and columns as the masterworksheet
        user_sheet = spreadsheet.add_worksheet(title=user_name, rows=str(num_rows), cols=str(num_cols))

        # Populate the new worksheet with the data from the master spreadsheet
        set_with_dataframe(user_sheet, master_data)

        print(f"Created and populated worksheet for user: {user_name}")

    # Now that the user worksheet is populated, get the data from it
    user_data = get_data("sorted_param_search_final_gpt_param_search", user_name)
    # Return the user data
    return user_data


# create_user_worksheet("Marusya4")

### INITIATE STREAMLIT

st.title(" 📰 Text Summarization Analysis")
st.write("""
    In the context of my master's thesis on the topic of "Automatic Text Summarization in German language: ", I need help with evaluation. 
    The steps to be performed are quite simple. There is an original text, an original summary, and several variants of text summaries. 
    Your task is first to provide your nickname, and then to evaluate the summaries based on the criteria provided on the right.
    """)
st.write("Please provide your name:")

user_name = st.text_input('Enter your name')  # Creates a text input box

if user_name:
        # Check if the 'user_name' key exists in the session state
    if 'user_name' not in st.session_state or st.session_state['user_name'] != user_name:
        st.session_state['user_name'] = user_name
            # Load the user_data when the user_name is first submitted
        st.session_state['user_data'] = create_user_worksheet(user_name)
        st.session_state['all_processed'] = False  # Variable to track if all texts have been processed
            # When the user name changes or the app restarts, start from the beginning
        st.session_state['selected_index'] = 0

    if 'user_data' in st.session_state and not st.session_state['all_processed']:
        user_data = st.session_state['user_data']
        print(len(user_data))
        ###### START ANALYSIS
        selected_index = st.session_state['selected_index']

        text_number = st.number_input('Enter text number to jump to', min_value=1, max_value=len(user_data) -1,
                                      value=1)
        if st.button('Jump to text number'):
            st.session_state['selected_index'] = text_number
            st.experimental_rerun()


        # Check if all texts have been processed
        if selected_index >= len(user_data)-1:
            st.write("All texts have been processed :)  Thank you for participation 🩷")
            st.balloons()  # Streamlit balloons
            st.session_state['all_processed'] = True  # Update all_processed when all texts have been processed
            st.stop()


        st.markdown(f"**Text {selected_index + 1} of {len(user_data)}**")

        selected_row = user_data.iloc[selected_index]

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
                'Geld/Finanzen',
                'Klima'
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
                    "dataset_name",
                    "params",
                    "model_name",
                    "topic",
                    "rouge1_scores_text_generated_summary",
                    "rouge1_scores_summary_generated_summary",
                    "rouge2_scores_text_generated_summary",
                    "rouge2_scores_summary_generated_summary",
                    "rougeL_text_to_generated",
                    "rrougeL_scores_text_generated_summary",
                    "rougeL_scores_summary_generated_summary",
                    "bert_score_text_generated_summary",
                    "bert_score_summary_generated_summary"]

                for column in info_columns:
                    if column in selected_row:
                        st.write(f"{column}: {selected_row[column]}")

        if st.button("Next"):
            scores = [st.session_state[criterion] for criterion in criteria]
            for i, criterion in enumerate(criteria):
                # UPDATE DATA
                user_data.at[selected_index, criterion] = scores[i]

            user_data.at[selected_index, 'Comment'] = st.session_state['comment']
            user_data.at[selected_index, 'Category'] = st.session_state['category']

            # Save the updated data to the worksheet
            save_data("sorted_param_search_final_gpt_param_search", st.session_state['user_name'], user_data)

            if 'selected_index' not in st.session_state:
                st.session_state['selected_index'] = 0  # or any other default value

            # Now it's safe to use st.session_state['selected_index'].
            st.session_state['selected_index'] = (st.session_state['selected_index'] + 1) % len(user_data)

            # Reset the scores, comment, and category in the session_state
            for criterion in criteria:
                st.session_state[criterion] = 0
            st.session_state['comment'] = ''
            st.session_state['category'] = categories[0]

                # Rerun the app to show the next text
            st.experimental_rerun()

