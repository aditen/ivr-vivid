# FS21: IVR ViViD group

This is our project for the FS21 seminar Interactive Video Retrieval. It contains of a React/Next.JS frontend and a Python/Flask backend

## Backend
The backend is located in the... supripse! **backend** subfolder. 
To use it, you need Python 3.8+ (I use 3.8.2, later ones should work as well).
Easiest way to set it up is by using a virtual environment. Example commands (from the backend folder):
``
python -m venv venv
pip install -r requirements.txt
python run_web_server.py
``
If you want to **add libraries** you can do so by adding them to the *requirements.txt* file. 
You can either just add the package name, which just downloads the latest version at that point or select a specific version with the syntax package==version

## User Interface
The user interface is located in the *gui* subfolder.
It requires a [Node.JS/npm](https://nodejs.org) installation with LTS (so choose version 14 LTS). 
I am personally still on version 10.14, but this should work with higher versions as well.
Setting it up just requires installing dependencies and then running the dev server, so run the following commands in the gui directory:
``
npm install
npm run dev
``
If you want to **add libraries** you can do so by doing an *npm i library* command, which adds the version to the package.json as well as package-lock.json files.
**Note: Please do not commit changes to the package.json file at the moment!**

## REST calls
For data loading, the user interface calls the backend via REST calls. The methods used are GET and POST. 
GET is used in the context of getting suggestions (for a given text query) 
whilst POST is used for executing queries (submitting a filter like dropdown selection, canvas, text in image, combination etc.)
At some later point we can also add a Swagger UI for that!

