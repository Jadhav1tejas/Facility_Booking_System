from django.contrib import admin
from .models import Facility, Booking, UserProfile, MemberID, CancellationLog


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "member_charge",
        "non_member_charge",
    )
    

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "facility",
        "booking_date",
        "booking_type",
        "half_day_slot",
        "membership_type",
        "total_amount",
        "start_time",
        "end_time",
        "name",
        "mobile",
        "is_complimentary",
    )
    list_filter = (
        "facility",
        "booking_date",
        "booking_type"
    )
    search_fields = (
        "facility__name",
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_member')
    list_filter = ('is_member',)
    search_fields = ('user__username', 'user__email')

@admin.register(MemberID)
class MemberIDAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'is_used')
    list_filter = ('is_used',)
    search_fields = ('member_id',)