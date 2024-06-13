from django.core.management.base import BaseCommand

env_vars = {
    "DEBUG": "True or False",
    "DB_NAME": "datamininglab",
    "DB_HOST": "localhost",
    "DB_USER": "postgres",
    "DB_PASSWORD": "password",
    "DB_PORT": "1234",
    "EMAIL_HOST": "smtp.xxxxxx.com",
    "EMAIL_HOST_USER": "xxxxxx@xxxxxx.com",
    "EMAIL_HOST_PASSWORD": "password",
    "EMAIL_PORT": "123",
    "MEDIA_FOLDER": "/media",
    "SECRET": "use django.core.management.utils.get_random_secret_key()",
}

class Command(BaseCommand):
    help = "Generates a .env template file"

    def handle(self, *args, **options):
        filename = ".env.template"
        with open(filename, "w") as file:
            for key, value in env_vars.items():
                file.write(f"{key}={value}\n")
        self.stdout.write(self.style.SUCCESS(f"Successfully created {filename}"))