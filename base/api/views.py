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
    MessageSerializer,
    RoomSerializerMsg,
)
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from ..models import Room, Topic, Message, User
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
from django.db.models import Count

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


# @api_view(["GET"])
# @authentication_classes([TokenAuthentication])
# def getRoom(request, pk):
#     room = Room.objects.get(id=pk)
#     serializer = RoomSerializer(room, many=False)
#     return Response(
#         {"message": "Room info fetched successfully", "room": serializer.data}
#     )


from .serializers import UserSerializer


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
def getRoom(request, pk):
    try:
        room = Room.objects.get(id=pk)
        messages = Message.objects.filter(room=room)
        message_data = []
        for message in messages:
            # Use the UserSerializer to serialize user data
            user_data = UserSerializer(message.user).data
            message_data.append(
                {
                    "id": message.id,
                    "body": message.body,
                    "user": user_data,
                    "created": message.created,
                    # Include other message fields as needed
                }
            )

        # Serialize host data
        host_data = UserSerializer(room.host).data if room.host else None

        # Serialize participants data
        participants_data = UserSerializer(room.participants.all(), many=True).data

        room_data = {
            "id": room.id,
            "host": host_data,
            "topic": room.topic.name if room.topic else None,
            "name": room.name,
            "description": room.description,
            "participants": participants_data,
            "updated": room.updated,
            "created": room.created,
        }
        return Response(
            {
                "message": "Room info and messages fetched successfully",
                "room": room_data,
                "messages": message_data,
            }
        )
    except Room.DoesNotExist:
        return Response(
            {"message": "Room does not exist"}, status=status.HTTP_404_NOT_FOUND
        )
    except Message.DoesNotExist:
        return Response(
            {"message": "No messages found for this room"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except User.DoesNotExist:
        return Response(
            {"message": "User associated with a message not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def roomCount(request):
    # Get the count of rooms
    count = Room.objects.count()

    # Return the count in the response
    return Response({"room_count": count})

   
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
                user = UserSerializer(user)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "user": user.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def logoutUser(request):
    if request.method == "POST":
        # Logout the user
        logout(request)

        # Clear the refresh token cookie
        response = JsonResponse({"message": "User logged out successfully."})
        response.delete_cookie("refresh_token")

        return response
    else:
        # Return a method not allowed response if the request method is not POST
        return Response(
            {"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )



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
            user.avatar = "https://api.multiavatar.com/" + user.name  # Set the password
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
    refresh_token = request.COOKIES.get("refresh")
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

        # Add the user to the room's participants if not already a participant
        if user not in room.participants.all():
            room.participants.add(user)

        # Get updated room messages and participants
        room_messages = room.message_set.all()
        participants = room.participants.all()

        # Serialize the room messages with the updated MessageSerializer
        message_serializer = MessageSerializer(instance=room_messages, many=True)

        # Serialize the message object separately
        serialized_message = MessageSerializer(instance=message).data

        return Response(
            {
                "success": "Message has been sent",
                "room": RoomSerializer(room).data,
                "room_messages": message_serializer.data,
                "participants": UserSerializer(participants, many=True).data,
                "message": serialized_message,
            },
            status=status.HTTP_200_OK,
        )

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

    print(request.data)
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

    try:
        host = User.objects.get(id=payload["user_id"])
    except User.DoesNotExist:
        return Response(
            {"error": "Host does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )
    print(host)
    print(room.host)
    # Check if the current user is the host of the room
    if host != room.host:
        return Response(
            {"error": "You are not allowed to modify this room."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Update the room fields directly from the request data if they exist
    name = request.data.get("name")
    topic = request.data.get("topic")
    description = request.data.get("description")

    if name:
        room.name = name
    if topic:
        topic_instance, _ = Topic.objects.get_or_create(name=topic)
        room.topic = topic_instance
    if description:
        room.description = description

    # Save the updated room
    room.save()

    # Get participants' data
    participants_data = []
    for participant in room.participants.all():
        participant_data = {
            "id": participant.id,
            "username": participant.username,
            "email": participant.email,
            "name": participant.name,
            "bio": participant.bio,
            "AdminAccount": participant.AdminAccount,
            "avatar": participant.avatar,
        }
        participants_data.append(participant_data)

    # Construct the response
    response_data = {
        "message": "Details updated successfully",
        "room": {
            "id": room.id,
            "host": {
                "id": room.host.id,
                "username": room.host.username,
                "email": room.host.email,
                "name": room.host.name,
                "bio": room.host.bio,
                "AdminAccount": room.host.AdminAccount,
                "avatar": room.host.avatar,
            },
            "topic": {
                "id": room.topic.id if room.topic else None,
                "name": room.topic.name if room.topic else None,
            },
            "name": room.name,
            "description": room.description,
            "participants": participants_data,
            "updated": room.updated,
            "created": room.created,
        },
    }

    return Response(response_data, status=status.HTTP_200_OK)


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
            {"error": "Host does not exist."},
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
            {"error": "Host does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )
    # Check if the current user is the host of the room
    if user != message.user:
        return Response(
            {"error": "You are not allowed to delete this message."},
            status=status.HTTP_403_FORBIDDEN,
        )
    message.delete()
    return Response({"success": "message deleted successfully!"})


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
                    {"error": "Host does not exist."},
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


@api_view(["GET"])
def topicsPage(request):
    try:
        q = request.GET.get("q") if request.GET.get("q") != None else ""
        topics = Topic.objects.filter(name__icontains=q)
        # Count the number of rooms for each topic
        topic_counts = topics.annotate(num_rooms=Count("room"))

        # Create a list of dictionaries containing topic names and their corresponding room counts
        topic_list = [
            {"topic": topic.name, "num_rooms": topic.num_rooms}
            for topic in topic_counts
        ]

        return Response(
            {"message": "Topics fetched successfully", "topics": topic_list}
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # return render(request, "base/topics.html", {"topics": topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return Response({"message": "messages fetched success", "messages": room_messages})
