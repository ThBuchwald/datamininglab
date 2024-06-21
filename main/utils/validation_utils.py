import re
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError
from ..models import Institute, Method
from django.db.models import Max
from ..serializers.sample_type_serializers import (
    SampleTypeBatterySerializer, SampleTypeSolidsSerializer, 
    SampleTypeLiquidSerializer, SampleTypeSuspensionSerializer,
)


def validate_sample_id(value):
    # Check format yymmdd_hhmmss_iiaaaa
    if not re.match(r'^\d{6}_\d{6}_\d{6}$', value):
        raise DjangoValidationError("Sample ID must be in the format 'yymmdd_hhmmss_iiaaaa'.")

    # Extract date, time, institution, and method
    date_str = value[:6]
    time_str = value[7:13]
    institution_code = int(value[14:16])
    method_code = int(value[16:20])

    # Check if date is valid and in the past
    try:
        date = datetime.strptime(date_str, '%y%m%d').date()
        if date >= timezone.now().date():
            raise DjangoValidationError("The date part of the Sample ID must be in the past.")
    except ValueError:
        raise DjangoValidationError("The date part of the Sample ID is not valid.")

    # Check if time is valid
    try:
        datetime.strptime(time_str, '%H%M%S')
    except ValueError:
        raise DjangoValidationError("The time part of the Sample ID is not valid.")

    # Check if institution code is valid
    max_institution_id = Institute.objects.aggregate(Max('id'))['id__max']
    if institution_code > max_institution_id:
        raise DjangoValidationError(f"The institution code {institution_code} exceeds the highest institute id {max_institution_id}.")

    # Check if method code is valid
    max_method_id = Method.objects.aggregate(Max('id'))['id__max']
    if method_code > max_method_id:
        raise DjangoValidationError(f"The method code {method_code} exceeds the highest method id {max_method_id}.")
    

def validate_json_structure(json_data, sample_type):
    # Map sample types to their serializers
    sample_type_serializers = {
        'Battery': SampleTypeBatterySerializer,
        'Solids': SampleTypeSolidsSerializer,
        'Liquid': SampleTypeLiquidSerializer,
        'Suspension': SampleTypeSuspensionSerializer,
    }

    # Get the serializer for the chosen sample type
    serializer_class = sample_type_serializers.get(sample_type)

    if not serializer_class:
        return False, "Invalid sample type name."

    # Validate the JSON data using the serializer
    serializer = serializer_class(data=json_data)

    if not serializer.is_valid():
        return False, serializer.errors

    return True