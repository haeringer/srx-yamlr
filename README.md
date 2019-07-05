# SRX YAMLr

## Prerequisites

Install pyenv + pipenv for dependency management.

MacOS:

    brew install python pyenv pipenv

CentOS:

    curl https://pyenv.run | bash
    sudo yum install epel-release
    sudo yum install python-pip
    sudo -H pip install -U pipenv

## Project installation

When having problems installing the appropriate Python version through pyenv, check the dependencies on https://github.com/pyenv/pyenv/wiki/common-build-problems.

    git clone https://gogs.intern.example.com/noc/SRX YAMLr.git
    cd SRX YAMLr
    pyenv install 3.7.2
    pipenv --python ~/.pyenv/versions/3.7.2/bin/python
    pipenv install

Activate the virtual environment:

    pipenv shell


### Set the environment variables for the application

    vi ~/.bash_profile || ~/.bashrc

    # SRX YAMLr Environment variables
    YM_ANSIBLEREPO="https://git.intern.example.com/noc/ansible-junos"; export YM_ANSIBLEREPO
    YM_YAMLFILE="host_vars/kami-kaze.yml"; export YM_YAMLFILE
    YM_DJANGOSECRET="!7_k=@u=0fh$rxd#8e@w##eqed63fn%4ph!19+3e+se=-69x7%"; export YM_DJANGOSECRET
    YM_DEBUG='True'; export YM_DEBUG


### When running the application for the first time with a fresh database:

    python manage.py migrate
    python manage.py createsuperuser


## Appendix

### Running the application in a development environment

Activate the virtual environment and start the development server:

    cd srx-yamlr
    pipenv shell
    python manage.py runserver 0.0.0.0:8000

Access the application via http://localhost:8000. The admin page can be reached at http://localhost:8000/admin.


### Updating the database after a change to the models

    python manage.py makemigrations srxapp
    python manage.py sqlmigrate srxapp 00XX
    python manage.py migrate

### Run unit tests

    python manage.py test srxapp
