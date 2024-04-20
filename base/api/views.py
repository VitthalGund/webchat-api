from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework import status
from .serializers import RoomSerializer, UserSerializer, UserLoginSerializer
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


@api_view(["GET"])
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user, room=room, body=request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)

    return Response(
        {
            "room": room,
            "room_messages": room_messages,
            "participants": participants,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    return Response(
        {
            "user": user,
            "rooms": rooms,
            "room_messages": room_messages,
            "topics": topics,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
# @login_required(login_url="login")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST" and request.user.AdminAccount == True:
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        return redirect("home")

    context = {"form": form, "topics": topics}
    return render(request, "base/room_form.html", context)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse("Your are not allowed here!!")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")

    context = {"form": form, "topics": topics, "room": room}
    return render(request, "base/room_form.html", context)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("Your are not allowed here!!")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": room})


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("Your are not allowed here!!")

    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": message})


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)

    return render(request, "base/update-user.html", {"form": form})


def topicsPage(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, "base/topics.html", {"topics": topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, "base/activity.html", {"room_messages": room_messages})
