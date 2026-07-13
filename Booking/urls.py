from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='base'),
    path('hall/', views.hall_booking, name='hall'),
    path('studio/', views.studio_booking, name='studio'),
    path('lounge/', views.lounge_booking, name='lounge'),
    path('api/bookings/', views.get_bookings_api, name='get_bookings_api'),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register_user, name="register"),
    path("api/availability/", views.check_availability, name="check_availability"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("cancel_booking/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
]