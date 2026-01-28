from rest_framework import serializers
from .models import Trip, LogSheet


class LogSheetSerializer(serializers.ModelSerializer):
    """Serializer for log sheets"""

    class Meta:
        model = LogSheet
        fields = [
            'id', 'day_number', 'date', 'timeline_data',
            'total_off_duty_hours', 'total_sleeper_berth_hours',
            'total_driving_hours', 'total_on_duty_hours', 'total_miles',
            'carrier_name', 'carrier_address', 'driver_name',
            'vehicle_number', 'remarks', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TripSerializer(serializers.ModelSerializer):
    """Serializer for trips"""

    log_sheets = LogSheetSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = [
            'id', 'current_location', 'pickup_location', 'dropoff_location',
            'current_cycle_hours', 'total_distance_miles', 'total_driving_hours',
            'total_on_duty_hours', 'num_days_required', 'route_data',
            'is_compliant', 'compliance_notes', 'log_sheets',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_distance_miles', 'total_driving_hours',
            'total_on_duty_hours', 'num_days_required', 'route_data',
            'is_compliant', 'compliance_notes', 'created_at', 'updated_at'
        ]


class TripCreateSerializer(serializers.Serializer):
    """Serializer for creating a new trip calculation"""

    current_location = serializers.CharField(max_length=255)
    pickup_location = serializers.CharField(max_length=255)
    dropoff_location = serializers.CharField(max_length=255)
    current_cycle_hours = serializers.FloatField(default=0, min_value=0, max_value=70)

    # Optional carrier/driver info
    carrier_name = serializers.CharField(max_length=255, default="FMCSA Carrier", required=False)
    carrier_address = serializers.CharField(max_length=255, default="City, State", required=False)
    driver_name = serializers.CharField(max_length=255, default="Driver Name", required=False)
    vehicle_number = serializers.CharField(max_length=50, default="", required=False)
