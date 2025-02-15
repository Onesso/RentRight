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


