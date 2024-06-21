from rest_framework import serializers


class SampleTypeBatterySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    composition = serializers.CharField(max_length=255, allow_blank=True, required=False)
    manufacturer = serializers.CharField(max_length=255)
    produced = serializers.DateField(allow_null=True, required=False)
    comment = serializers.CharField(max_length=255, allow_null=True, required=False)

    # allowing all empty values to be accepted as null
    def to_internal_value(self, data):
        for field in data.keys():
            if field == '':
                field = None
        return super(SampleTypeBatterySerializer, self).to_internal_value(data)


class SampleTypeSolidsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    weight_in_g = serializers.FloatField(min_value=0.0)
    volume_in_ccm = serializers.FloatField(min_value=0.0, allow_null=True, required=False)
    density_in_gccm = serializers.FloatField(min_value=0.0, allow_null=True, required=False)
    comment = serializers.CharField(max_length=255, allow_null=True, required=False)

    def to_internal_value(self, data):
        for field in data.keys():
            if field == '':
                field = None
        return super(SampleTypeSolidsSerializer, self).to_internal_value(data)


class SampleTypeLiquidSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    volume_in_ccm = serializers.FloatField(min_value=0.0)
    weight_in_g = serializers.FloatField(min_value=0.0, allow_null=True, required=False)
    density_in_gccm = serializers.FloatField(min_value=0.0, allow_null=True, required=False)
    comment = serializers.CharField(max_length=255, allow_null=True, required=False)

    def to_internal_value(self, data):
        for field in data.keys():
            if field == '':
                field = None
        return super(SampleTypeLiquidSerializer, self).to_internal_value(data)


class SampleTypeSuspensionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    liquid = serializers.CharField(max_length=255)
    solid = serializers.CharField(max_length=255)
    volume_in_ccm = serializers.FloatField(min_value=0.0)
    weight_in_g = serializers.FloatField(min_value=0.0, allow_null=True, required=False)
    density_in_gccm = serializers.FloatField(min_value=0.0, allow_null=True, required=False)

    def to_internal_value(self, data):
        for field in data.keys():
            if field == '':
                field = None
        return super(SampleTypeSuspensionSerializer, self).to_internal_value(data)