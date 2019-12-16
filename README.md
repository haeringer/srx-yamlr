# SRX YAMLr

When trying to maintain a Juniper SRX firewall configuration with Ansible, one probably will realize that it's a PITA to manage firewall policies in a YAML file due to the object-based configuration of the SRX.

The SRX YAMLr digests all the policy objects (zones, addresses, address sets, applications and application sets) from a host_var file within an Ansible Git repository. It then provides a Web interface to search for object names or values, create new objects and policies and commit & push them back into the git repository.

The SRX host_var file needs to be in a specific format in order to be processed by the SRX YAMLr. An example file is provided here: https://github.com/haeringer/ansible-juniper/blob/master/host_vars/firewall1.yml

To be able read from private repositories and commit, you need to create a personal access token in your Git account and save it in the SRX YAMLr user settings. Currently, only Gogs is supported as Git server type.


## Configuration

The app configuration is defined via environment variables in the container.
While the development environment uses the .env file from the repository for configuration, the environment variables need to be handed over to the container when running in production.


## Development

#### Prerequisites

- Install Docker and docker-compose
- Clone the repository and change into directory

Run the development environment:

    docker-compose up

When running the application container for the first time with a fresh database / new docker volume:

    docker-compose exec web bash
    python manage.py migrate
    python manage.py createsuperuser

Access the application via http://localhost:8000. The admin page can be reached at http://localhost:8000/admin.
The dev environment uses the Django development server, which automatically
reloads when changes are made to the python source code.


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

The functional tests are made with Selenium, which can be accessed at vnc://localhost:5900 (password "secret") for debugging purposes.

Use coverage.py to check backend test coverage of the project:

    cd django
    coverage run manage.py test
    coverage html
    # then visit django/htmlcov/index.html
