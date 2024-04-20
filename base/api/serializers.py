from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from ..models import Room, User, Topic, Message


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class CreateRoomSerializer(ModelSerializer):
    topic = serializers.CharField()

    class Meta:
        model = Room
        fields = ["host", "topic", "name", "description", "participants"]
        extra_kwargs = {
            "description": {"required": False},
            "participants": {"required": False},
        }


class UpdateRoomSerializer(serializers.ModelSerializer):
    topic = serializers.CharField()

    class Meta:
        model = Room
        fields = [
            "id",
            "host",
            "topic",
            "name",
            "description",
            "participants",
            "updated",
            "created",
        ]
        read_only_fields = ["id", "host"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "name", "bio", "AdminAccount", "avatar"]


class UserLoginSerializer(ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            return data
        else:
            raise serializers.ValidationError("Email and password are required.")


class TopicSerializer(ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
