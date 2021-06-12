[![swagger-editor](https://img.shields.io/badge/open--API-in--editor-brightgreen.svg?style=flat&label=client%20open-api-v3)](https://editor.swagger.io/?url=https://raw.githubusercontent.com/aditen/ivr-vivid/main/openapi-spec-swagger.yaml)
# FS21: IVR ViViD group

This is our project for the FS21 seminar Interactive Video Retrieval. It contains of a React/Next.JS frontend and a Python/Flask backend

## Backend
The backend is located in the... supripse! **backend** subfolder. 
To use it, you need Python 3.8+ (I use 3.8.2, later ones should work as well).
Easiest way to set it up is by using a virtual environment. Example commands (from the backend folder):
```
python -m venv venv
pip install -r requirements.txt
python run_web_server.py
```
If you want to **add libraries** you can do so by adding them to the *requirements.txt* file. 
You can either just add the package name, which just downloads the latest version at that point or select a specific version with the syntax package==version

## User Interface
The user interface is located in the *gui* subfolder.
It requires a [Node.JS/npm](https://nodejs.org) installation with LTS (so choose version 14 LTS). 
I am personally still on version 10.14, but this should work with higher versions as well.
Setting it up just requires installing dependencies and then running the dev server, so run the following commands in the gui directory:
```
npm install
npm run dev
```
If you want to **add libraries** you can do so by doing an *npm i library* command, which adds the version to the package.json as well as package-lock.json files.
**Note: Please do not commit changes to the package.json file at the moment!**

## Static fileserver for Keyframes
As they load way faster from your localhost (being read from the disk) you should set up a static server on your machine. Do this , use the [npm static-server package](https://www.npmjs.com/package/static-server). The steps to use it are simple. As you have already installed NodeJS for the GUI on your machine, just run the following two commands (**second one has to be run inside your keyframe directory**)

```
npm -g install static-server
static-server
```

## Setting up the database locally
You need a **MariaDB** server locally. Simplest way to do this is with docker. Simply run below command, overriding the passwords (pass1234 respectively root 1234) with whatever you want and your mariadb will be running on port 3306, available for other processes (and running in the background due to the -d flag):
```
docker run -p 3306:3306  --name ivr-mariadb --restart always -e MYSQL_ROOT_PASSWORD=root1234 -e MYSQL_DATABASE=ivr -e MYSQL_USER=ivr -e MYSQL_PASSWORD=pass1234 -d mariadb --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
```
Subsequently, just load the sql dump (ivr.sql in the shared directory) into your database, it will automatically build indices to speed up the queries 😎

Then set the following environment variables to your backend runtime (again, adjust the password if you change it. I recommend **NOT** to use the root user for the connection!
```
db_host=localhost;db_pw=pass1234;db_user=ivr;db_name=ivr
```

## REST calls
For data loading, the user interface calls the backend via REST calls. The methods used are GET and POST. 
GET is used in the context of getting suggestions (for a given text query) 
whilst POST is used for executing queries (submitting a filter like dropdown selection, canvas, text in image, combination etc.)
At some later point we can also add a Swagger UI for that!

