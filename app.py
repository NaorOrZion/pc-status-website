from flask import Flask, render_template
from googleapiclient.discovery import build
import google.oauth2.service_account
from typing import Union, List, Dict

# Consts
SCOPES = ["https://www.googleapis.com/auth/forms.responses.readonly"]
CLIENT_SECRET_PATH = "resources/client_secret.json"
QUESTIONS_IDS = {"Question 1": "51d60a34",
                 "Question 2": "115635e7",
                 "Question 3": "5cd564b4"}

# The form ID can be found in the edit mode of any form that was 
# created under the user which made the Google Cloud Console project.
FORM_ID = "1spTaWVM6t2BPGFGhmrfFszV2HZdgjzrSHzbPROny0wg"

# Unique Typing Types
JsonType = List[Dict[Union[str, Dict[str, Dict[str, Union[str, Dict[str, List[Dict[str, str]]]]]]], str]]

# App Initializer
app = Flask(__name__)
app.config["SECRET_KEY"] = "pc-status"


def parse_json_response(json_responses: JsonType) -> List[Dict[str, str]]:
    '''
    This function will get a response in json format, extract the data out of
    it to a list of dictionaries which every dictionary in the list is a single
    form response.

    @params: json_responses     -> a JsonType form response the function will parse.
    Returns: parsed_responses   -> a parsed responses extracted from the json responses.
    '''
    parsed_responses = []

    for response in json_responses:
        single_response = {}
        answers = response["answers"]
        questions_ids = {f"Question {index + 1}": id for index, id in enumerate(answers)}

        for index, answer in enumerate(answers):
            question_id = answer["questionId"]
            text_value = answer["textAnswers"]["answers"][0]["value"]

            # Replace the hard coded question ids with iteration
            # match question_id:
            #     case questions_ids[f"Question {index + 1}"]:
            #         single_response["Answer 1"] = text_value

            #     case questions_ids["Question 2"]:
            #         single_response["Answer 2"] = text_value

            #     case questions_ids["Question 3"]:
            #         single_response["Answer 3"] = text_value

            #     case _:
            #         None



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
    dict_reponses = parse_json_response(json_responses=json_responses)

    return render_template("home.html", responses=json_responses)


if __name__ == "__main__":
    app.run(debug=True)
