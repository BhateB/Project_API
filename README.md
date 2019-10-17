
This Application serves as an example of a generic reusable Django application. The actual code of the app implements many functionalities related to management with tests, the main project and documentation.

It runs under officially Django supported versions:

Django 2.2 
Python 2.7 and Python 3 (3.2, 3.4, 3.5, 3.6)

This tutorial passes through all the steps to successfully run the application, while the rest of the documentation addresses the functionalities of the project.


## Setting up project dependencies on local machine

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

 1. git clone https://github.com/BhateB/Project_API.git

 2. pip3 install -r requirements.txt

 3. python3 manage.py migrate

 4. python3 manage.py makemigrations

 5. python3 manage.py migrate

 6. python3 manage.py runserver

 7. Login to http://127.0.0.1:8000

 8. python3 manage.py createsuperuser (enter username, email, password)


#### Key Features
- 1 . Register
- 2 . Login
- 3 . File Upload
- 4 . Form Validation
- 5 . CRUD Application
- 6 . File Upload
- 7 . CSV Import
- 8 . CSV Export


## Built With

* [Django](https://docs.djangoproject.com/en/2.2/) - Python based web framework.
* [Django Rest framework](https://www.django-rest-framework.org/) - Toolkit for building web API's
