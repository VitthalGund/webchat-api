from django.urls import path
from base.api import views
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path("", views.getRoutes),
    path("rooms/", views.getRooms),
    path("count/", views.roomCount),
    path("room/<int:pk>", views.getRoom),
    # path("rooms/<str:pk>/", views.getRoom),
    path("login/", views.login, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.register, name="register"),
    path("", views.home, name="home"),
    path("send/<str:pk>/", views.sendMessage, name="room"),
    path("profile/<str:pk>/", views.userProfile, name="user-profile"),
    path("create-room/", views.createRoom, name="create-room"),
    path("update-room/<str:pk>/", views.updateRoom, name="update-room"),
    path("delete-room/<str:pk>/", views.deleteRoom, name="delete-room"),
    path("delete-message/<str:pk>/", views.deleteMessage, name="delete-message"),
    path("update-user/", views.updateUser, name="update-user"),
    path("topics/", views.topicsPage, name="topics"),
    path("activity/", views.activityPage, name="activity"),
]
