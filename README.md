## Requirements (Development on MacOS)

### Set up Python Virtual Environment

Install pyenv, virtualenv + desired python version and create the virtualenv:

    brew update
    brew install pyenv
    brew install pyenv-virtualenv
    pyenv install 3.7.0
    pyenv virtualenv 3.7.0 django

Configure working directory to automatically use the desired python version when switching into the directory:

    vi ~/.bash_profile
        eval "$(pyenv init -)"
        eval "$(pyenv virtualenv-init -)"
    mkdir django
    cd django
    pyenv local 3.7.0

Install pip packages

    cd cfgen/
    pip install -r requirements.txt


### Set up PostgreSQL as database

    brew install postgresql
    pg_ctl -D /usr/local/var/postgres start
    createdb cfgen_db
    psql postgres
    CREATE ROLE cfgen WITH LOGIN PASSWORD 'rjBvtl2VinRA6QZKNPA46ZQwuR2jmz';
    GRANT ALL PRIVILEGES ON DATABASE cfgen_db TO cfgen;
    ALTER USER cfgen CREATEDB;


### Run the application

Activate the virtual environment and start the development server:

    cd django/cfgen/
    pyenv activate django
    pg_ctl -D /usr/local/var/postgres start
    python manage.py runserver

When running for the first time with a fresh database:

    python manage.py migrate
    python manage.py createsuperuser


### Update the database after a change to the models

    python manage.py makemigrations cgapp
    python manage.py sqlmigrate cgapp 00XX
    python manage.py migrate
