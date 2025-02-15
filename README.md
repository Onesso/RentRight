# RentRight
rent right business logic

### **_Procedure of Building a Docker Image and Container that Django Runs In_**


create a git repo; with gitinore and readme file only

clone the repo to your local machine

log in to dockerHub =>Account settings=>personal access token=>generate new token

back to github => project settings =>Secrets and variables=>Action=>New repository secrete;    Name: DOCKERHUB_USER Secret: {DockerHub acount username}  next add  Name: DOCKERHUB_TOKEN Secret: {secret generated from dockerhub}

inside the root of the project structure create a requirement.txt file and write the following Django>=3.2.4,<3.3  \n djangorestframework>=3.12.4,<3.13


