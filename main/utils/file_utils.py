import os
from django.http import Http404, FileResponse
from django.core.exceptions import PermissionDenied
from django.conf import settings

def download_file(request, subfolder, filename):
    """
    Downloads a file from a specific subfolder within the MEDIA_ROOT, ensuring the user has the proper permissions.

    Args:
    - request: HttpRequest object, needed to check user permissions.
    - subfolder: String representing the subdirectory within MEDIA_ROOT where the file is located.
    - filename: String representing the name of the file to be downloaded.

    Returns:
    - FileResponse to facilitate file download.

    Raises:
    - Http404 if the file does not exist.
    - PermissionDenied if the user does not have permission to download the file.
    """
    file_path = os.path.join(settings.MEDIA_ROOT, subfolder, filename)
    if not os.path.exists(file_path):
        raise Http404("File does not exist")
    
    if not request.user.groups.filter(name='UseGroup').exists():
        raise PermissionDenied("You do not have permission to access this file")

    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)