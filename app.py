from flask import Flask, render_template
from googleapiclient.discovery import build
import google.oauth2.service_account
from typing import Union, List, Dict

# Consts
SCOPES = ["https://www.googleapis.com/auth/forms.responses.readonly"]
CLIENT_SECRET_PATH = "resources/client_secret.json"
EXCEL_DB_PATH = "db/test.py"

# The form ID can be found in the edit mode of any form that was 
# created by the user which made the Google Cloud Console project.
FORM_ID = "1spTaWVM6t2BPGFGhmrfFszV2HZdgjzrSHzbPROny0wg"

# Unique Typing Types
JsonType = List[Dict[Union[str, Dict[str, Dict[str, Union[str, Dict[str, List[Dict[str, str]]]]]]], str]]

# App Initializer
app = Flask(__name__)
app.config["SECRET_KEY"] = "pc-status"


def save_responses_to_excel(parsed_reponses: List[Dict[str, str]]):
    pass


def parse_json_response(json_responses: JsonType) -> List[Dict[str, str]]:
    '''
    This function will get a response in json format, extract the data out of
    it to a list of dictionaries which every dictionary in the list is a single
    form response.
    Please notice that the json reponse contains answers in the following order:
        1. Unit
        2. Email
        3. Date
        4. Designated action
        5. Ofiice segment
        6. Personal number/ ID
        7. Serial number (Computer name)
        8. Network
        9. Notes
        10. Full name
        11. Phone number
    
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
                single_response[f"Answer {index + 1}"] = text_value

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
