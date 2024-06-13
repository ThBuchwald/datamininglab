# Data Mining Lab

This Django-based project is a precursor to the Data Mining Lab Freiberg which will collect data from different research institutes situated in beautiful Freiberg, Saxony to form datasets that will offer new insights into areas of recycling and increased use of secondary raw materials. As such it is a vital step forward in the research of circular economy, cradle-to-cradle design and zero waste.

## Setup

When you first clone the project into a new folder, you have to follow a few steps to get the Data Mining Lab Server to run:

### Create a virtual environment

The ``pyproject.toml`` file contains all the necessary information to set up a virtual environment with Poetry. If you don't like to use poetry, create an environment with the tool you are comfortable with; just make sure to install the specified packages in the ``.toml`` file along with their dependencies.

If you choose the Poetry route:

* Make sure that you have Python (3.11) installed and Poetry set up (https://python-poetry.org/docs/#installing-with-the-official-installer).
* Next, make sure you have set the in-project flag: ``poetry config virtualenvs.in-project true``
* Install the environment with ``poetry install``

### Create .env

You need a ``.env`` file in your root directory with quite a few variables in order for the whole project to work. Django's ``settings.py`` will look up the ``.env`` file to get all required variables and work out of the box.

You can create a ``.env.template`` file by running the following command inside the projects directory:

``$ python manage.py createenv``

Fill out the newly created file and rename it to ``.env``. All of these variables need to be filled with sensible values, but your settings may change and at least the database password and secret key should be your own.

Regarding the secret key: Django offers a function that will create a brandnew key for you: ``django.core.management.utils.get_random_secret_key()``.

Set ``DEBUG`` to ``True`` if you are just trying things out. Finally: no, neither password should be ``password``.

### Create a Database

The Data Mining Lab has been configured to use Postgres. With minimal effort, you could change the codebase to use MySQL or adjacent, mostly changing a few settings in ``settings.py`` in the root folder. If you are fine with Postgres,

* install Postgres (https://www.postgresql.org/), if you haven't done so already.
* Open pgAdmin and create a new database, user, and so on.
* Add all the variables (user name, database name, password, host, and port) to the ``.env`` file for Django to use.

### Migrate the Schema

You can now fill the database with the required tables by running the Django migrations. Additionally, there are some fixtures that need to added to tables that supply the predefined user groups, i.e., access management. In the root directory, run:

* ``python manage.py migrate``
* ``python manage.py loaddata auth_group auth_permission``

This sets you up with an empty database, but filled auth permissions for the three user groups: AdminGroup, CreateGroup, and UseGroup.

### Create Superuser

You will need to create a superuser to access the Django admin page. Do it by running

``python manage.py createsuperuser``

and supply the required info, username and password.

### Load the Webserver

In Debug mode, the server can be started from the command line with

``python manage.py runserver``.

This should result in the server running on ``localhost``. Access the server (the command line will tell you the URL) and go the admin panel via the URL ``/admin``.

Congratulations, you have set up the current version of the Data Mining Lab!