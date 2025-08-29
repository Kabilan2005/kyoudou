This file helps you step by step to run the application smoothly.

Download python latest version.
Create a virtual environment in order to isolate the application development without conflicting with others and global config.

CLI : python -m venv <name>
Activate it using : <name>\Scripts\activate

Then install django using pip : pip install django
Create a directory to hold your project
  mkdir <dir>
  cd <dir>
  
The following is optional if you cloned the entire repo but it is highly recommended to learn what are the files and what they are meant to do
To generate automated code for django settings, configurations, URL dispatcher
For that in the curr dir:
  django-admin startproject <name> <dir>(use . if present dir)
Then create application:
  python manage.py startapp <app_name>
Copy the contents (if doing manually)
After run the server using:
  python manage.py runserver
