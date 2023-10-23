from typing import Union, List, Dict, Tuple
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


def arrange_responses_by_status(responses: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[Dict[str, str]]]:
    '''
    This function gets the responses unordered by status so it will order them by status and designate every response to it's 
    corresponding list.

    @params: responses -> a list of dictionaries which every dictionary represents a single response with random status.
    Returns: Tuple of three lists -> every list stores it's responses by it's unique status.   
    '''
    waiting_responses = []
    not_taken_responses = []
    taken_responses = []

    for response in responses:
        if response['סטטוס'] == WAITING_TEXT:
            waiting_responses.append(response)
        
        if response['סטטוס'] == NOT_TAKEN_TEXT:
            not_taken_responses.append(response)

        if response['סטטוס'] == TAKEN_TEXT:
            taken_responses.append(response)

    return (waiting_responses, not_taken_responses, taken_responses)


def get_responses_from_excel() -> List[Dict[str, str]]:
    '''
    This function gets the rows of all responses from the excel, transfer them to a list of dictionaries which
    every dictionary represents a single response with the following data in order:
        1. שם מלא
        2. תאריך כניסת מחשב
        3. הפעולה הנדרשת
        4. פרמוט לרשת
        5. מספר סריאלי
        6. סגמנט במשרד
        7. יחידה
        8. מספר אישי/ת.ז
        9. מייל אזרחי
        10. טלפון אזרחי
        11. הערות
        12. סטטוס

    @params: None.
    Returns: responses_dicts -> a list of dictionaries which every dictionary represents a single response.
    '''
    df = pd.read_excel(EXCEL_FILE_PATH,engine='openpyxl',dtype=object,header=None)
    responses_list = df.values.tolist()
    responses_list = responses_list[1:] if len(responses_list) > 0 else ['0','0','0','0','0','0','0','0','0','0','0']
    responses_dicts = []

    for response in responses_list:
        # Create a new dictionary with keys matching the columns' value
        response_dict = {
            'שם מלא': response[0],
            'תאריך כניסת מחשב': response[1],
            'הפעולה הנדרשת': response[2],
            'פרמוט לרשת': response[3],
            'מספר סריאלי': response[4],
            'סגמנט במשרד': response[5],
            'יחידה': response[6],
            'מספר אישי/ת.ז': response[7],
            'מייל אזרחי': response[8],
            'טלפון אזרחי': response[9],
            'הערות': response[10],
            'סטטוס': response[11]
        }

        responses_dicts.append(response_dict)

    return responses_dicts
    


def save_responses_to_excel(parsed_reponses: List[Dict[str, str]]) -> None:
    '''
    This function gets the parsed responese and add every each and one of them that
    to the excel file. Notice that if a computer's serial number is already in the excel,
    it won't be added.

    @params: parsed_reponses -> a parsed responses extracted from the json responses.
    Returns: None.
    '''
    # Load the existing Excel file into a DataFrame
    df = pd.read_excel(EXCEL_FILE_PATH, engine='openpyxl', dtype=str)
    

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

    # Sort responses based on timestamp (assuming 'timestamp' is the key)
    sorted_responses = sorted(responses, key=lambda x: x.get('timestamp', ''))

    return sorted_responses


@app.route("/", methods=["GET"])
def home_page():
    '''
    This function is responsible to render the main page

    @params: None.
    Returns: None.
    '''
    json_responses = get_json_response()
    parsed_responses = parse_json_response(json_responses=json_responses)
    save_responses_to_excel(parsed_reponses=parsed_responses)
    db_responses = get_responses_from_excel()
    waiting_responses, not_taken_responses, taken_responses = arrange_responses_by_status(responses=db_responses)

    return render_template("home.html", 
                           waiting_responses=waiting_responses, 
                           not_taken_responses=not_taken_responses, 
                           taken_responses=taken_responses)


if __name__ == "__main__":
    app.run(debug=True)
