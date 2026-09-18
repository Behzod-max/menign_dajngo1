from rest_framework import serializers
from .models import Izoh, Post, Profil
from django.contrib.auth.models import User

class PostSerializer(serializers.ModelSerializer):
    muallif_ismi = serializers.CharField(source='muallif.username', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'sarlavha',
            'matn',
            'muallif',
            'muallif_ismi',
            'rasm',
            'yaratilgan_sana',
            'yangilangan_sana',
            'nashr_etilgan',
            'korildi'
        ]
        read_only_fields = [
            'id',
            'muallif',
            'yaratilgan_sana',
            'yangilangan_sana',
            'korildi',
        ]


class IzohSerializer(serializers.ModelSerializer):
    class Meta:
        model = Izoh
        fields = '__all__'


class PostBatafsilSerializer(serializers.ModelSerializer):
    izohlar = IzohSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = '__all__'


class ProfilSerializer(serializers.ModelSerializer):
    foydalanuvchi_ismi = serializers.CharField(
        source='foydalanuvchi.username',
        read_only=True,
    )

    class Meta:
        model = Profil
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)


class TokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    user_id = serializers.IntegerField()
    username = serializers.CharField()


class MessageResponseSerializer(serializers.Serializer):
    xabar = serializers.CharField()