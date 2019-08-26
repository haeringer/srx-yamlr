# SRX YAMLr

## Development

Install Docker: https://docs.docker.com/install/

Clone the repository:

    git clone https://gogs.intern.example.com/noc/SRX YAMLr.git && cd SRX YAMLr

Run the development environment:

    docker-compose build
    docker-compose up

When running the application container for the first time with a fresh database / new docker volume:

    docker-compose exec web bash
    python manage.py migrate
    python manage.py createsuperuser

Access the application via http://localhost:8000. The admin page can be reached at http://localhost:8000/admin.
The dev environment uses the Django development server, which automatically
reloads when changes are made to the python source code.

## Configuration

The app configuration is defined via environment variables in the container.
While the development environment uses the .env file from the repository for configuration,
the environment variables are handed over from the Jenkins credentials store in production (see Jenkinsfile), because they contain the Django secret.


## Appendix

### Updating the database after a change to the models

    python manage.py makemigrations baseapp
    python manage.py sqlmigrate baseapp 00XX
    python manage.py migrate

### Running tests

    python manage.py test

Run unit or functional tests separately:

    python manage.py test tests_units
    python manage.py test tests_functional

The functional tests are made with Selenium, which can be accessed at vnc://localhost:5900 for debugging purposes.

Use coverage.py to check backend test coverage of the project:

    cd srx-yamlrapp
    coverage run manage.py test
    coverage html
    # then visit srx-yamlrapp/htmlcov/index.html
