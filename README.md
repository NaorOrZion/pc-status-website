# pc-status-website
This website is designed to track the computers' status at the lab.

## How to use and initialize the website?

### Prerequities

-   Python3
-   Google Cloud Console Project
-   Google Form
-   Gmail

## How does it work?

This project takes a google form responses data. Every response will contain a customer data about about his computer
which will be transferred to the website and from now on the computer can be tracked easily. A computer status can be:
WAITING -> FIXED AND NOT TAKEN -> TAKEN.
You can manage the computer's status in any time.
A computer that went from WAITING to FIXED AND NOT TAKEN will send an email to the customer to come and take it.

To use this program you must have a Google Cloud Console Project that has 2 packages: "Gmail API" and "Google Forms API".

#### How to open a google cloud console project?

1.  Visit: https://console.cloud.google.com/apis/dashboard
2.  Open a new project.

#### How to connect a Google Forms API package and use it?

1. Open your google cloud console project.
2. In the left bar: click on "Library".
3. Search for "Google Forms API" and download the first package.
4. Now create a service account in the project in this url: https://console.cloud.google.com/iam-admin/serviceaccounts
5. Give it a name and ID.
6. Give a role to the service.
7. Give a role to a google user which will use this project.
8. Now you have permissions to collaborate with a form that the user who has permissions created.
9. Go to your form in edit mode and copy the last part of the url (should look like this: "1spTaWVM6t2BPGFGhmrfFszV2HZdgjzrSHzbPROny0wg").
10. Paste it in the variable "FORM_ID" in "app.py".

#### How to connect a Gmail API package and use it?

Open google with the google account you synced your contacts with, than:
1. Open your google cloud console project.
3. In the left bar: click on "Library".
4. Search for "Gmail API" and download the first package.
5. In the left bar: click on "Credentials".
6. Click on "Create credentials".
7. Create an OAuth Id and pick a name for the project.
8. When requested to fill the "Application type", pick Desktop App and pick a name.
9. Now download the "Client JSON".
10. Change it's name to "credentials.json".
11. Place this file in your github project in the folder "resources".

### Installation

1. Clone the github project to a designated folder in your desktop.
```sh
git clone https://github.com/NaorOrZion/pc-status-website
```

2. Move to the cloned folder.
```sh
cd pc-status-website
```
    
3. Create a Virtual environment and activate it.
```sh
python -m venv venv
venv\Scripts\activate
```

4. Install the requirements.
```sh
pip install -r requirements.txt
```

5. Run the main file (Notice that it will run on 127.0.0.1:5000 at it currently in development).
```sh
python app.py
```
