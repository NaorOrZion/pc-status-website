from typing import Union, List, Dict, Tuple
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from googleapiclient.discovery import build
from email.message import EmailMessage

import ssl
import smtplib
import pandas as pd
import google.oauth2.service_account

# Global
get_responses = True

# Consts
SCOPES = ["https://www.googleapis.com/auth/forms.responses.readonly", "https://www.googleapis.com/auth/forms.currentonly", ]
CLIENT_SECRET_PATH = "resources/client_secret.json"
EXCEL_FILE_PATH = "db/test.xlsx"

## Email consts
EMAIL_SENDER = "naororzion101@gmail.com"
EMAIL_PASSWORD = "inbx ufab rjfq xxnh"
EMAIL_SUBJECT = "מתקן לוטם סיימו לתקן את המחשב שלך!"
EMAILֹ_BODY = "צוות מתקן לוטם תיקנו את המחשב שלך!\nאפשר להגיע לקחת אותו מהצוות.\nבברכה, צוות מתקן לוטם."

## Text consts
WAITING_TEXT = "מחשבים שלא טופלו"
NOT_TAKEN_TEXT = "מחשבים שטופלו ולא נלקחו"
TAKEN_TEXT = "מחשבים שטופלו ונלקחו"
DELETED_TEXT = "נמחקו"
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


def send_email(email_reciver: str) -> None:
    '''
    This function gets an email string as a parameter and send an email
    from EMAIL_SENDER to the reciver about his computer status.

    @params: email_reciver -> a string representing the email to send to.
    Returns: None.
    '''
    email = EmailMessage()
    email['From'] = EMAIL_SENDER
    email['To'] = email_reciver
    email['Subject'] = EMAIL_SUBJECT
    email.set_content(EMAILֹ_BODY)
    
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_SENDER, email_reciver, email.as_string())


def change_row_status(move_to_status: str, response_id: str):
    '''
    This function edits a status to a designated status in a row from the excel by the response id.
    It edits the row's status to "move_to_status".

    @params: move_to_status -> current status of the row,
             response_id -> a response id to match one of the values in the column 'מזהה תשובה'.
    Returns: None.
    '''
    # Load the Excel file into a DataFrame
    df = pd.read_excel(EXCEL_FILE_PATH, engine='openpyxl')

    # Identify the row index based on the specified column value
    row_index = df.index[df['מזהה תשובה'] == response_id].tolist()[0]

    # Edit the cell value using the 'at' accessor to "נמחקו"
    df.at[row_index, 'סטטוס'] = move_to_status

    try:
        # Write the updated DataFrame back to the Excel file
        df.to_excel(EXCEL_FILE_PATH, index=False, engine='openpyxl')

    except PermissionError as pe:
        print(f"Error: Please close the excel file located in - {EXCEL_FILE_PATH}")
        return


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
        13. מזהה תשובה

    @params: None.
    Returns: responses_dicts -> a list of dictionaries which every dictionary represents a single response.
    '''
    df = pd.read_excel(EXCEL_FILE_PATH,engine='openpyxl',dtype=object,header=None)
    responses_list = df.values.tolist()
    responses_list = responses_list[1:] if len(responses_list) > 0 else ['0','0','0','0','0','0','0','0','0','0','0', '0']
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
            'סטטוס': response[11],
            'מזהה תשובה': response[12]
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
        if response['Response ID'] in df['מזהה תשובה'].values:
            continue

        # Create a new row as a dictionary with keys matching the column headers
        new_row = {
            'שם מלא': response['Full name'],
            'תאריך כניסת מחשב': response['Date'],
            'הפעולה הנדרשת': response['Designated action'],
            'פרמוט לרשת': response['Network'],
            'מספר סריאלי': response['Serial number (Computer name)'].upper(),
            'סגמנט במשרד': response['Ofiice segment'],
            'יחידה': response['Unit'],
            'מספר אישי/ת.ז': response['Personal number / ID'],
            'מייל אזרחי': response['Email'],
            'טלפון אזרחי': response['Phone number'],
            'הערות': response['Notes'],
            'סטטוס': WAITING_TEXT,
            'מזהה תשובה': response['Response ID']
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
        12. Response ID
    
    This is inconvenient because the form is not ordered in that way, but the json reponse is.

    @params: json_responses     -> a JsonType form response the function will parse.
    Returns: parsed_responses   -> a parsed responses extracted from the json responses.
    '''
    parsed_responses = []

    for response in json_responses:
        single_response = {}
        response_id = response['responseId']
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

        # Add response ID to every response
        single_response['Response ID'] = response_id

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


@app.route('/set-row-status', methods=['POST'])
def set_row_status() -> None:
    '''
    This function is responsible to retrieve the post request of the delete button in the main page.

    @params: None.
    Returns: None.
    '''

    # Get the value of 'action' from query parameters
    action = request.args.get('action')

    # Get metadata from html input
    serial_number = request.form.get('serial_number')
    response_id = request.form.get('response_id')

    match action:
        case "delete":
            change_row_status(move_to_status=DELETED_TEXT, response_id=response_id)
        case "move from waiting to not taken":
            change_row_status(move_to_status=NOT_TAKEN_TEXT, response_id=response_id)
        case "move from waiting to taken":
            change_row_status(move_to_status=TAKEN_TEXT, response_id=response_id)
        case "move from not taken to waiting":
            change_row_status(move_to_status=WAITING_TEXT, response_id=response_id)
        case "move from not taken to taken":
            change_row_status(move_to_status=TAKEN_TEXT, response_id=response_id)
        case "move from taken to not taken":
            change_row_status(move_to_status=NOT_TAKEN_TEXT, response_id=response_id)
            send_email()
        case "move from taken to waiting":
            change_row_status(move_to_status=WAITING_TEXT, response_id=response_id)


    global get_responses
    get_responses = False

    return redirect("/")


@app.route("/", methods=["GET"])
def home_page():
    '''
    This function is responsible to render the main page

    @params: None.
    Returns: None.
    '''
    global get_responses
    if get_responses is True:
        json_responses = get_json_response()
        parsed_responses = parse_json_response(json_responses=json_responses)
        save_responses_to_excel(parsed_reponses=parsed_responses)

    get_responses = True

    db_responses = get_responses_from_excel()
    waiting_responses, not_taken_responses, taken_responses = arrange_responses_by_status(responses=db_responses)

    return render_template("home.html", 
                           waiting_responses=waiting_responses, 
                           not_taken_responses=not_taken_responses, 
                           taken_responses=taken_responses)


if __name__ == "__main__":
    app.run(debug=True)
