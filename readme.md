# Django Blog service

## Source 
* Packt Django (Chapter 1 ~ 4)

## setup

### Virtual Env
* ``source venv/Scripts/activate``
* ``deactivate``

### Setup Python Dependencies
* ``pip install -r requirements.txt``

### [Enviroment](.env)
* For Django Project settings
    * `DJANGO_SECRET_KEY`
* For connecting DB
    * `DB_PASSWORD`
* For Email recommendation service
    * `EMAIL_HOST`
    * `EMAIL_HOST_USER`
    * `EMAIL_HOST_PASSWORD`

### Postgresql DB
* via Docker Container: set DB port to `5432:5432`
* Postgresql User & Database name: `blog`