from rest_framework import serializers
from .models import Sample, Experiment, FundingBody, Institute, Method, Project, Staff

''' ------------
    sample types
    ------------ '''


class SampleTypeBatterySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    composition = serializers.CharField(max_length=255, allow_blank=True)
    manufacturer = serializers.CharField(max_length=255)
    produced = serializers.DateField(allow_null=True)
    comment = serializers.CharField(max_length=255, allow_null=True)

    # allowing all empty values to be accepted as null
    def to_internal_value(self, data):
        for field in data:
            if field == '':
                field = None
        return super(SampleTypeBatterySerializer, self).to_internal_value(data)


class SampleTypeSolidsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    weight_in_g = serializers.FloatField(min_value=0.0)
    volume_in_ccm = serializers.FloatField(min_value=0.0, allow_null=True)
    density_in_gccm = serializers.FloatField(min_value=0.0, allow_null=True)
    comment = serializers.CharField(max_length=255, allow_null=True)

    def to_internal_value(self, data):
        for field in data:
            if field == '':
                field = None
        return super(SampleTypeBatterySerializer, self).to_internal_value(data)


class SampleTypeLiquidSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    volume_in_ccm = serializers.FloatField(min_value=0.0)
    weight_in_g = serializers.FloatField(min_value=0.0, allow_null=True)
    density_in_gccm = serializers.FloatField(min_value=0.0, allow_null=True)
    comment = serializers.CharField(max_length=255, allow_null=True)

    def to_internal_value(self, data):
        for field in data:
            if field == '':
                field = None
        return super(SampleTypeBatterySerializer, self).to_internal_value(data)


class SampleTypeSuspensionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    liquid = serializers.CharField(max_length=255)
    solid = serializers.CharField(max_length=255)
    volume_in_ccm = serializers.FloatField(min_value=0.0)
    weight_in_g = serializers.FloatField(min_value=0.0, allow_null=True)
    density_in_gccm = serializers.FloatField(min_value=0.0, allow_null=True)

    def to_internal_value(self, data):
        for field in data:
            if field == '':
                field = None
        return super(SampleTypeBatterySerializer, self).to_internal_value(data)


''' ------------
    API-specific
    ------------ '''


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = '__all__'


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = '__all__'


class FundingBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = FundingBody
        fields = '__all__'


class InstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        fields = '__all__'


class MethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Method
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'
