import logging
from rest_framework import viewsets, mixins, permissions, views, serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer, \
                                  OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes
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


@extend_schema_view(
    list=extend_schema(summary="List all samples"),
    create=extend_schema(summary="Create a new sample"),
    retrieve=extend_schema(summary="Retrieve a sample"),
    update=extend_schema(summary="Update a sample"),
    partial_update=extend_schema(summary="Partially update a sample (only provided fields)"),
    destroy=extend_schema(summary="Delete a sample")
)
class SampleViewSet(ReadWriteViewSet):
    queryset = Sample.objects.select_related('user').all()
    serializer_class = SampleSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [LogUnauthorizedAccess]

    def perform_create(self, serializer):
        # Assign the authenticated user (the owner of the token) to the 'user' field of the sample
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(summary="List all experiments"),
    create=extend_schema(summary="Create a new experiment"),
    retrieve=extend_schema(summary="Retrieve an experiment"),
    update=extend_schema(summary="Update an experiment"),
    partial_update=extend_schema(summary="Partially update an experiment (only provided fields)"),
    destroy=extend_schema(summary="Delete an experiment")
)
class ExperimentViewSet(ReadWriteViewSet):
    queryset = Experiment.objects.select_related('user').all()
    serializer_class = ExperimentSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [LogUnauthorizedAccess]

    def perform_create(self, serializer):
        # Assign the authenticated user (the owner of the token) to the 'user' field of the sample
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(summary="List all funding bodies"),
    retrieve=extend_schema(summary="Retrieve a funding body")
)
class FundingBodyViewSet(ReadOnlyViewSet):
    queryset = FundingBody.objects.all()
    serializer_class = FundingBodySerializer
    permission_classes = [LogUnauthorizedAccess]


@extend_schema_view(
    list=extend_schema(summary="List all institutes"),
    retrieve=extend_schema(summary="Retrieve an institute")
)
class InstituteViewSet(ReadOnlyViewSet):
    queryset = Institute.objects.all()
    serializer_class = InstituteSerializer
    permission_classes = [LogUnauthorizedAccess]


@extend_schema_view(
    list=extend_schema(summary="List all methods"),
    retrieve=extend_schema(summary="Retrieve a method")
)
class MethodViewSet(ReadOnlyViewSet):
    queryset = Method.objects.all()
    serializer_class = MethodSerializer
    permission_classes = [LogUnauthorizedAccess]


@extend_schema_view(
    list=extend_schema(summary="List all projects"),
    retrieve=extend_schema(summary="Retrieve a project")
)
class ProjectViewSet(ReadOnlyViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [LogUnauthorizedAccess]


@extend_schema_view(
    list=extend_schema(summary="List all sample types"),
    retrieve=extend_schema(summary="Retrieve a sample type")
)
class SampleTypeViewSet(ReadOnlyViewSet):
    queryset = SampleType.objects.all()
    serializer_class = SampleTypeSerializer
    permission_classes = [LogUnauthorizedAccess]

# staff personal data may not be read via API
#@extend_schema_view(
#    list=extend_schema(summary="List all staff members"),
#    retrieve=extend_schema(summary="Retrieve a staff member")
#)
#class StaffViewSet(ReadOnlyViewSet):
#    queryset = Staff.objects.all()
#    serializer_class = StaffSerializer
#    permission_classes = [LogUnauthorizedAccess]


class SampleTypeInfoView(views.APIView):

    @extend_schema(
        summary="Retrieve schema information for a specific sample type",
        parameters=[
            OpenApiParameter(name='sample_type_name', description='Name of the sample type', required=True, type=str)
        ],
        responses={
            200: inline_serializer(
                name='SampleTypeInfoResponse',
                fields={
                    'type': OpenApiTypes.STR,
                    'help_text': OpenApiTypes.STR,
                    'required': OpenApiTypes.BOOL,
                    'allow_null': OpenApiTypes.BOOL
                }
            ),
            404: OpenApiResponse(description="Sample type not found", response=OpenApiTypes.OBJECT)
        },
        description="Returns dynamic schema information based on the sample type name."
    )
    def get(self, request, *args, **kwargs):
        sample_type_name = request.query_params.get('sample_type_name')
        serializer_class = {
            'Battery': SampleTypeBatterySerializer,
            'Solids': SampleTypeSolidsSerializer,
            'Liquid': SampleTypeLiquidSerializer,
            'Suspension': SampleTypeSuspensionSerializer,
        }.get(sample_type_name.capitalize())

        if serializer_class:
            # Create an instance of the serializer
            serializer = serializer_class()
            # Manually building response dictionary for fields description
            fields_info = {
                field_name: {
                    'type': field.__class__.__name__,
                    'help_text': field.help_text if field.help_text else '',
                    'required': field.required,
                    'allow_null': field.allow_null,
                }
                for field_name, field in serializer.get_fields().items()
            }
            return Response(fields_info)
        
        return Response({'error': 'Sample type not found'}, status=status.HTTP_404_NOT_FOUND)