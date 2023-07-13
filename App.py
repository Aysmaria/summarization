import streamlit as st
import pandas as pd
import gspread as gspread
'''
def load_data(file_path):
    return pd.read_excel(file_path)

def save_data(file_path, data):
    data.to_excel(file_path, index=False)

data = load_data('test_params_combos.xlsx')
'''
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name('thesis-392509-283588878017.json', scope)
client = gspread.authorize(creds)

sheet = client.open('data_sample').worksheet('Sheet1')
# row = [name, adr, age, symptoms, gender, email]
# sh.append_row(row)


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

st.markdown(f"**Original Summary:**\n\n{selected_row['summary']}")

st.markdown(f"**Generated Summary:**\n\n{selected_row['generated_summary']}")



with st.sidebar:
    st.markdown("Select criteria")
    criteria = ['Readability', 'Informativeness', 'Fluency', 'Conciseness', 'Factual correctness']
    criteria_info = {
        'Readability': 'It measures how well the summary is fluent and grammatical.',
        'Informativeness': 'It measures how well the summary contains the gist of the original input.',
        'Fluency':'It measures how well the summary is consistent with human language habits.',
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
        data.at[selected_index, criterion] = scores[i]
    data.at[selected_index, 'Comment'] = st.session_state['comment']
    data.at[selected_index, 'Category'] = st.session_state['category']

    if st.button("Next"):
        scores = [st.session_state[criterion] for criterion in criteria]
        for i, criterion in enumerate(criteria):
            # The next row index is (selected_index + 2) because Google Sheets indexes start from 1, not 0.
            # For the column, you should find the column index of your criterion (you may need to update this)
            sheet.update_cell(selected_index + 2, 82, scores[i])
        # You should replace 'column_number' with the actual column number for 'Comment' and 'Category'
        sheet.update_cell(selected_index + 2, 83, st.session_state['comment'])
        sheet.update_cell(selected_index + 2, 84, st.session_state['category'])

        # Update the selected_index for the next iteration
        st.session_state['selected_index'] = (selected_index + 1) % len(sheet)

        # Reset the criteria scores, comment and category for the next iteration
        for criterion in criteria:
            st.session_state[criterion] = 0
        st.session_state['comment'] = ''
        st.session_state['category'] = categories[0]

        # This will rerun the script, effectively refreshing the page
        st.experimental_rerun()