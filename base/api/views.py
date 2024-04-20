from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from dotenv import load_dotenv
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    RoomSerializer,
    UserSerializer,
    UserLoginSerializer,
    CreateRoomSerializer,
    UpdateRoomSerializer,
)
from base.api import serializers
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from ..models import Room, Topic, Message, User
from base.forms import RoomForm, UserForm, MyUserCreationForm
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import InvalidToken
from django.shortcuts import get_object_or_404
import jwt
import os
from dotenv import load_dotenv

load_dotenv()


@api_view(["GET"])
def getRoutes(request):
    routes = ["GET /api", "GET /api/rooms", "GET /api/rooms/:id"]
    return Response(routes)


@api_view(["GET"])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)

    # @api_view(["POST"])
    # def login(request):
    # if request.COOKIES["refresh"]:
    #     return Response(
    #         {"messsage": "You are already login!"}, status=status.HTTP_202_ACCEPTED
    #     )

    if request.method == "POST":
        email = request.data.get("email").lower()
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email, password=password)
        except:
            return Response(
                {"error": "invalidate credentials!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user)
            response = Response()
            response.set_cookie("refresh", str(refresh))
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "invalidate credentials!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    # context = {"page": page}
    # return render(request, "base/login_register.html", context)


@api_view(["POST"])
def login(request):
    if request.method == "POST":
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            user = authenticate(request._request, username=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response(
                    {"refresh": str(refresh), "access": str(refresh.access_token)},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def logoutUser(request):
    logout(request)
    return redirect("home")


# @api_view(["POST"])
# def register(request):
#     if request.method == "POST":
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             login(
#                 request, serializer.data
#             )  # Change serializers.data to serializer.data
#             refresh = RefreshToken.for_user(
#                 serializer.data
#             )  # Change serializers.data to serializer.data
#             serializer = UserSerializer(serializers.data)
#             response = Response()
#             response.set_cookie("refresh", str(refresh))
#             return Response(
#                 {
#                     "refresh": str(refresh),
#                     "access": str(refresh.access_token),
#                     "user": serializer.data,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         # form = MyUserCreationForm(request.POST)
#         # print(request.POST)
#         # if form.is_valid():
#         #     user = form.save(commit=False)
#         #     user.username = user.username.lower()
#         #     user.save()
#         #
#         # else:
#         #     # print(form.error_messages)
#         #     # messages.error(request, "An error occurred during registration")
#         #     return JsonResponse({"error": "invalidate credentials!"})

#     # return render(request, "base/login_register.html", {"form": form})


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)  # This should work now
        return Response({"token": token.key, "user_id": user.pk, "email": user.email})


@api_view(["POST"])
def register(request):
    if request.method == "POST":
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data.get("password"))  # Set the password
            user.save()
            # login(request, user)  # Removed this line
            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user)
            response = Response()
            response.set_cookie("refresh", str(refresh))
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def refresh_token(request):
    refresh_token = request.COOKIES.get("refresh_token")
    if refresh_token:
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access_token": access_token}, status=status.HTTP_200_OK)
        except:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    else:
        return Response(
            {"error": "Refresh token not found in cookies"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
def home(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[0:3]

    return Response(
        {
            "rooms": rooms,
            "topics": topics,
            "room_count": room_count,
            "room_messages": room_messages,
        },
        status=status.HTTP_200_OK,
    )


from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
def sendMessage(request, pk):
    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "POST":
        # Get user ID from request data
        user_id = request.data.get("user_id")

        # Retrieve user object using the user ID
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Get message body from request data
        body = request.data.get("body")

        # Create the message
        message = Message.objects.create(user=user, room=room, body=body)

        # Add the user to the room's participants
        room.participants.add(user)

        # Get updated room messages and participants
        room_messages = room.message_set.all()
        participants = room.participants.all()

        return Response(
            {
                "room": room,
                "room_messages": room_messages,
                "participants": participants,
                "message": message,
            },
            status=status.HTTP_200_OK,
        )


# @api_view(["GET"])
# def userProfile(request, pk):
#     user = User.objects.get(id=pk)
#     rooms = user.room_set.all()
#     room_messages = user.message_set.all()
#     topics = Topic.objects.all()
#     return Response(
#         {
#             "user": user,
#             "rooms": rooms,
#             "room_messages": room_messages,
#             "topics": topics,
#         },
#         status=status.HTTP_200_OK,
#     )


@api_view(["GET"])
def userProfile(request, pk):
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    data = {
        "user": serializer.data,
        "rooms": rooms,
        "room_messages": room_messages,
        "topics": topics,
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
def createRoom(request):
    if request.method != "POST":
        return Response(
            {"message": "You are not allowed."},
            status=status.HTTP_403_FORBIDDEN,
        )

    host_id = request.data.get("host")
    if host_id is None:
        return Response(
            {"message": "Host id is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        host = User.objects.get(id=host_id)
    except User.DoesNotExist:
        return Response(
            {"message": "Host does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not host.AdminAccount:
        return Response(
            {"message": "Only Admins are allowed to create Rooms."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    serializer = CreateRoomSerializer(data=request.data)
    if serializer.is_valid():
        topic_name = request.data.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        new_room_data = {
            "host": host,
            "topic": topic,
            "name": request.data.get("name"),
            "description": request.data.get("description", ""),
        }

        new_room = Room.objects.create(**new_room_data)

        return Response(
            {
                "message": "Room created Successfully",
                "room": {
                    "id": new_room.id,
                    "host": new_room.host.id,
                    "topic": new_room.topic.id,
                    "name": new_room.name,
                    "description": new_room.description,
                },
            },
            status=status.HTTP_201_CREATED,
        )
    else:
        return Response(
            {"error": serializer.error_messages}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["PUT"])
@authentication_classes([TokenAuthentication])
def updateRoom(request, pk):
    room = get_object_or_404(Room, pk=pk)
    token = request.headers.get("Authorization").replace("Bearer ", "")
    payload = jwt.decode(
        token, verify=False, algorithms="HS256", key=os.getenv("screct")
    )
    print(payload["user_id"])
    try:
        host = User.objects.get(id=payload["user_id"])
    except User.DoesNotExist:
        return Response(
            {"message": "Host does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )
    # Check if the current user is the host of the room
    if host != room.host:
        return Response(
            {"message": "You are not allowed to modify this room."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Proceed with the update if the user is the host
    serializer = UpdateRoomSerializer(room, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # If topic is provided in the request data, create the topic if it doesn't exist
    topic_name = serializer.validated_data.get("topic")
    if topic_name:
        topic, created = Topic.objects.get_or_create(name=topic_name)
        if created:
            # Update the topic field in the serializer data with the newly created topic
            serializer.validated_data["topic"] = topic

    serializer.save()
    return Response(
        {"message": "Details updated successfully", "room": serializer.data},
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
def deleteRoom(request, pk):
    try:
        room = Room.objects.get(pk=pk)
    except Room.DoesNotExist:
        return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

    token = request.headers.get("Authorization").replace("Bearer ", "")
    payload = jwt.decode(
        token, verify=False, algorithms="HS256", key=os.getenv("screct")
    )
    print(payload["user_id"])
    try:
        host = User.objects.get(id=payload["user_id"])
    except User.DoesNotExist:
        return Response(
            {"message": "Host does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if host != room.host:
        return Response(
            {"error": "You are not allowed to delete this room"},
            status=status.HTTP_403_FORBIDDEN,
        )

    room.delete()
    return Response(
        {"message": "Room deleted successfully"}, status=status.HTTP_204_NO_CONTENT
    )


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    token = request.headers.get("Authorization").replace("Bearer ", "")
    payload = jwt.decode(
        token, verify=False, algorithms="HS256", key=os.getenv("screct")
    )
    # print(payload["user_id"])
    try:
        user = User.objects.get(id=payload["user_id"])
    except User.DoesNotExist:
        return Response(
            {"message": "Host does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )
    # Check if the current user is the host of the room
    if user != message.user:
        return Response(
            {"message": "You are not allowed to delete this message."},
            status=status.HTTP_403_FORBIDDEN,
        )
    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": message})


@authentication_classes([TokenAuthentication])
def updateUser(request):
    user_data = request.data

    if request.method == "PUT":
        try:
            # Decode JWT token to get user information
            token = request.headers.get("Authorization").replace("Bearer ", "")
            payload = jwt.decode(
                token, verify=False, algorithms="HS256", key=os.getenv("screct")
            )
            # print(payload["user_id"])
            try:
                user = User.objects.get(id=payload["user_id"])
            except User.DoesNotExist:
                return Response(
                    {"message": "Host does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Check if the decoded user's email matches the email provided in the request data
            if user != user_data.get("email"):
                return Response(
                    {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
                )

            # Update user's details
            serializer = UserSerializer(user, data=user_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except InvalidToken:
            return Response(
                {"error": "Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED
            )

    return Response(
        {"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )

    # user = request.user
    # form = UserForm(instance=user)

    # if request.method == "POST":
    #     form = UserForm(request.POST, request.FILES, instance=user)
    #     if form.is_valid():
    #         form.save()
    #         return redirect("user-profile", pk=user.id)

    # return render(request, "base/update-user.html", {"form": form})


def topicsPage(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(name__icontains=q)
    return Response({"message": "topics fetched success", "topics": topics})
    # return render(request, "base/topics.html", {"topics": topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return Response({"message": "messages fetched success", "messages": room_messages})
