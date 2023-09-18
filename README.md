wireone django boilerplate
overview

django boiletplate to jumpstart building django apps

    python - 3.10

    django - 4.0

    postgres - 13.4

Setting up dev environment
Setting up python

    install pyenv

git clone https://github.com/pyenv/pyenv.git ~/.
cd ~/.pyenv && src/configure && make -C src

then put this in your ~/.bashrc:

# the sed invocation inserts the lines at the start of the file

# after any initial comment lines

sed -Ei -e '/^([^#]|$)/ {a \
export PYENV_ROOT="$HOME/.pyenv"
a \
export PATH="$PYENV_ROOT/bin:$PATH"
a \
' -e ':a' -e '$!{n;ba};}' ~/.profile
echo 'eval "$(pyenv init --path)"' >>~/.profile

echo 'eval "$(pyenv init -)"' >> ~/.bashrc

    install python version

pyenv install 3.10

setting up postgres

    instructons on installing

sudo apt install postgresql

    starting postgres

sudo systemctl enable --now postgresql.service

    create db, db user, password

        switch to postgres user

        sudo su postgres

        open psql

        psql

        create database, database user and grant privileges to user

        CREATE DATABASE project;
        CREATE USER projectuser WITH PASSWORD 'password';
        ALTER ROLE projectuser SET client_encoding TO 'utf8';
        ALTER ROLE projectuser SET default_transaction_isolation TO 'read committed';
        ALTER ROLE projectuser SET timezone TO 'UTC';
        GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;

        change project and projectuser to appropriate names.

    export to env

setting up django

    install virualenv

    pip install virtualenv

    create a virtual evironment

    virtualenv --python=python3 .venv

    activate virtualenv

    source .venv/bin/activate

    install requirements

    pip install -r requirements/dev-requirements.txt

    copy env.sample to .env

    cp env.sample .env

    and edit `.env in your favourite editor and fill in the required details including the database credentials in previous step

    creating log folder and give it appropriate permissions

    sude mkdir /var/log/django
    sudo chmod 777 /var/log/django

    make migrations for the django project

    python manage.py migrate

    run the development server

    python manage.py runserver

deployment instructions

    install supervisor

    sudo apt-get install supervisor

    start supervisor service

    sudo systemctl enable --now supervisor

    make a supervisor config file for gunicorn
    create a configuration file for the project in /etc/supervisor/conf.d/ with appropriate name
    e.g. /etc/supervisor/conf.d/project.conf. put this inside it

    [program:project]
    command=/path/to/project/.venv/bin/gunicorn --bind unix:/tmp/ipc.sock project.wsgi
    directory=/path/to/project/
    autostart=true
    autorestart=true
    stderr_logfile=/var/log/myproject.err.log
    stdout_logfile=/var/log/myproject.out.log

    this creates a sock file in /tmp named ipc.sock which we need to forward to from nginx.

    start the project from the config file

    sudo supervisorctl start project

    install nginx

    sudo apt install nginx

    create a entry point in /etc/nginx/sites-available/ for our project. e.g. project. the file location should be /etc/nginx/sites-available/project and put this inside it

    server {
        listen 80;

        location / {
            proxy_pass http://unix:/tmp/ipc.sock;
        }
    }

    remove all enabled existing sites and enable the django app

    sudo rm -rf /etc/sites-enabled/*
    sudo ln -s /etc/nginx/sites-available/project /etc/nginx/sites-enabled/project

    start nginx

    sudo systemctl enable --now nginx

this project directory includes:

main - Main project directory
envs - Environments
requirements - Requirements dev/prod
pyproject.toml - Project metadata
pytest.init - Test Configuration File
.pre-commit-config.yaml - Pre commit config file
.gitignore - gitignore
creating env from sample

Open env.sample and replace value with the intended values.
envs

contains environment variables for different use cases

# create virtual environment

python -m venv .env
source .enn/bin/activate

# install requirements

pip install -r requirements/dev-requirements.txt

# or for production

pip install -r requirements/requirements.txt

# load environment variables

source envs/local.env

# or a test environment

source envs/test.env

main directory

contains source code for the project

    main/app1: layout of an app inside the project

    main/libs: folder for helper functions and boilerplate templates/classes

    main/main: project root configuration folder

requirements

contains project requirements

    dev-requirements.txt: requirements for development environment

    requirements.txt: requirements for production environment

.pre-commit-config.yaml

This file stores the configuration for pre-commit

# See https://pre-commit.com for more information

# See https://pre-commit.com/hooks.html for more hooks

repos:

- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v3.2.0
  hooks:
  - id: trailing-whitespace
  - id: end-of-file-fixer
  - id: check-yaml
  - id: check-added-large-files
- repo: https://github.com/psf/black
  rev: 21.12b0
  hooks:
  - id: black

.black

This file is the configuration file for black formatter.
pytest.ini

test configuration file
pyproject.toml

python project settings file

# CHANGELOGS
