from django.urls import path
from . import views

urlpatterns = [
    path("<str:party_room_id>", views.PartyRoomReviewListView.as_view(), name="get_review_from_party_room"),
    path("create/", views.PartyRoomCreateReviewView.as_view(), name="create_review"),
]