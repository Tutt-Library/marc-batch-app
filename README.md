[GUNICORN]: http://gunicorn.org/

# MARC Batch Application

## Run in background
This application runs in the background using [gunicorn][GUNICORN].

Use the following command after activating a Python virtual environment with 
[gunicorn][GUNICORN] installed:

    `nohup gunicorn -b 0.0.0.0:8000 app:app &`  

