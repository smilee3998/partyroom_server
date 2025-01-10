from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("", views.PartyRoomImageCoverView)

urlpatterns = [
    path("all/", views.PartyRoomList.as_view(), name='get_all_partyrooms'),
    path("create/", views.PartyRoomCreateView.as_view(), name='create_partyroom'),
    path("detail/<str:uid>", views.PartyRoomUIdDetail.as_view(), name='detail_partyroom'),
    path("filter/", views.PartyRoomFilterView.as_view(), name='filter_partyroom'),
    path('', include(router.urls))
]
