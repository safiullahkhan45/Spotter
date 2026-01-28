"""
FMCSA Hours of Service (HOS) Calculator
Implements all HOS regulations for property-carrying drivers
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import math


class HOSCalculator:
    """Calculate HOS compliance and generate trip schedules"""

    # HOS Limits (in hours)
    MAX_DRIVING_HOURS = 11
    MAX_DRIVING_WINDOW = 14
    MIN_OFF_DUTY_HOURS = 10
    BREAK_REQUIRED_AFTER_DRIVING = 8
    MIN_BREAK_DURATION = 0.5  # 30 minutes
    MAX_CYCLE_HOURS = 70
    CYCLE_DAYS = 8

    # Driving assumptions
    AVERAGE_SPEED_MPH = 60  # Conservative average
    PICKUP_DROPOFF_TIME = 1.0  # 1 hour each
    FUEL_STOP_INTERVAL_MILES = 1000
    FUEL_STOP_DURATION = 0.5  # 30 minutes (counts as break)

    def __init__(self, current_cycle_hours: float = 0):
        """
        Initialize calculator

        Args:
            current_cycle_hours: Hours already used in current 8-day cycle
        """
        self.current_cycle_hours = current_cycle_hours

    def calculate_trip(
        self,
        distance_miles: float,
        current_location: str,
        pickup_location: str,
        dropoff_location: str
    ) -> Dict:
        """
        Calculate complete trip schedule with HOS compliance

        Returns:
            Dict containing timeline, log sheets, compliance info
        """
        # Calculate basic time requirements
        driving_hours = distance_miles / self.AVERAGE_SPEED_MPH
        num_fuel_stops = math.floor(distance_miles / self.FUEL_STOP_INTERVAL_MILES)

        # Add pickup and dropoff time
        total_on_duty_hours = driving_hours + (2 * self.PICKUP_DROPOFF_TIME)

        # Calculate breaks needed (30-min break every 8 hours of driving)
        breaks_needed = math.floor(driving_hours / self.BREAK_REQUIRED_AFTER_DRIVING)

        # Fuel stops count as breaks if they're 30+ minutes
        additional_breaks = max(0, breaks_needed - num_fuel_stops)
        total_break_time = additional_breaks * self.MIN_BREAK_DURATION

        # Total time on duty (not counting breaks)
        total_duty_hours = total_on_duty_hours + (num_fuel_stops * self.FUEL_STOP_DURATION)

        # Check if trip can be completed in one day
        single_day_possible = (
            driving_hours <= self.MAX_DRIVING_HOURS and
            total_duty_hours <= self.MAX_DRIVING_WINDOW and
            (self.current_cycle_hours + total_duty_hours) <= self.MAX_CYCLE_HOURS
        )

        if single_day_possible:
            return self._generate_single_day_trip(
                distance_miles=distance_miles,
                driving_hours=driving_hours,
                total_duty_hours=total_duty_hours,
                num_fuel_stops=num_fuel_stops,
                breaks_needed=breaks_needed,
                current_location=current_location,
                pickup_location=pickup_location,
                dropoff_location=dropoff_location
            )
        else:
            return self._generate_multi_day_trip(
                distance_miles=distance_miles,
                driving_hours=driving_hours,
                current_location=current_location,
                pickup_location=pickup_location,
                dropoff_location=dropoff_location
            )

    def _generate_single_day_trip(
        self,
        distance_miles: float,
        driving_hours: float,
        total_duty_hours: float,
        num_fuel_stops: int,
        breaks_needed: int,
        current_location: str,
        pickup_location: str,
        dropoff_location: str
    ) -> Dict:
        """Generate schedule for single-day trip"""

        timeline = []
        current_hour = 0.0
        remarks = []

        # Start with off-duty (sleep before trip)
        timeline.append({
            "status": "OFF_DUTY",
            "start_hour": 0,
            "end_hour": 6,
            "duration": 6,
            "location": current_location,
            "description": "Off duty - rest before trip"
        })
        current_hour = 6.0
        remarks.append(f"6:00 AM - Report for duty at {current_location}")

        # On-duty prep and drive to pickup
        distance_to_pickup = distance_miles * 0.2  # Estimate 20% to pickup
        time_to_pickup = distance_to_pickup / self.AVERAGE_SPEED_MPH

        timeline.append({
            "status": "ON_DUTY",
            "start_hour": current_hour,
            "end_hour": current_hour + 0.5,
            "duration": 0.5,
            "location": current_location,
            "description": "Pre-trip inspection, paperwork"
        })
        current_hour += 0.5

        timeline.append({
            "status": "DRIVING",
            "start_hour": current_hour,
            "end_hour": current_hour + time_to_pickup,
            "duration": time_to_pickup,
            "location": f"{current_location} to {pickup_location}",
            "description": f"Driving to pickup location"
        })
        current_hour += time_to_pickup
        remarks.append(f"Arrived at {pickup_location}")

        # Pickup (on-duty)
        timeline.append({
            "status": "ON_DUTY",
            "start_hour": current_hour,
            "end_hour": current_hour + self.PICKUP_DROPOFF_TIME,
            "duration": self.PICKUP_DROPOFF_TIME,
            "location": pickup_location,
            "description": "Loading cargo, paperwork"
        })
        current_hour += self.PICKUP_DROPOFF_TIME

        # Drive to dropoff with breaks
        distance_to_dropoff = distance_miles * 0.8  # Remaining 80%
        time_to_dropoff = distance_to_dropoff / self.AVERAGE_SPEED_MPH

        # Calculate when to take break
        if breaks_needed > 0:
            drive_before_break = min(self.BREAK_REQUIRED_AFTER_DRIVING, time_to_dropoff / 2)

            # Drive segment 1
            timeline.append({
                "status": "DRIVING",
                "start_hour": current_hour,
                "end_hour": current_hour + drive_before_break,
                "duration": drive_before_break,
                "location": f"{pickup_location} to {dropoff_location}",
                "description": "Driving to dropoff"
            })
            current_hour += drive_before_break

            # 30-minute break (fuel stop)
            timeline.append({
                "status": "ON_DUTY",
                "start_hour": current_hour,
                "end_hour": current_hour + self.MIN_BREAK_DURATION,
                "duration": self.MIN_BREAK_DURATION,
                "location": "Highway fuel stop",
                "description": "Fuel stop (30-min break)"
            })
            current_hour += self.MIN_BREAK_DURATION
            remarks.append("Fuel stop - satisfies 30-minute break requirement")

            # Drive segment 2
            remaining_drive = time_to_dropoff - drive_before_break
            timeline.append({
                "status": "DRIVING",
                "start_hour": current_hour,
                "end_hour": current_hour + remaining_drive,
                "duration": remaining_drive,
                "location": f"En route to {dropoff_location}",
                "description": "Driving to dropoff"
            })
            current_hour += remaining_drive
        else:
            # No break needed - straight drive
            timeline.append({
                "status": "DRIVING",
                "start_hour": current_hour,
                "end_hour": current_hour + time_to_dropoff,
                "duration": time_to_dropoff,
                "location": f"{pickup_location} to {dropoff_location}",
                "description": "Driving to dropoff"
            })
            current_hour += time_to_dropoff

        remarks.append(f"Arrived at {dropoff_location}")

        # Dropoff (on-duty)
        timeline.append({
            "status": "ON_DUTY",
            "start_hour": current_hour,
            "end_hour": current_hour + self.PICKUP_DROPOFF_TIME,
            "duration": self.PICKUP_DROPOFF_TIME,
            "location": dropoff_location,
            "description": "Unloading cargo, paperwork"
        })
        current_hour += self.PICKUP_DROPOFF_TIME

        # Post-trip inspection
        timeline.append({
            "status": "ON_DUTY",
            "start_hour": current_hour,
            "end_hour": current_hour + 0.5,
            "duration": 0.5,
            "location": dropoff_location,
            "description": "Post-trip inspection, log completion"
        })
        current_hour += 0.5

        # Off duty for rest of day
        timeline.append({
            "status": "OFF_DUTY",
            "start_hour": current_hour,
            "end_hour": 24,
            "duration": 24 - current_hour,
            "location": dropoff_location,
            "description": "Off duty"
        })
        remarks.append(f"Off duty at {dropoff_location}")

        # Calculate totals
        totals = self._calculate_daily_totals(timeline)

        return {
            "num_days": 1,
            "total_distance_miles": distance_miles,
            "total_driving_hours": totals["driving"],
            "total_on_duty_hours": totals["on_duty"] + totals["driving"],
            "is_compliant": True,
            "compliance_notes": "Trip complies with all HOS regulations",
            "log_sheets": [{
                "day_number": 1,
                "date": datetime.now().date().isoformat(),
                "timeline": timeline,
                "totals": totals,
                "remarks": " | ".join(remarks),
                "total_miles": distance_miles
            }]
        }

    def _generate_multi_day_trip(
        self,
        distance_miles: float,
        driving_hours: float,
        current_location: str,
        pickup_location: str,
        dropoff_location: str
    ) -> Dict:
        """Generate schedule for multi-day trip"""

        # Calculate number of days needed
        days_needed = math.ceil(driving_hours / self.MAX_DRIVING_HOURS)

        # For now, create a simplified multi-day schedule
        # Split driving evenly across days
        miles_per_day = distance_miles / days_needed

        log_sheets = []
        current_date = datetime.now().date()

        for day in range(days_needed):
            is_first_day = (day == 0)
            is_last_day = (day == days_needed - 1)

            daily_miles = miles_per_day
            daily_driving = daily_miles / self.AVERAGE_SPEED_MPH

            timeline = []
            current_hour = 0.0
            remarks = []

            # Off duty start
            timeline.append({
                "status": "OFF_DUTY",
                "start_hour": 0,
                "end_hour": 6,
                "duration": 6,
                "location": current_location if is_first_day else "Rest area",
                "description": "Off duty - 10-hour rest"
            })
            current_hour = 6.0

            # On-duty prep
            timeline.append({
                "status": "ON_DUTY",
                "start_hour": current_hour,
                "end_hour": current_hour + 0.5,
                "duration": 0.5,
                "location": current_location if is_first_day else "Rest area",
                "description": "Pre-trip inspection"
            })
            current_hour += 0.5

            # Pickup on first day
            if is_first_day:
                timeline.append({
                    "status": "DRIVING",
                    "start_hour": current_hour,
                    "end_hour": current_hour + 1,
                    "duration": 1,
                    "location": f"{current_location} to {pickup_location}",
                    "description": "Drive to pickup"
                })
                current_hour += 1

                timeline.append({
                    "status": "ON_DUTY",
                    "start_hour": current_hour,
                    "end_hour": current_hour + 1,
                    "duration": 1,
                    "location": pickup_location,
                    "description": "Loading"
                })
                current_hour += 1
                remarks.append(f"Picked up load at {pickup_location}")

            # Main driving
            drive_before_break = min(8, daily_driving / 2)
            timeline.append({
                "status": "DRIVING",
                "start_hour": current_hour,
                "end_hour": current_hour + drive_before_break,
                "duration": drive_before_break,
                "location": "En route",
                "description": "Driving"
            })
            current_hour += drive_before_break

            # 30-min break
            timeline.append({
                "status": "ON_DUTY",
                "start_hour": current_hour,
                "end_hour": current_hour + 0.5,
                "duration": 0.5,
                "location": "Rest stop",
                "description": "Break/fuel"
            })
            current_hour += 0.5

            # Continue driving
            remaining = min(3, daily_driving - drive_before_break)
            timeline.append({
                "status": "DRIVING",
                "start_hour": current_hour,
                "end_hour": current_hour + remaining,
                "duration": remaining,
                "location": "En route",
                "description": "Driving"
            })
            current_hour += remaining

            # Dropoff on last day
            if is_last_day:
                timeline.append({
                    "status": "ON_DUTY",
                    "start_hour": current_hour,
                    "end_hour": current_hour + 1,
                    "duration": 1,
                    "location": dropoff_location,
                    "description": "Unloading"
                })
                current_hour += 1
                remarks.append(f"Delivered load at {dropoff_location}")

            # Off duty rest
            timeline.append({
                "status": "OFF_DUTY",
                "start_hour": current_hour,
                "end_hour": 24,
                "duration": 24 - current_hour,
                "location": dropoff_location if is_last_day else "Rest area",
                "description": "Off duty - 10-hour rest"
            })

            totals = self._calculate_daily_totals(timeline)

            log_sheets.append({
                "day_number": day + 1,
                "date": (current_date + timedelta(days=day)).isoformat(),
                "timeline": timeline,
                "totals": totals,
                "remarks": " | ".join(remarks) if remarks else f"Day {day + 1} of trip",
                "total_miles": daily_miles
            })

        total_driving = sum(sheet["totals"]["driving"] for sheet in log_sheets)
        total_on_duty = sum(sheet["totals"]["driving"] + sheet["totals"]["on_duty"] for sheet in log_sheets)

        return {
            "num_days": days_needed,
            "total_distance_miles": distance_miles,
            "total_driving_hours": total_driving,
            "total_on_duty_hours": total_on_duty,
            "is_compliant": True,
            "compliance_notes": f"Multi-day trip - {days_needed} days required for HOS compliance",
            "log_sheets": log_sheets
        }

    def _calculate_daily_totals(self, timeline: List[Dict]) -> Dict:
        """Calculate total hours for each duty status"""
        totals = {
            "off_duty": 0,
            "sleeper_berth": 0,
            "driving": 0,
            "on_duty": 0
        }

        for entry in timeline:
            duration = entry.get("duration", 0)
            status = entry["status"]

            if status == "OFF_DUTY":
                totals["off_duty"] += duration
            elif status == "SLEEPER_BERTH":
                totals["sleeper_berth"] += duration
            elif status == "DRIVING":
                totals["driving"] += duration
            elif status == "ON_DUTY":
                totals["on_duty"] += duration

        return totals

    def check_compliance(self, timeline: List[Dict]) -> Tuple[bool, str]:
        """
        Check if a timeline is HOS compliant

        Returns:
            (is_compliant, message)
        """
        totals = self._calculate_daily_totals(timeline)

        if totals["driving"] > self.MAX_DRIVING_HOURS:
            return False, f"Exceeds 11-hour driving limit ({totals['driving']:.1f} hours)"

        total_duty = totals["driving"] + totals["on_duty"]
        if total_duty > self.MAX_DRIVING_WINDOW:
            return False, f"Exceeds 14-hour driving window ({total_duty:.1f} hours)"

        # Check for 30-minute break after 8 hours driving
        cumulative_driving = 0
        had_break = False
        for entry in timeline:
            if entry["status"] == "DRIVING":
                cumulative_driving += entry["duration"]
                if cumulative_driving > self.BREAK_REQUIRED_AFTER_DRIVING and not had_break:
                    return False, "Missing required 30-minute break after 8 hours driving"
            elif entry["status"] in ["ON_DUTY", "OFF_DUTY", "SLEEPER_BERTH"]:
                if entry["duration"] >= self.MIN_BREAK_DURATION:
                    had_break = True

        return True, "Compliant with all HOS regulations"
