from typing import Union, List, Dict
from flask import Flask, render_template
from googleapiclient.discovery import build

import pandas as pd
import google.oauth2.service_account

# Consts
SCOPES = ["https://www.googleapis.com/auth/forms.responses.readonly"]
CLIENT_SECRET_PATH = "resources/client_secret.json"
EXCEL_FILE_PATH = "db/test.xlsx"
WAITING_TEXT = "מחשבים שלא טופלו"
NOT_TAKEN_TEXT = "מחשבים שטופלו ולא נלקחו"
TAKEN_TEXT = "מחשבים שטופלו ונלקחו"
COLUMNS_BANK = ['Unit',
                'Email',
                'Designated action',
                'Date',
                'Ofiice segment',
                'Personal number / ID',
                'Serial number (Computer name)',
                'Network',
                'Notes',
                'Phone number',
                'Full name']

# The form ID can be found in the edit mode of any form that was 
# created by the user which made the Google Cloud Console project.
FORM_ID = "1spTaWVM6t2BPGFGhmrfFszV2HZdgjzrSHzbPROny0wg"

# Unique Typing Types
JsonType = List[Dict[Union[str, Dict[str, Dict[str, Union[str, Dict[str, List[Dict[str, str]]]]]]], str]]

# App Initializer
app = Flask(__name__)
app.config["SECRET_KEY"] = "pc-status"


def save_responses_to_excel(parsed_reponses: List[Dict[str, str]]) -> None:
    '''
    This function gets the parsed responese and add every each and one of them that
    to the excel file. Notice that if a computer's serial number is already in the excel,
    it won't be added.

    @params: parsed_reponses -> a parsed responses extracted from the json responses.
    Returns: None.
    '''
    # Load the existing Excel file into a DataFrame
    df = pd.read_excel(EXCEL_FILE_PATH, engine='openpyxl')
    

    for response in parsed_reponses:
        # Check if the serial number is in the serial numbers column to prevent duplicates
        serial_number = response['Serial number (Computer name)'].upper()
        is_serial_in_serials = serial_number in df['מספר סריאלי'].values
        if is_serial_in_serials:
            continue

        # Create a new row as a dictionary with keys matching the column headers
        new_row = {
            'שם מלא': response['Full name'],
            'תאריך כניסת מחשב': response['Date'],
            'הפעולה הנדרשת': response['Designated action'],
            'פרמוט לרשת': response['Network'],
            'מספר סריאלי': serial_number,
            'סגמנט במשרד': response['Ofiice segment'],
            'יחידה': response['Unit'],
            'מספר אישי/ת.ז': response['Personal number / ID'],
            'מייל אזרחי': response['Email'],
            'טלפון אזרחי': response['Phone number'],
            'הערות': response['Notes'],
            'סטטוס': WAITING_TEXT
        }

        # Convert the values in the new row to strings to ensure they are treated as text
        new_row = {key: str(value) for key, value in new_row.items()}

        # Append the new row to the DataFrame
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        try:
            # Write the updated DataFrame back to the Excel file
            df.to_excel(EXCEL_FILE_PATH, index=False, engine='openpyxl')
        except PermissionError as pe:
            print(f"Error: Please close the excel file located in - {EXCEL_FILE_PATH}")
            return


def parse_json_response(json_responses: JsonType) -> List[Dict[str, str]]:
    '''
    This function will get a response in json format, extract the data out of
    it to a list of dictionaries which every dictionary in the list is a single
    form response.
    Please notice that the json reponse contains answers in the following order:
        1. Unit
        2. Email
        3. Designated action
        4. Date
        5. Ofiice segment
        6. Personal number/ ID
        7. Serial number (Computer name)
        8. Network
        9. Notes
        10. Phone number
        11. Full name
    
    This is inconvenient because the form is not ordered in that way, but the json reponse is.

    @params: json_responses     -> a JsonType form response the function will parse.
    Returns: parsed_responses   -> a parsed responses extracted from the json responses.
    '''
    parsed_responses = []

    for response in json_responses:
        single_response = {}
        answers = response["answers"]
        questions_ids = {f"Question {index + 1}": id for index, id in enumerate(answers)}

        # Iterate over the user answers
        for index, answer in enumerate(answers):
            # Retrive the question id of the asnwer
            question_id = answers[answer]["questionId"]

            # Retrive the user answer value
            text_value = answers[answer]["textAnswers"]["answers"][0]["value"]

            # Create a dict to store all the answers by checking
            #   if the question id of the answer is in the questions_ids dict.
            if question_id in questions_ids.values():
                single_response[COLUMNS_BANK[index]] = text_value

        # Append single response to a list
        parsed_responses.append(single_response)

    return parsed_responses



def get_json_response() -> JsonType:
    '''
    This function gets the forms responses in a json format and returns it.

    @params: None.
    Returns: The form's answers in json type.
    '''
    # Authenticate with service account credentials
    credentials = (
        google.oauth2.service_account.Credentials.from_service_account_file(
            CLIENT_SECRET_PATH, scopes=SCOPES
        )
    )

    # Build the Forms service
    service = build("forms", "v1", credentials=credentials)

    # Retrieve form responses
    response = service.forms().responses().list(formId=FORM_ID).execute()

    # Process response data
    responses = response.get("responses", [])

    return responses


@app.route("/", methods=["GET"])
def home_page():
    '''
    This function is responsible to render the main page

    @params: None.
    Returns: None.
    '''
    json_responses = get_json_response()
    parsed_reponses = parse_json_response(json_responses=json_responses)
    save_responses_to_excel(parsed_reponses=parsed_reponses)

    return render_template("home.html", responses=parsed_reponses)


if __name__ == "__main__":
    app.run(debug=True)
