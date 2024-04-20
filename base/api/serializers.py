from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from ..models import Room, User, Topic, Message


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


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
