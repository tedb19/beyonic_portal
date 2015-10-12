#Beyonic Portal

This project has been built and tested on python 3.4

1. Install, create and activate a virtualenv (see https://virtualenv.pypa.io/en/latest/installation.html for details)

2. Once in the virtualenv, install the dependencies defined in the requirements.txt file as follows:

          pip install -r requirements.txt

3. Set the following environment variables on activate.bat (windows) or bin/activate script (linux) file on your virtualenv

    VARIABLE                 | ROLE                                                     | PROPOSED VALUES 
    -------------------------|----------------------------------------------------------|----------------
    TWILIO_ACCOUNT_SID       |The twilio account SID provided on twilio account         |
    TWILIO_AUTH_TOKEN        |The twilio authentication token provided on twilio account|
    TWILIO_DEFAULT_CALLERID  |The twilio default caller ID value                        |
    CALLER_ID                |The twilio phone number to be used for sending the sms    |
    EMAIL_HOST_USER          |The email address used for sending mails                  |
    EMAIL_HOST_PASSWORD      |The password for the email address                        |
    SECRET_KEY               |The secret key of the django project                      |
    ROOT_URL                 |The root url of the application.Used in the activation link|http://127.0.0.1:8000
    
4. Restart the virtual environment so that the environment variables can be applied.

5. Run the following to apply the database migrations included in the app

	           python manage.py migrate

6. Run the following to copy all the static files into the STATIC_ROOT folder

	           python manage.py collectstatic
	
7. The following runs the application using local settings (which is the default settings file)

	           python manage.py runserver

8. The following runs the project’s unit and functional tests

	           python manage.py test --settings=beyonic_portal.settings.test

9. To use the production settings, use the following

	           python manage.py runserver --settings=beyonic_portal.settings.production
