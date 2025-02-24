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


