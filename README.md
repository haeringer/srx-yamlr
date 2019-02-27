# SRX YAMLr

## Requirements (Development on MacOS)

### Set up Python environment

Install pipenv (and pyenv) for dependency management and use it to install the packages that are defined in the Pipfile. With pyenv available, the appropriate Python version itself will be installed as well.

    brew install pyenv pipenv
    cd srx-yamlr
    pipenv install

Activate the virtual environment:

    pipenv shell


### Set the environment variables for the application

    vi ~/.bash_profile

    # SRX YAMLr Environment variables
    YAMLOMAT_GIT_URL="https://git.intern.example.com/noc/ansible-junos"; export YAMLOMAT_GIT_URL
    YAMLOMAT_YAMLFILE="workspace/host_vars/kami-kaze.yml"; export YAMLOMAT_YAMLFILE
    YAMLOMAT_DJANGOSECRET="!7_k=@u=0fh$rxd#8e@w##eqed63fn%4ph!19+3e+se=-69x7%"; export YAMLOMAT_DJANGOSECRET
    YAMLOMAT_DB_NAME="srx-yamlr_db"; export YAMLOMAT_DB_NAME
    YAMLOMAT_DB_USER="srx-yamlr"; export YAMLOMAT_DB_USER
    YAMLOMAT_DB_PASSWORD="rjBvtl2VinRA6QZKNPA46ZQwuR2jmz"; export YAMLOMAT_DB_PASSWORD
    YAMLOMAT_DEBUG='True'; export YAMLOMAT_DEBUG


### Set up PostgreSQL as database

    brew install postgresql
    pg_ctl -D /usr/local/var/postgres start
    createdb srx-yamlr_db
    psql postgres
    CREATE ROLE srx-yamlr WITH LOGIN PASSWORD 'rjBvtl2VinRA6QZKNPA46ZQwuR2jmz';
    GRANT ALL PRIVILEGES ON DATABASE srx-yamlr_db TO srx-yamlr;
    ALTER USER srx-yamlr CREATEDB;


### Run the application

Activate the virtual environment and start the development server:

    cd srx-yamlr
    pipenv shell
    pg_ctl -D /usr/local/var/postgres start
    python manage.py runserver

When running for the first time with a fresh database:

    python manage.py migrate
    python manage.py createsuperuser


### Update the database after a change to the models

    python manage.py makemigrations srxapp
    python manage.py sqlmigrate srxapp 00XX
    python manage.py migrate


### Run unit tests

Test with production database:

    python manage.py test srxapp

Test with in-memory sqlite database (faster):

    python manage.py test --settings=test_settings srxapp