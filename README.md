# SRX YAMLr

## Requirements

### Setting up the Python environment

Install pipenv + pyenv for dependency management and use it to install the packages that are defined in the Pipfile. With pyenv available, the appropriate Python version itself will be installed as well.

    brew||apt||yum install pyenv pipenv
    git clone https://gogs.intern.example.com/noc/SRX YAMLr.git
    cd srx-yamlr
    pipenv install

Activate the virtual environment:

    pipenv shell


### Setting the environment variables for the application

    vi ~/.bash_profile || ~/.bashrc

    # SRX YAMLr Environment variables
    YM_GIT_URL="https://git.intern.example.com/noc/ansible-junos"; export YM_GIT_URL
    YM_YAMLFILE="workspace/host_vars/kami-kaze.yml"; export YM_YAMLFILE
    YM_DJANGOSECRET="!7_k=@u=0fh$rxd#8e@w##eqed63fn%4ph!19+3e+se=-69x7%"; export YM_DJANGOSECRET
    YM_DEBUG='True'; export YM_DEBUG


### Runnig the application

Activate the virtual environment and start the development server:

    cd srx-yamlr
    pipenv shell
    python manage.py runserver

When running for the first time with a fresh database:

    python manage.py migrate
    python manage.py createsuperuser


### Updating the database after a change to the models

    python manage.py makemigrations srxapp
    python manage.py sqlmigrate srxapp 00XX
    python manage.py migrate


### Running unit tests

    python manage.py test srxapp
