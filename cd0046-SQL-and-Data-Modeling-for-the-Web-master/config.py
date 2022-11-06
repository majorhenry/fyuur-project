import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
ENV = 'DEV'
if ENV == 'DEV':
    SQLALCHEMY_DATABASE_URI = 'postgdataql://postgdata@localhost:5432/fyurr'
else:
    SQLALCHEMY_DATABASE_URI = '<Put your local database url>'

