from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("", views.BookingViewSet)

urlpatterns = [
    path('my_booking/<str:uid>', views.BookingDetailView.as_view(), name='my_booking'),
    path('my_bookings/', views.MyBookingListView.as_view(), name='my_bookings'),
    path('', include(router.urls))
]
