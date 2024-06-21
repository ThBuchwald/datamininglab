from rest_framework import serializers
import json
import zipfile
from main.models import Sample, Experiment, FundingBody, Institute, Method, Project, SampleType, Staff
from main.utils.validation_utils import validate_sample_id, validate_json_structure



class SampleSerializer(serializers.ModelSerializer):
    sample_id = serializers.CharField(validators=[validate_sample_id])
    
    class Meta:
        model = Sample
        fields = '__all__'
        read_only_fields = ('user',)

    def validate_supplementary_file(self, file):
        if file:
            if not zipfile.is_zipfile(file):
                raise serializers.ValidationError("Only zip files are allowed.")
        return file

    def validate_sample_info(self, sample_info):
        sample_type_id = self.initial_data.get('sample_type')

        if not sample_info:
            raise serializers.ValidationError("This field is required.")

        try:
            sample_type = SampleType.objects.get(pk=sample_type_id)
            sample_type_name = sample_type.name
        except SampleType.DoesNotExist:
            raise serializers.ValidationError("Invalid sample type.")

        try:
            sample_info_file = sample_info.read().decode('utf-8')
            sample_info_json = json.loads(sample_info_file)
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON file. Please upload a valid JSON file.")
        except Exception as e:
            raise serializers.ValidationError(f"An error occurred while processing the file: {e}")

        if not validate_json_structure(sample_info_json, sample_type_name):
            raise serializers.ValidationError("Invalid JSON structure for the selected sample type.")

        return sample_info
    

class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = '__all__'
        read_only_fields = ('user',)

    def validate_experiment_file(self, file):
        if file:
            if not zipfile.is_zipfile(file):
                raise serializers.ValidationError("Only zip files are allowed.")
        return file
    

class FundingBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = FundingBody
        fields = '__all__'


class InstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        fields = '__all__'


# needs no file check since it cannot be created via API
class MethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Method
        fields = '__all__'


# needs no file check since it cannot be created via API
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class SampleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleType
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'
