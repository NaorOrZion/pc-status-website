from flask import Flask, render_template
from googleapiclient.discovery import build
import google.oauth2.service_account

# Consts
FORM_ID = "1M1WV-FrjumLRmCSOGmXlN1bQ9A3agS9Znt-pdCzT9pk"
SCOPE = "https://www.googleapis.com/auth/forms.responses.readonly"
CLIENT_SECRET_PATH = "resources/client_secret.json"

# App Initializer
app = Flask(__name__)
app.config["SECRET_KEY"] = "pc-status"

@app.route("/", methods=["GET"])
def home():
    try:
        # Authenticate with service account credentials
        credentials = google.oauth2.service_account.Credentials.from_service_account_file(
            CLIENT_SECRET_PATH,
            scopes=SCOPE
        )

        # Build the Forms service
        service = build('forms', 'v1', credentials=credentials)

        # Retrieve form responses
        response = service.forms().responses().list(formId=FORM_ID).execute()

        # Process response data
        responses = response.get('responses', [])
        print(responses)
        return render_template("home.html")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    app.run(debug=True)
