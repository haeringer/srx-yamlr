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
    YM_GIT_URL="https://git.intern.example.com/noc/ansible-junos"; export YM_GIT_URL
    YM_JENKINS_USER="srx-yamlr"; export YM_JENKINS_USER
    YM_JENKINS_TOKEN="11446bd6f14b99baa3c66c41e8206d5a41"; export YM_JENKINS_TOKEN
    YM_JENKINS_URL="https://jenkins.mgmt.intern.example.com"; export YM_JENKINS_URL
    YM_JENKINS_JOB="ansible-junos_test"; export YM_JENKINS_JOB
    YM_YAMLFILE="workspace/host_vars/kami-kaze.yml"; export YM_YAMLFILE
    YM_DJANGOSECRET="!7_k=@u=0fh$rxd#8e@w##eqed63fn%4ph!19+3e+se=-69x7%"; export YM_DJANGOSECRET
    YM_DEBUG='True'; export YM_DEBUG


### Run the application

Activate the virtual environment and start the development server:

    cd srx-yamlr
    pipenv shell
    python manage.py runserver

When running for the first time with a fresh database:

    python manage.py migrate
    python manage.py createsuperuser


### Update the database after a change to the models

    python manage.py makemigrations srxapp
    python manage.py sqlmigrate srxapp 00XX
    python manage.py migrate


### Run unit tests

    python manage.py test srxapp
