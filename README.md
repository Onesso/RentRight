# RentRight
rent right business logic

### **_Procedure of Building a Docker Image and Container that Django Runs In_**


1. create a git repo; with gitinore and readme file only

2. clone the repo to your local machine

3. log in to dockerHub =>Account settings=>personal access token=>generate new token

4. back to github => project settings =>Secrets and variables=>Action=>New repository secrete;    Name:             DOCKERHUB_USER Secret: {DockerHub acount username}  next add  Name: DOCKERHUB_TOKEN Secret: {secret generated from dockerhub}

5. inside the root of the project structure create a requirement.txt file and write the following Django>=3.2.4,<3.3  \n djangorestframework>=3.12.4,<3.13

6. On the root create Dockerfile(contains a set of instructions to automate the creation of a Docker image)

7. On the root create .dockerignore file and add details

8. on the root create docker-compose.yml (is used to define and manage multi-container Docker applications.It automate container creation. it ensure that services starts in the correct order)

9. Linting and Tests (Linting is the process of analyzing code for potential errors, style violations, and best practices) install flake8 package and runned through docker compose; to solve linting errors we work from bottom to top for testing we use Django test suite (it is Django's built-in framework for writing and running automated tests on models, views, forms and APIs)

on the root create requirements.dev.txt file; the reason to create a new requirements file is so as to add dependencies that is only used for development.

And Modified docker-compose.yml , Dockerfile then build {docker-compose build} then we are going to tell flake8 to exclude othe files since by default django will have many linting errors

inside the app directory create .dockerignore file and inside it list the exclusions.
on the terminal run: docker-compose run --rm app sh -c "flake8"

10. Create the django project by runining: docker-compose run --rm app sh -c "django-admin startproject app ."
the dot is to make sure it run in the current directory


### ** Configure Github Actions
github action is an automated tool that allows us to run jobs when code changes and automate task. it is activate by a trigger example push to github. the problem is that there is pricing.
Dockerhub allows 100/6h for anonymous users

    Trigger      =>        Job       =>     Result
(Push to GitHub)    (Run unit tests)    (Success/fail)

                prerequisites
        create an account with hub.docker.com
        Use docker login during job


1. Create a config file at .github/workflows/checks.yml

in the checks.yml write the jobs (test-lint) that is going to be performed when triggered.

    Login to Docker Hub: Uses the docker/login-action@v1 action to log in to Docker Hub using the credentials stored in the repository secrets (DOCKERHUB_USER and DOCKERHUB_TOKEN).

    Checkout: Uses the actions/checkout@v2 action to check out the repository's code.

    Test: Runs the command docker compose run --rm app sh -c "python manage.py test" to execute the tests inside the Docker container.

    Lint: Runs the command docker compose run --rm app sh -c "flake8" to perform linting checks inside the Docker container.

    note: on ubuntu-20.04 that we are running the job, it comes with docker and docker-compose pre-installed.

### ** Test Driven Development (TDD)
django comes with Django test framework which built on top of unittest module from python. and TestCase classes out of the box, when you create an app in django it comes with a file test.py nevertheless you can create a directory for testing and in it __init__.py is a must. The directory and test.py can not exist in the same application. For the directory we can have different test but must be name in the following convection test_module_one.py

Test Database; it test code that uses the DB, It creates a flash DB that is used to run test, clear data and again run test.


Test classes

    a. SimpleTestCase - usefull when no database is required for the   test

    b. TestCase - usually when code requires to read the database

outline of Writing tests

    a. import test class (either SimpleTestCase or TestCase).
    b. import the object you want to test (code you are testing).
    c. define the test class and as a parameter (include either SimpleTestCase or TestCase).
    d. add test method/function.
    e. Setup inputs.
    f. Exercute code to be tested.
    g. Check output.

SimpleTestCase example
        create calc.py inside app/app dir, write an addition function inside, this is the function we'll be testing
        create test.py inside app/app dir, wite the write the test that will test the calc.py function.


Unittest.mock => is a situation where you a different code or function than the intended one to prevent wastage of resources
        (MagicMock/Mock) = Replaces real objects
        patch - Overrides code for test

APIClient based on the django TestClient -> we can make requests, check result and even override authentification

Overview of using the APIClient
        1. import APIClient
        2. Create TestClient
        3. Make request
        4. Check result

Problems associated with testting
        indetation of different test methods
        every test method must start with a prefix "test"
        when grouping test in a directory an __init.py__ is compulsary
        ImportError - this occurs when there is both test directory and test.py


### ** Database configuration

                        architecture:

                          DOCKER COMPOSE
    Database(PostgreSQL) <|             |> APP(Django)

Docker compose will set the network connectivity between the application and database
Volumes - this is how we store persistent data using docker compose. It maps a directory in container to our local machine

1. open docker-compose.yml and add the database service take two services i.e. app(django) and db(PostgreSQL)
    the enviroment variables used in the app and db is for establish a connection to the database.

        steps on how django connects to the database
            1. Configure Django - tell django how to connect
            2. install database adaptor dependencies - tools django uses to connect
            3. Update python requirements (includes the postgres adaptor)

            NOTE: Before the connection django need to know
                    1.engine
                    2.Hostname
                    3.Port number
                    4.Databse name
                    5.username
                    6.password
                All this are defined in the settings.py file

            Environment variables

                why use environment variables?
                    1. pull configuration values
                    2. Easily passed to Docker
                    3. Used in local dev or production
                    4. Single place to configure project
                    5. Easy to do with Python

    Psycopg2 (PostgreSQL adaptor for python)
        installation option
            1. psycopg2-binary (OK for local development not good for production)
            2. Psycopg2 (Compiles from source (linux, windows), require addition dependencies, easy to install in docker)

        for this project we'll be using Psycopg2 and the followwing are the list of package dependencies
            1. C compiler
            2. python3-dev
            4. libpq-dev

            NOTE for Alpine our operating system we'll be using
                1. postgres-client
                2. build-base
                3. postgresql-dev
                4. musl-dev
                NOTE: the last three pacges are only used for installation not running, therefore we'll remove later
2. Open the Dockerfile - on RUN we'll install postgresql-client line:18 and in --virtual .tmp-build-deps install the other three; line:19 and 20
    on line:22 we install the postgres-client which is listed in the requirement
3. after finishing step 2 you should run docker-compose down then docker-compose build to install all the requirements.

4. open settings.py to configure the database import os, remove db.sqllite file and update the DATABASES section

# Solving race condition
because we are using the "depends_on" in the app service of the container, the "depends_on" only ensures that db service is on, but not the actual postgres is running.
the db service will first start and when it finishes the app service will then start due to the "depends_on", while the app service is starting on the other side postgres will then start but it takes
long i.e. the qpp service will finish starting then django start and finishes before postgres is ready, django will then crash since the database was not ready.

The solution is for django to "wait for db" a fucntion that will continually the availabity and readiness of the Databse to do this we are going to create a custom Django management command

a. create a new app called core where we are going where we we'll write the wait_for_db command
b. on the core app remove the test.py replace it with a test directory and also veiws.py from the core

# write tests wait_for_db function
Note: customer management functions/command, this are function/command that provide a built-in managemnt command like migrate, runserver and createsuperuser, they are exercuted using python manage.py <command>, since it is a management command

a. inside core, create management/command/wait_for_db.py in each directory an __init__.py file is included.
b. Due to test driven develoment, write a test inside the test directory,namely: test_commands.py for wait_for_db command, two command are ritten to test whether the database is ready or there is a delay; the test command will be testing then waiting for a few second then test again, we are not going to wait in our unit test because that will slow our test
c. write the function that checks the connection for database in wait_for_db.py file

### Migrations
in django you do not need to write the actual querries.
Django comes with (Django ORM) Object Relation Mapper; this is an abstration layer that handles database structure and changes therefore in django you can use any database and the ORM we'll handle the rest.

            using the ORM

                Define models => Generate migration files => Setup databse => Store data

                NOTE: you only need to define the models and the reset is handle by django ORM

Each model is mapped to a table, Models containe: Name, Fields, Other metadata, Custom Python Logic.
Once you have created the models you do the migrations

            Creating migrations

            a. Ensure app is enabled in settings.py
            b. Use Django CLI
                python manage.py makemigrations

            Applying migrations

            a. Use Django CLI
                python manage.py migrate
NOTE: due to automation all the migration command will be written inside the docker-compose inside command

Open docker-compose.yml app -> command -> write the migration commands together with the wait_for_db

# CREATING USER MODEL
what is a model? In django a Model defines how data is stores.Model is the part that interacts with the database.
Each model coresponds to a table in the database. And each attribute in the model would correspond to a field in that table.

Django user model - is a built-in model in django's authentication system that handles user accounts, including authentication, permission and user management.
the default user model is not easy to customize therefore it is important to create a custom model for new projects

How to create a customise user model
    a. Create model
        Base from AbstractBaseUser and PermissionsMixin
    b. Create a custom manager
        Used for CLI integration
    c. Set AUTH_USER_MODEL in setting.py => this is to tell django that you'll be using the custome user model
    d. Create and run Migrations

    NOTE: AbstractBaseUser - provides features for authentication but does not include fields therefore you'll have to create you own.
          PermissionsMixin - it is used for django permission system for different user. It provides all the fields and methods required

                    Common issues
                    Running migrations before setting custom model. therefore since we already ran migrations we'll have to clear them
                    it is recommend to set up the custom model first before running the migration
                    Typos in config - it does not throw errors in config
                    indetation

        User model manager
            - used to manage objects from our user Model
            - custom logic for creaating objects (Hashing password)
            - used by Django CLI to create superuser.

        BaseUserManager (Comes default by django)
            - it is the base class for managing users
            - contains useful helper method; normalize_email (for storing emails consistently)

            we'll also define our methods
                - create_user (called when creating a user)
                - create_superuser (used by the CLI to create a superuser(admin))

Before creating our user model we'll create a unit test
1. navigate to core/tests/ and create file test_model.py the test class of creating a user is written.
2. navigate to core/models.py create the model User for adding user to the system. And also create a user
3. navigate to app/app/settings.py define the custom User Model and set the Auth_User_Model configuration

NOTE: after settings.py run docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate" which will throw error: InconsistentMigrationHistory.  this is because you had already made a migration before
      To solve this we'll delete the current volume first make sure the containers are not running and run the following command docker volume rentright_dev-db-data then run docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate"
      which we'll work this time.

      migrations are created automatic

4. Validation to ensure that users are created with email address. on test_models create create a method that will raise an error if a user is to be created without an email

        Summary: in this section: created a custom user model
                                  Configured django to use the custom user model that we created
                                  Handle normalising email
                                  Handle encrypting passwords


# SETUP DJNAGO ADMIN
 - django admin is a graphical user interface for models it supports create, read, update, delete
 - the following are operations that we can do to modify the admin interface

 How to enabled Django admin?
    a. enable per model
    b. inside admin.py
        - admin.site.register(property)

 Customising
    a. Create class based off ModelAdmin or UserAdmin
    b. Override/set class variables

 Changing list of objects
    a. ordering: changes order items appear
    b. list_display: fields to appear in list

 Add/update pages
    a. fieldsets: control layout of page
    b. readonly_fields: fields that can not be changed example last log in time

 Add page
    a. add_fieldsets: fields displayed only on add page



1. create app/core/test/test_admin.py => this will be the unittest from the admin section this is where there is list fo test for the admin section; like test to create an admin user who in return can generate a link that will return a list of all common user
                                      => write another test that will ensure that the admin edit user page works.
                                      => test create user page
2. navigate app/core/admin.py => here the code is written to customize the admin inteface; where by it will present users email and name order is by their id
                              => further write a code that will render the edit page once the email address is clicked

                              NOTE: the two functionality above was to list all user and e able to open a specific user and see details
                              => adding a support for creating new users


                              NOTE: in short the admin.py define how the admin should look and the functionalities that is should support


# API DOCUMENTATION
What is API documentaion? is a detail guide that explain how to use and intergrate an API.

Why do the documentaion? a. APIs are designed for developers to use.
                         b. Developer need to know how to use it.
                         c. An API in only as good as its documentation

What to document?   a. Everything needed to use the API
                    b. Available endpoints (path) e.g. /api/property
                    c. Supported methods e.g. GET, POST, production
                    d. Format of payloads (Inputs), (parameters), (Post JSON format)
                    e. Format of responses (outputs)
                    d. authentification process

    <u> Automated documentation with djangorestframework </u>
        => we'll be using a third party library known as drf-spectacular. this library generates a schema (Document in format of JSON or YAML) the schema then allows us to create a browsable web interface, this interface furthers allows us make test request and hnadle authentication

        => OpenAPI Schema; is a Standard for describing APIs, it is popular in the industry, Supported by most API documentation tools in our case swagger, it uses popular data format like YAML and JSON

        NOTE: drf-spectacular it generates a schema -> swagger genearates the GUI

        1.  Install drf-spectacular.
                => navigate to requirements.txt and add drf-spectacular>=0.15.1,<0.16

        2. run docker-compose build  -> this is to instll drf-spectacular to the container

        3. navigate to app/settings.py to configure drf-spectacular

        4. Configure URLs; navigate to app/app/urls.py  here we'll add the code to generate the schema

        5. Test Swagger documentation on the browser surf 127.0.0.1/api/docs/  => here we'll be able to visualize the GUI made by Swagger from the schema made by openAPI Schema

# Building user API
Design of users API:
                        User registration
                        Creating auth token
                        Viewing/updating profile

Endpoints:
                        a. user/create/     => POST - for registering new user
                        b. user/token/      => POST - for creating a new token
                        c. user/me/         => PUT/PATCH - for updating the profile
                                            => GET - View profile

1. Run docker-compose run --rm app sh -c "python manage.py startapp user => this is to create a new django app.
2. Do some cleaning remove: migrations, admin, models and test.
3. After removing the test file create a new category for test and add __init__.py
4. Add the user app to settings.py installed apps
----------------------------------------------------------------------------------------------------------------
5. Create test for our create user endpoint.
                NOTE: Public test - Unauthenticated requests example registering a user.

6. Implimenting the API to make the test passed(Implimenting create user API)
                How do we impliment out create user API?
                    a.  Add a serializer; a component that converts complex data types (like Django models) into JSON and vice versa.
                        => create new file; app/user/serializers.py and write the serializer here

                    b.  navigate to app/app/user/views.py  write the views for the user API  N/B: to connect the views to the us=rl we'll modify two files.
                    c.  Create app/app/user/urls.py here we'll define the URL routing for the user API, it mapps specific URL to corresponging views
                    d.  navigate to app/app/urls.py 


                    NOTE: When we make a http request, it through the url.py, passed in to views.py the CreateUserView class, which interns calls the serializer that creates the object