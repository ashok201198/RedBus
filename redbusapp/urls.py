from django.urls import path

from .views.auth import*
from .views.journey import *
from .views.admin import *

app_name = "redbus"

urlpatterns = [
    path('register/', SignupUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutUser, name='logout'),
    path('forgot/',Prereset.as_view(),name='stage1'),
    path('forgot/reset',reset.as_view(),name='stage2'),
    path('reset',changepass.as_view(),name='reset'),
    path('bus/',Get_Journey.as_view(),name='journey'),
    path('add/',admin_add_bus.as_view(),name='add_bus'),
    path('add/<int:pk>/route',admin_add_route.as_view(),name='add_route'),
    path('buses/',Get_buses.as_view(),name='buses'),
    path('seats/',Get_seats.as_view(),name='seats'),
    path('details/',get_details.as_view(),name='details'),
    path('confirmed/',get_ticket.as_view(),name='confirmation'),
    path('booking/',get_bookings.as_view(),name='booking'),
]
