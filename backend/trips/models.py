from django.db import models
from django.utils import timezone


class Trip(models.Model):
    """Model for storing trip details and calculations"""

    # Input fields
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    current_cycle_hours = models.FloatField(default=0)  # Hours already used in 8-day cycle

    # Calculated fields
    total_distance_miles = models.FloatField(null=True, blank=True)
    total_driving_hours = models.FloatField(null=True, blank=True)
    total_on_duty_hours = models.FloatField(null=True, blank=True)
    num_days_required = models.IntegerField(default=1)

    # Route data (stored as JSON)
    route_data = models.JSONField(null=True, blank=True)

    # HOS compliance
    is_compliant = models.BooleanField(default=True)
    compliance_notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trip: {self.current_location} → {self.pickup_location} → {self.dropoff_location}"


class LogSheet(models.Model):
    """Model for individual ELD log sheets"""

    DUTY_STATUS_CHOICES = [
        ('OFF_DUTY', 'Off Duty'),
        ('SLEEPER_BERTH', 'Sleeper Berth'),
        ('DRIVING', 'Driving'),
        ('ON_DUTY', 'On Duty (Not Driving)'),
    ]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='log_sheets')
    date = models.DateField()
    day_number = models.IntegerField(default=1)  # Which day of the trip

    # Log sheet data (stored as timeline JSON)
    # Format: [{"status": "OFF_DUTY", "start_hour": 0, "end_hour": 6, "location": "Richmond, VA"}, ...]
    timeline_data = models.JSONField(default=list)

    # Daily totals
    total_off_duty_hours = models.FloatField(default=0)
    total_sleeper_berth_hours = models.FloatField(default=0)
    total_driving_hours = models.FloatField(default=0)
    total_on_duty_hours = models.FloatField(default=0)
    total_miles = models.FloatField(default=0)

    # Carrier info
    carrier_name = models.CharField(max_length=255, default="FMCSA Carrier")
    carrier_address = models.CharField(max_length=255, default="City, State")
    driver_name = models.CharField(max_length=255, default="Driver Name")
    vehicle_number = models.CharField(max_length=50, default="")

    # Remarks
    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'day_number']

    def __str__(self):
        return f"Log Sheet - Day {self.day_number} ({self.date})"
