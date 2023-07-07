# CIXORS
Cixors is a URL Shortener application. This is the API built with Flask RestX

## Table of Contents
 - [About](#about)
 - [Features](#features)
     - [Url Shortening](#url-shortening)
     - [Custome URLs](#custome-urls)
     - [QRCode Generation](#qrcode-generation)
     - [Analytics and History](#analytics-and-history)
 - [Installation and Usage](#installation-and-usage)
    - [How to run the app locally (Installation)](#how-to-run-the-app-locally)
    - [Usage](#usage)
 - [Endpoints](#endpoints)
    - [Auth Enpoints](#auth-enpoints)
    - [User Enpoints](#user-enpoints)
    - [URL Enpoints](#url-enpoints)
 - [Languages and Tools Used](#languages-and-tools-used)
 - [Screenshots](#screenshots)
 - [Acknowledgements](#acknowledgements)


## About
In today’s world, it’s important to keep things as short as possible, and this applies to more concepts than you may realize. From music, speeches, to wedding receptions. Cixors is a simple tool which makes URLs as short as possible.
Cixors is a URL shortener RESTFul-API which was built using python Flask and Flask-RestX 

## Features

### Url Shortening
<img align="center" src="https://qph.cf2.quoracdn.net/main-qimg-cde2acf9623ce82ba8fd7c021df8d4dd-lq" alt="url_cut" />
Cixors allows users to shorten URLs by pasting a long URL into the Cixors platform and a shorter URL gets automatically generated. The shortened URL is designed to be as short as possible, making it easy to share on social media or through other channels.

### Custome URLs
<img align="center" src="https://beyondplm.com/wp-content/uploads/2014/03/plm-customization.jpg" alt="customize" />
Cixors also allows users to customize their shortened URLs. Users can customize the shorl URL to reflect their brand or content. To choose their own custom domain name as well, users will need to integrate our API on thier website and send a request with thier customized domian name. Our API can be found [here](https://cixors.onrender.com/) for testing. This feature is particularly useful for individuals or small businesses who want to create branded links for their business

### QRCode Generation
<img align="center" src="https://staveapps.com/wp-content/uploads/2021/03/1792-1.png" alt="customize" />
Cixors allows users to also generate QR codes for the shortened URLs. Users can download the QR code image and use it in their promotional materials or/and on their website.

### Analytics and History
<img align="center" src="https://www.searchenginejournal.com/wp-content/uploads/2020/02/10-great-google-analytics-alternatives-5e4175671fa6a.png" alt="customize" />
Cixors provides basic analytics that allow users to track their shortened URL's performance. Users can see how many clicks their shortened URL has received and where the clicks are coming from.

It also allows users to see the history of links they’ve created so they can easily find and reuse links they have previously created.

## Installation and Usage
- To try this application, you can either clone and run it locally on your PC or visit the website [here](https://cixor.onrender.com/) or the hosted [API](https://cixor.onrender.com/) to check it out.

- Follow the steps below to run and test the application locally

## How to run the app locally
1. Clone this app
```
git clone https://github.com/kojosimtema/cixors.git
``` 
2. cd to the root directorate of the project and create your virtual environment
```
cd cixors

python -m venv env_name
``` 
3. Activate your virtual environment
```
source env_name/Scripts/activate "for windows"
``` 
```
source env_name/bin/activate "for linus and MacOS"
``` 
4. Install all packages from the requirements.txt file
```
pip install -r requirements.txt
``` 


## Usage
**Before you run the application locally, do the following:**

**1. In the run.py file remove the *"config=config_dict['prod']"* argument from the create_app function as below to run in development mode**
```
from api import create_app
from api.main.config.config import config_dict

app = create_app(config=config_dict['prod'])

if __name__ == '__main__':
    app.run()
```
```
from api import create_app
from api.main.config.config import config_dict

app = create_app()

if __name__ == '__main__':
    app.run()
```
**2. Navigate to api/main/config and comment line 23 to 25 and line 59 in the config.py file**
```
import os
from decouple import config
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

uri = os.getenv('DATABASE_URL') #or other relevant config var
if uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)

```
```
import os
from decouple import config
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

#uri = config('DATABASE_URL') #or other relevant config var
#if uri.startswith('postgres://'):
#    uri = uri.replace('postgres://', 'postgresql://', 1)

```
**3. Create the database using flask shell as follows;**
- Set the flask app

```
export FLASK_APP=api/
```
```
flask shell

db.create_all()
```
**4. Run the application to get started**
```
flask run
``` 
or 
```
python run.py
``` 

Once the application is running, you can start testing

- Signup and validate your email
> **NOTE:** You need to signup with a valid email when testing
- Login to get a JWT token.
- Add the token preceded by "Bearer" i.e `Bearer Token` to the authorization header.
- You can go ahead and test all other endpoints once you are logged in

You can visit the app [here](https://students-management-system-api.herokuapp.com/) as well to test the already hosted application with the same credentials provided above.

## ENDPOINTS

You can find the full documentation of the API on [Stoplight](https://cixors.stoplight.io/docs/cixors-url-shortener/branches/main/spqrv6qmaugyp-cixors-url-shortener)

### Auth Enpoints

HTTP METHOD|ENDPOINT|ACTION|RETURN VALUE|PARAMETER|AUTHORIZATION
---|---|---|---|---|---
POST|/auth/signup|Create a new User|User|None|None
POST|/auth/login|Generate Access Token for User|Access Token & Refresh Token|None|None
PUT|/auth/verify/{user_email}|Verify a new user|Success message|User Email|None
GET|/auth/verify/{user_email}|Resend verification code|Success message|User Email|None
PUT|/auth/resetpassword/{email}|Reset a forgotten password|Success message|User email|None
PUT|/auth/change_password|Change a user password|Success message|None|Bearer Token

___
### User Enpoints

HTTP METHOD|ENDPOINT|ACTION|RETURN VALUE|PARAMETER|AUTHORIZATION
---|---|---|---|---|---
GET|/users/|Retrieve or get all users|Users|None|None
GET|/users/{user_id}|Retrieve or get a user by user ID|User|User ID|None
GET|/users/{username}|Retrieve or get a user by username|User|Username|None
PUT|/users/{user_id}|Update or edit a user|Username and email|User ID|Bearer Token

___
### URL Enpoints

HTTP METHOD|ENDPOINT|ACTION|RETURN VALUE|PARAMETER|AUTHORIZATION
---|---|---|---|---|---
POST|/scx/|Generate a short URL|Short URL|None|Bearer Token
GET|/scx/|Retrieve or get all URLs|URLs|None|None
GET|/scx/{url_path}|Retrieve or get Long URL by short URL path|Long URL|Short URL path|None
GET|/scx/{url_id}|Retrieve or get URL by URL ID|URL|URL ID|None
PUT|/scx/{url_id}|Edit URL by ID|URL|URL ID|Bearer Token
DELETE|/scx/{url_id}|Delete URL by URL ID|Success Message|URL ID|Bearer Token
GET|/scx/user/{user_id}|Retrieve or get all URLs of a user by User ID|User URLs|User ID|None
PUT|/scx/{url_path}/qrcode|Generate a QRCode for URL by Short URL path|Success Message|Short URL path|Bearer Token
GET|/scx/{url_path}/{user_id}|Retrieve or get a specific URL by short URL path and User ID|URL|Short URL path, User ID|Bearer Token
GET|/scx/qrcode/{filename}|Retrieve or get a QRCode by Name|QRCode|QRCode name|None



___


## Languages and Tools Used
<img align="center" src="https://user-images.githubusercontent.com/53656050/192115605-aebc5f03-6e81-4537-985a-6bdd7c95f83a.png" style="width:70px; height:70px" alt="python" /> <img align="center" src="https://user-images.githubusercontent.com/53656050/192115449-02c26cf0-a2aa-4b45-a5ef-0243ac26f200.png" style="width:70px; height:70px" alt="flask" /> <img align="center" src="https://user-images.githubusercontent.com/53656050/225774036-d7db456d-49be-4b72-9dbb-97f36f005a2a.png" style="width:70px; height:70px" alt="sqlite" /><img align="center" src="https://user-images.githubusercontent.com/53656050/225773399-08e79528-2c33-4a52-962b-7bb54d0bea03.png" style="width:70px; height:70px" alt="postgresql" /><img align="center" src="https://miro.medium.com/v2/resize:fit:1200/1*oUCfmjOl7p00AVgtvy4wIg.png" style="width:110px; height:70px" alt="postgresql" />

- Python
- Flask
- SQLAlchemy
- SQLite
- Flask RestX
- PostgreSQL
- Render

## Screenshots

### *Swagger UI for API*

![image](https://github.com/kojosimtema/cixors/assets/53656050/acf1c834-c175-49fc-93a5-09d7d3107967)

### *Endpoints for Authentication*

![image](https://github.com/kojosimtema/cixors/assets/53656050/8de24544-daaa-4689-8761-b2e6bd94269a)

### *Endpoints for Users*

![image](https://github.com/kojosimtema/cixors/assets/53656050/522d7a8a-c9de-4703-94fa-27a906e0c313)

### *Endpoints for URL*

![image](https://github.com/kojosimtema/cixors/assets/53656050/048d7ec3-81a7-4e95-b839-791c493c82f3)

### *API Models*

![image](https://github.com/kojosimtema/cixors/assets/53656050/274ae19e-7976-4bc8-8e29-aa7417d2f397)


## Acknowledgements
- [AltSchool Africa](https://altschoolafrica.com/schools/engineering)

- [Caleb Emelike](https://github.com/CalebEmelike)
