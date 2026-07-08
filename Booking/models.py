from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_member = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - Member: {self.is_member}"

class Facility(models.Model):
    name = models.CharField(max_length=100)
    member_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    non_member_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)

    def __str__(self):
            return self.name

BOOKING_TYPES = (
    ("hourly", "Hourly"),
    ("half_day", "Half Day"),
    ("full_day", "Full Day"),
)
HALF_DAY_SLOTS = (
    ("morning", "Morning"),
    ("evening", "Evening"),
)

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)

    booking_date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    booking_type = models.CharField(
        max_length=20,
        choices=BOOKING_TYPES,
        default="hourly"
    )

    half_day_slot = models.CharField(
    max_length=20,
    choices=HALF_DAY_SLOTS,
    blank=True,
    null=True
    )

    total_amount = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
    )

    membership_type = models.CharField(
    max_length=20,
    choices=[
        ("member", "Member"),
        ("non_member", "Non Member")
    ],
    default="non_member"
    )
    
    name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    mobile = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    is_complimentary = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.facility.name} - {self.booking_date}"