import os
from django.core.management.base import BaseCommand
from datamininglab.settings import BASE_DIR

class Command(BaseCommand):
    help = 'Collects specified files and combines their content into a single TXT file'

    def handle(self, *args, **kwargs):
        # List of files to include in the output TXT file
        files_to_include = [
            'datamininglab/settings.py',
            'datamininglab/urls.py',
            'main/admin.py',
            'main/api.py',
            'main/apps.py',
            'main/forms.py',
            'main/models.py',
            'main/tests.py',
            'main/urls.py',
            'main/views.py',
            'main/serializers/main_serializers.py',
            'main/serializers/sample_type_serializers.py',
            'main/utils/email_utils.py',
            'main/utils/file_utils.py',
            'main/utils/validation_utils.py',
        ]
        
        output_file_path = os.path.join(BASE_DIR, 'gpt_codebase.txt')
        
        with open(output_file_path, 'w') as output_file:
            for file_path in files_to_include:
                full_file_path = os.path.join(BASE_DIR, file_path)
                if os.path.exists(full_file_path):
                    with open(file_path, 'r') as input_file:
                        content = input_file.read()
                        output_file.write(f"```{file_path}\n")
                        #output_file.write("#" * 80 + "\n")
                        output_file.write(content)
                        output_file.write("\n```\n\n")
                else:
                    self.stdout.write(self.style.WARNING(f"File not found: {file_path}"))
        
        self.stdout.write(self.style.SUCCESS(f"Collected code written to {output_file_path}"))
