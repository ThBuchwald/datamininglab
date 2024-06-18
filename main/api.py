import logging
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Sample, Experiment, FundingBody, Institute, Method, Project, Staff, SampleType
from .serializers import SampleSerializer, ExperimentSerializer, FundingBodySerializer, InstituteSerializer, \
                         MethodSerializer, ProjectSerializer, StaffSerializer, SampleTypeSerializer, \
                         SampleTypeBatterySerializer, SampleTypeSolidsSerializer, SampleTypeLiquidSerializer, SampleTypeSuspensionSerializer

logger = logging.getLogger(__name__)

# This class adds logging for all API Viewsets
class LogUnauthorizedAccess(permissions.BasePermission):
    """
    Permission class that logs unauthorized attempts to access API endpoints.
    """

    def has_permission(self, request, view):
        # Perform the standard permission check
        has_permission = super().has_permission(request, view)

        # If the request does not have permission, log it
        if not has_permission:
            username = request.user.username if request.user.is_authenticated else 'Anonymous'
            logger.warning(
                f"Unauthorized access attempt to {request.path} by an unauthenticated user (IP: {request.META.get('REMOTE_ADDR')})."
            )

        return has_permission


class ReadWriteViewSet(viewsets.ModelViewSet):  # CRUD endpoints
    pass


class ReadOnlyViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin,
                      mixins.ListModelMixin):  # Read-only endpoints
    pass


class SampleViewSet(ReadWriteViewSet):
    queryset = Sample.objects.select_related('user').all()
    serializer_class = SampleSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [LogUnauthorizedAccess]

    def perform_create(self, serializer):
        # Assign the authenticated user (the owner of the token) to the 'user' field of the sample
        serializer.save(user=self.request.user)


class ExperimentViewSet(ReadWriteViewSet):
    queryset = Experiment.objects.select_related('user').all()
    serializer_class = ExperimentSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [LogUnauthorizedAccess]

    def perform_create(self, serializer):
        # Assign the authenticated user (the owner of the token) to the 'user' field of the sample
        serializer.save(user=self.request.user)


class FundingBodyViewSet(ReadOnlyViewSet):
    queryset = FundingBody.objects.all()
    serializer_class = FundingBodySerializer
    permission_classes = [LogUnauthorizedAccess]


class InstituteViewSet(ReadOnlyViewSet):
    queryset = Institute.objects.all()
    serializer_class = InstituteSerializer
    permission_classes = [LogUnauthorizedAccess]


class MethodViewSet(ReadOnlyViewSet):
    queryset = Method.objects.all()
    serializer_class = MethodSerializer
    permission_classes = [LogUnauthorizedAccess]


class ProjectViewSet(ReadOnlyViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [LogUnauthorizedAccess]


class SampleTypeViewSet(ReadOnlyViewSet):
    queryset = SampleType.objects.all()
    serializer_class = SampleTypeSerializer
    permission_classes = [LogUnauthorizedAccess]


class StaffViewSet(ReadOnlyViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [LogUnauthorizedAccess]


@api_view(['GET'])
def sample_type_info(request, sample_type_name):
    serializer_classes = {
        'Battery': SampleTypeBatterySerializer,
        'Liquid': SampleTypeLiquidSerializer,
        'Solids': SampleTypeSolidsSerializer,
        'Suspension': SampleTypeSuspensionSerializer,
    }
    # Get the serializer for the requested sample type
    serializer_class = serializer_classes.get(sample_type_name.capitalize())
    if serializer_class:
        # Create a serializer instance
        serializer = serializer_class()
        # Return the fields of the serializer as the expected schema
        fields_info = {
            field_name: {
                'type': str(field.__class__.__name__),
                'help_text': str(field.help_text) if field.help_text else '',
                'required': field.required,
                'allow_null': field.allow_null,
            }
            for field_name, field in serializer.get_fields().items()
        }
        return Response(fields_info)

    return Response({'error': 'Sample type not found'}, status=404)