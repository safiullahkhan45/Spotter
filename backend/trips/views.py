from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, timedelta

from .models import Trip, LogSheet
from .serializers import TripSerializer, TripCreateSerializer, LogSheetSerializer
from .hos_calculator import HOSCalculator
from .routing_service import RoutingService


class TripViewSet(viewsets.ModelViewSet):
    """API endpoints for trip planning and ELD log generation"""

    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    def create(self, request):
        """
        Create a new trip calculation

        POST /api/trips/
        {
            "current_location": "Richmond, VA",
            "pickup_location": "Baltimore, MD",
            "dropoff_location": "Newark, NJ",
            "current_cycle_hours": 15,
            "carrier_name": "ABC Trucking",
            "driver_name": "John Doe",
            "vehicle_number": "123"
        }
        """
        serializer = TripCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Get route information
        routing_service = RoutingService()
        route_data = routing_service.get_route_for_trip(
            current_location=data['current_location'],
            pickup_location=data['pickup_location'],
            dropoff_location=data['dropoff_location']
        )

        if not route_data:
            return Response(
                {"error": "Could not calculate route. Please check location names."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate HOS schedule
        hos_calculator = HOSCalculator(current_cycle_hours=data['current_cycle_hours'])
        hos_result = hos_calculator.calculate_trip(
            distance_miles=route_data['distance_miles'],
            current_location=data['current_location'],
            pickup_location=data['pickup_location'],
            dropoff_location=data['dropoff_location']
        )

        # Create Trip instance
        trip = Trip.objects.create(
            current_location=data['current_location'],
            pickup_location=data['pickup_location'],
            dropoff_location=data['dropoff_location'],
            current_cycle_hours=data['current_cycle_hours'],
            total_distance_miles=hos_result['total_distance_miles'],
            total_driving_hours=hos_result['total_driving_hours'],
            total_on_duty_hours=hos_result['total_on_duty_hours'],
            num_days_required=hos_result['num_days'],
            route_data=route_data,
            is_compliant=hos_result['is_compliant'],
            compliance_notes=hos_result['compliance_notes']
        )

        # Create log sheets
        carrier_name = data.get('carrier_name', 'FMCSA Carrier')
        carrier_address = data.get('carrier_address', 'City, State')
        driver_name = data.get('driver_name', 'Driver Name')
        vehicle_number = data.get('vehicle_number', '')

        for log_data in hos_result['log_sheets']:
            LogSheet.objects.create(
                trip=trip,
                date=log_data['date'],
                day_number=log_data['day_number'],
                timeline_data=log_data['timeline'],
                total_off_duty_hours=log_data['totals']['off_duty'],
                total_sleeper_berth_hours=log_data['totals']['sleeper_berth'],
                total_driving_hours=log_data['totals']['driving'],
                total_on_duty_hours=log_data['totals']['on_duty'],
                total_miles=log_data['total_miles'],
                carrier_name=carrier_name,
                carrier_address=carrier_address,
                driver_name=driver_name,
                vehicle_number=vehicle_number,
                remarks=log_data['remarks']
            )

        # Return complete trip data
        response_serializer = TripSerializer(trip)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
