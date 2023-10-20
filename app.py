from flask import Flask, render_template
from googleapiclient.discovery import build
import google.oauth2.service_account
from typing import Union, List, Dict

# Consts
SCOPES = ["https://www.googleapis.com/auth/forms.responses.readonly"]
CLIENT_SECRET_PATH = "resources/client_secret.json"

# The form ID can be found in the edit mode of any form that was 
# created under the user which made the Google Cloud Console project.
FORM_ID = "1spTaWVM6t2BPGFGhmrfFszV2HZdgjzrSHzbPROny0wg"

# Special Typing Types
JsonType = List[Dict[Union[str, Dict[str, Dict[str, Union[str, Dict[str, List[Dict[str, str]]]]]]], str]]

# App Initializer
app = Flask(__name__)
app.config["SECRET_KEY"] = "pc-status"


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
    responses = get_json_response()
    return render_template("home.html", responses=responses)


if __name__ == "__main__":
    app.run(debug=True)
