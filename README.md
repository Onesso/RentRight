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

inside the app directory create .flake8 file and inside it list the exclusions.
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

