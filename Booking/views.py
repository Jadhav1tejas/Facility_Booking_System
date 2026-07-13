from datetime import timedelta, datetime
from tracemalloc import start
from urllib import request
from .utils import calculate_duration
from django.shortcuts import render
from .models import Booking, Facility, UserProfile, MemberID
from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

# Create your views here.
@login_required
def base(request):
    return render(request, 'base.html')

@login_required
def hall_booking(request):

    facilities = Facility.objects.filter(name__icontains="Hall")

    if request.method == "POST":

        # -----------------------
        # Form Data
        # -----------------------

        facility_id = request.POST.get("facility_id")
        booking_date = request.POST.get("Booking_date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        name = request.POST.get("name")
        mobile = request.POST.get("mobile")

        # -----------------------
        # Validations (Date/Time)
        # -----------------------
        try:
            parsed_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
            if parsed_date < timezone.localtime().date():
                return render(request, "hall.html", {"facilities": facilities, "error": "Cannot book for a past date.", "booking_date": booking_date})
            if parsed_date == timezone.localtime().date():
                parsed_time = datetime.strptime(start_time, "%H:%M").time()
                if parsed_time < timezone.localtime().time():
                    return render(request, "hall.html", {"facilities": facilities, "error": "Cannot book for a past time today.", "booking_date": booking_date})
        except (ValueError, TypeError):
            return render(request, "hall.html", {"facilities": facilities, "error": "Invalid date format. Please use YYYY-MM-DD.", "booking_date": booking_date})
            
        if start_time >= end_time:
            return render(request, "hall.html", {"facilities": facilities, "error": "End time must be after start time.", "booking_date": booking_date})

        if start_time < "08:00" or end_time > "22:00":
            return render(request, "hall.html", {"facilities": facilities, "error": "Hall can only be booked between 08:00 AM and 10:00 PM.", "booking_date": booking_date})

        # -----------------------
        # Duration
        # -----------------------

        duration = calculate_duration(
            start_time,
            end_time
        )

        print(duration)

        # -----------------------
        # Existing Bookings
        # -----------------------

        existing_bookings = Booking.objects.filter(
            facility_id=facility_id,
            booking_date=booking_date
        )

        # -----------------------
        # Validations
        # -----------------------

        for booking in existing_bookings:

            # Overlapping Validation

            if (
                start_time < str(booking.end_time)
                and end_time > str(booking.start_time)
            ):

                return render(
                    request,
                    "hall.html",
                    {
                        "facilities": facilities,
                        "error": "Selected Hall is already booked for this time slot.",
                        "booking_date": booking_date
                    }
                )

            # 1 Hour Gap Validation

            today_date = datetime.today()
            new_start = datetime.combine(today_date, datetime.strptime(start_time, "%H:%M").time())
            new_end = datetime.combine(today_date, datetime.strptime(end_time, "%H:%M").time())
            old_start = datetime.combine(today_date, booking.start_time)
            old_end = datetime.combine(today_date, booking.end_time)

            if new_start < old_end + timedelta(hours=1) and new_end > old_start - timedelta(hours=1):

                return render(
                    request,
                    "hall.html",
                    {
                        "facilities": facilities,
                        "error": "Minimum 1 hour gap is required between bookings.",
                        "booking_date": booking_date
                    }
                )

        # -----------------------
        # Facility Details
        # -----------------------

        facility = Facility.objects.get(
            id=facility_id
        )

        if request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.is_member:
            membership_type = "member"
        else:
            membership_type = "non_member"

        # -----------------------
        # Total Amount
        # -----------------------

        if membership_type == "member":

            total_amount = (
                Decimal(str(duration))
                * facility.member_charge
        )

        else:

            total_amount = (
                Decimal(str(duration))
                * facility.non_member_charge
        )

        print("Duration :", duration)
        print("Total Amount :", total_amount)

        # -----------------------
        # Save Booking
        # -----------------------

        Booking.objects.create(

            facility_id=facility_id,

            booking_date=booking_date,

            start_time=start_time,

            end_time=end_time,

            booking_type="hourly",

            membership_type=membership_type,

            total_amount=total_amount,
            name=name,
            mobile=mobile,
            user=request.user

        )

        # -----------------------
        # Success
        # -----------------------

        return render(
            request,
            "hall.html",
            {
                "facilities": facilities,
                "success": "Hall booked successfully.",
                "facility_name": facility.name,
                "booking_type": "Hourly",
                "booking_date": booking_date,
                "membership_type": membership_type,
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration,
                "total_amount": total_amount,
            }
        )

    return render(
        request,
        "hall.html",
        {
            "facilities": facilities
        }
    )

@login_required
def studio_booking(request):

    facilities = Facility.objects.filter(name__icontains="Studio")

    if request.method == "POST":

        # Form Data
        facility_id = request.POST.get("facility_id")
        booking_date = request.POST.get("Booking_date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        name = request.POST.get("name")
        mobile = request.POST.get("mobile")

        try:
            parsed_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
            if parsed_date < timezone.localtime().date():
                return render(request, "studio.html", {"facilities": facilities, "error": "Cannot book for a past date.", "booking_date": booking_date})
            if parsed_date == timezone.localtime().date():
                parsed_time = datetime.strptime(start_time, "%H:%M").time()
                if parsed_time < timezone.localtime().time():
                    return render(request, "studio.html", {"facilities": facilities, "error": "Cannot book for a past time today.", "booking_date": booking_date})
        except (ValueError, TypeError):
            return render(request, "studio.html", {"facilities": facilities, "error": "Invalid date format. Please use YYYY-MM-DD.", "booking_date": booking_date})
            
        if start_time >= end_time:
            return render(request, "studio.html", {"facilities": facilities, "error": "End time must be after start time.", "booking_date": booking_date})

        if start_time < "08:00" or end_time > "22:00":
            return render(request, "studio.html", {"facilities": facilities, "error": "Studio can only be booked between 08:00 AM and 10:00 PM.", "booking_date": booking_date})
        
        duration = calculate_duration(
        start_time,
        end_time
        )

        print(duration)

        # Existing Bookings
        existing_bookings = Booking.objects.filter(
            facility_id=facility_id,
            booking_date=booking_date
        )

        # Validations
        for booking in existing_bookings:

            # 1. Overlapping Validation
            if (
                start_time < str(booking.end_time)
                and end_time > str(booking.start_time)
            ):

                return render(
                    request,
                    "studio.html",
                    {
                        "facilities": facilities,
                        "error": "Selected Studio is already booked for this time slot.",
                        "booking_date": booking_date
                    }
                )

            # 30 Mins Gap Validation

            today_date = datetime.today()
            new_start = datetime.combine(today_date, datetime.strptime(start_time, "%H:%M").time())
            new_end = datetime.combine(today_date, datetime.strptime(end_time, "%H:%M").time())
            old_start = datetime.combine(today_date, booking.start_time)
            old_end = datetime.combine(today_date, booking.end_time)

            if new_start < old_end + timedelta(minutes=30) and new_end > old_start - timedelta(minutes=30):

                return render(
                    request,
                    "studio.html",
                    {
                        "facilities": facilities,
                        "error": "Minimum 30 minutes gap is required between Studio bookings.",
                        "booking_date": booking_date
                    }
                )
            
        facility = Facility.objects.get(id=facility_id)

        if request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.is_member:
            membership_type = "member"
            charge = facility.member_charge
        else:
            membership_type = "non_member"
            charge = facility.non_member_charge

        total_amount = Decimal(str(duration)) * charge

        # Save Booking
        Booking.objects.create(
            facility_id=facility_id,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,  
            booking_type="hourly",
            membership_type=membership_type,
            total_amount=total_amount,
            name=name,
            mobile=mobile,
            user=request.user
        )

        return render(
            request,
            "studio.html",
            {
                "facilities": facilities,
                "success": "Studio booked successfully.",
                "facility_name": facility.name,
                "booking_type": "Hourly",
                "booking_date": booking_date,
                "membership_type": membership_type,
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration,
                "total_amount": total_amount,

            }
        )

    return render(
        request,
        "studio.html",
        {
            "facilities": facilities
        }
    )

@login_required
def lounge_booking(request):

    facilities = Facility.objects.filter(name__icontains="Lounge")

    if request.method == "POST":

        # ----------------------------
        # Form Data
        # ----------------------------

        facility_id = request.POST.get("facility_id")
        booking_date = request.POST.get("Booking_date")
        booking_type = request.POST.get("booking_type")
        half_day_slot = request.POST.get("half_day_slot")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        name = request.POST.get("name")
        mobile = request.POST.get("mobile")

        try:
            parsed_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
            if parsed_date < timezone.localtime().date():
                return render(request, "lounge.html", {"facilities": facilities, "error": "Cannot book for a past date.", "booking_date": booking_date})
            if parsed_date == timezone.localtime().date() and booking_type == "hourly":
                parsed_time = datetime.strptime(start_time, "%H:%M").time()
                if parsed_time < timezone.localtime().time():
                    return render(request, "lounge.html", {"facilities": facilities, "error": "Cannot book for a past time today.", "booking_date": booking_date})
        except (ValueError, TypeError):
            return render(request, "lounge.html", {"facilities": facilities, "error": "Invalid date format. Please use YYYY-MM-DD.", "booking_date": booking_date})

        # ----------------------------------
        # Half Day Slot sirf Half Day ke liye
        # ----------------------------------

        if booking_type != "half_day":
            half_day_slot = None

        # ----------------------------
        # Half Day
        # ----------------------------

        if booking_type == "half_day":

            if half_day_slot == "morning":

                start_time = "08:00"
                end_time = "14:00"

            else:

                start_time = "15:00"
                end_time = "22:00"

        # ----------------------------
        # Full Day
        # ----------------------------

        elif booking_type == "full_day":

            start_time = "08:00"
            end_time = "22:00"

        # ----------------------------
        # Duration
        # ----------------------------
        
        if booking_type == "hourly" and start_time >= end_time:
            return render(request, "lounge.html", {"facilities": facilities, "error": "End time must be after start time.", "booking_date": booking_date})

        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")

        duration = (end - start).seconds / 3600

        # ----------------------------
# Operating Hours Validation
# ----------------------------

        opening_time = datetime.strptime(
                    "08:00",
                    "%H:%M"
        )

        closing_time = datetime.strptime(
    "22:00",
    "%H:%M"
)

        if start < opening_time or end > closing_time:

            return render(
                 request,
                "lounge.html",
                {
                    "facilities": facilities,
                    "error": "Lounge can only be booked between 08:00 AM and 10:00 PM.",
                    "booking_date": booking_date
                }
    )

        # ----------------------------
        # Overlapping Validation
        # ----------------------------

        existing_bookings = Booking.objects.filter(

            facility_id=facility_id,

            booking_date=booking_date

        )

        for booking in existing_bookings:

            if (

                start_time < str(booking.end_time)

                and end_time > str(booking.start_time)

            ):

                return render(

                    request,

                    "lounge.html",

                    {

                        "facilities": facilities,

                        "error": "Selected Lounge is already booked for this time slot.",
                        "booking_date": booking_date

                    }

                )

        # ----------------------------
        # Facility
        # ----------------------------

        facility = Facility.objects.get(
            id=facility_id
        )

        # ----------------------------
        # Membership
        # ----------------------------

        if request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.is_member:
            membership_type = "member"
        else:
            membership_type = "non_member"

        # ----------------------------
        # Complimentary Booking Check
        # ----------------------------

        free_booking_used = Booking.objects.filter(

            facility__name__icontains="Lounge",

            name=name,

            mobile=mobile,

            is_complimentary=True

        ).exists()

        is_complimentary = False

        # ----------------------------
# Price Calculation
# ----------------------------

        if (

            booking_type == "hourly"

            and duration <= 4

            and not free_booking_used

        ):

            total_amount = Decimal("0.00")

            is_complimentary = True

        else:

            if membership_type == "member":

                charge = facility.member_charge

            else:

                charge = facility.non_member_charge

    # Hourly Pricing

            if booking_type == "hourly":

                total_amount = (

                Decimal(str(duration))

                * charge

            )

    # Half Day Pricing

            elif booking_type == "half_day":

                total_amount = (

                    Decimal("5")

                    * charge

                )

    # Full Day Pricing

            elif booking_type == "full_day":

                total_amount = (

                Decimal("10")

                * charge

            )
        # ----------------------------
        # Save Booking
        # ----------------------------

        Booking.objects.create(

            facility_id=facility_id,

            booking_date=booking_date,

            booking_type=booking_type,

            half_day_slot=half_day_slot,

            membership_type=membership_type,

            total_amount=total_amount,

            start_time=start_time,

            end_time=end_time,

            name=name,

            mobile=mobile,

            is_complimentary=is_complimentary,
            
            user=request.user

        )

        # ----------------------------
        # Success Message
        # ----------------------------

        if is_complimentary:

            success_message = (
                "🎉 Complimentary Lounge Booking Applied! Amount: ₹0"
            )

        else:

            success_message = (
                "✔ Lounge booked successfully."
            )

        return render(

            request,

            "lounge.html",

            {

                "facilities": facilities,

                "success": success_message,

                "membership_type": membership_type,

                "half_day_slot": half_day_slot,

                "total_amount": total_amount,

                "booking_type": booking_type,

                "duration": duration,

                "name": name,

                "mobile": mobile

            }

        )

    return render(
    request,
    "lounge.html",
    {
        "facilities": facilities
    }
)

def login_user(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("/")

        else:

            return render(
                request,
                "login.html",
                {
                    "error": "Invalid Username or Password"
                }
            )

    return render(request, "login.html")

def logout_user(request):

    logout(request)

    return redirect("/login/")

def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        is_member_value = request.POST.get("is_member") == "True"
        member_id_input = request.POST.get("member_id")

        if password != confirm_password:
            return render(request, "register.html", {"error": "Passwords do not match."})

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username is already taken."})
            
        if is_member_value:
            if not member_id_input:
                return render(request, "register.html", {"error": "Member ID is required for members."})
            
            try:
                member_record = MemberID.objects.get(member_id=member_id_input, is_used=False)
            except MemberID.DoesNotExist:
                return render(request, "register.html", {"error": "Invalid or already used Member ID."})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        if is_member_value:
            member_record.is_used = True
            member_record.save()
        
        # Create the UserProfile with membership status
        UserProfile.objects.create(user=user, is_member=is_member_value)
        
        return redirect("/login/")

    return render(request, "register.html")

def check_availability(request):
    facility_id = request.GET.get('facility_id')
    date_str = request.GET.get('date')
    
    if not facility_id or not date_str:
        return JsonResponse({'error': 'Missing facility_id or date'}, status=400)
    
    try:
        facility = Facility.objects.get(id=facility_id)
    except Facility.DoesNotExist:
        return JsonResponse({'error': 'Facility not found'}, status=404)
        
    bookings = Booking.objects.filter(facility_id=facility_id, booking_date=date_str).order_by('start_time')
    
    gap_minutes = 0
    if "hall" in facility.name.lower():
        gap_minutes = 60
    elif "studio" in facility.name.lower():
        gap_minutes = 30
        
    timeline = []
    
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
        
    today_date = timezone.localtime().date()
    current_time = datetime.combine(parsed_date, datetime.strptime("08:00", "%H:%M").time())
    end_of_day = datetime.combine(parsed_date, datetime.strptime("22:00", "%H:%M").time())
    
    if parsed_date == today_date:
        now = timezone.localtime().replace(tzinfo=None)
        if now > current_time:
            current_time = now

    for b in bookings:
        b_start = datetime.combine(parsed_date, b.start_time)
        b_end = datetime.combine(parsed_date, b.end_time)
        
        buffer_start = b_start - timedelta(minutes=gap_minutes) if gap_minutes > 0 else b_start
        
        # 1. Available block before buffer
        if current_time < buffer_start:
            timeline.append({
                'start': current_time.strftime("%I:%M %p"),
                'end': buffer_start.strftime("%I:%M %p"),
                'status': 'Available',
                'icon': '✅'
            })
            current_time = buffer_start
            
        # 1b. Buffer block before booking
        if current_time < b_start:
            actual_buffer_start = max(current_time, buffer_start)
            if actual_buffer_start < b_start:
                timeline.append({
                    'start': actual_buffer_start.strftime("%I:%M %p"),
                    'end': b_start.strftime("%I:%M %p"),
                    'status': 'Buffer',
                    'icon': '⛔'
                })
        
        # 2. Booked block
        actual_b_start = max(current_time, b_start) if current_time > b_start else b_start
        if actual_b_start < b_end:
            timeline.append({
                'start': actual_b_start.strftime("%I:%M %p"),
                'end': b_end.strftime("%I:%M %p"),
                'status': 'Booked',
                'icon': '❌'
            })
            
        current_time = max(current_time, b_end)
        
        # 3. Buffer block
        if gap_minutes > 0:
            buffer_end = current_time + timedelta(minutes=gap_minutes)
            if buffer_end > end_of_day:
                buffer_end = end_of_day
            if current_time < buffer_end:
                timeline.append({
                    'start': current_time.strftime("%I:%M %p"),
                    'end': buffer_end.strftime("%I:%M %p"),
                    'status': 'Buffer',
                    'icon': '⛔'
                })
                current_time = buffer_end
                
    # 4. Remaining available block
    if current_time < end_of_day:
        timeline.append({
            'start': current_time.strftime("%I:%M %p"),
            'end': end_of_day.strftime("%I:%M %p"),
            'status': 'Available',
            'icon': '✅'
        })
        
    return JsonResponse({
        'facility_name': facility.name,
        'date': date_str,
        'timeline': timeline
    })

@login_required
def dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        upcoming_bookings = Booking.objects.filter(
            booking_date__gte=timezone.localtime().date()
        ).order_by('booking_date', 'start_time')
    else:
        upcoming_bookings = Booking.objects.filter(
            user=request.user,
            booking_date__gte=timezone.localtime().date()
        ).order_by('booking_date', 'start_time')
    return render(request, "dashboard.html", {"upcoming_bookings": upcoming_bookings})

@login_required
def get_bookings_api(request):
    if request.user.is_staff or request.user.is_superuser:
        bookings = Booking.objects.all()
    else:
        bookings = Booking.objects.filter(user=request.user)

    events = []
    for b in bookings:
        start_dt = datetime.combine(b.booking_date, b.start_time).isoformat()
        end_dt = datetime.combine(b.booking_date, b.end_time).isoformat()
        
        color = '#3b82f6' # Blue default
        if 'studio' in b.facility.name.lower():
            color = '#8b5cf6' # Purple
        elif 'lounge' in b.facility.name.lower():
            color = '#10b981' # Green

        events.append({
            'id': b.id,
            'title': f"{b.facility.name} - {b.user.username if b.user else b.name or 'Guest'}",
            'start': start_dt,
            'end': end_dt,
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'facility': b.facility.name,
                'user': b.user.username if b.user else b.name or 'Guest',
                'amount': float(b.total_amount),
                'type': b.booking_type,
                'mobile': b.mobile or 'N/A'
            }
        })

    return JsonResponse(events, safe=False)

@login_required
def cancel_booking(request, booking_id):
    if request.method == "POST":
        try:
            if request.user.is_staff or request.user.is_superuser:
                booking = Booking.objects.get(id=booking_id)
            else:
                booking = Booking.objects.get(id=booking_id, user=request.user)
            booking.delete()
            return JsonResponse({"success": True})
        except Booking.DoesNotExist:
            return JsonResponse({"error": "Booking not found or not authorized"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)