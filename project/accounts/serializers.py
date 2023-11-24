from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers, exceptions
from rest_framework.generics import get_object_or_404

from accounts.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128, min_length=8,
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'date_of_birth', 'password')

    def validate(self, attrs):
        if User.objects.filter(email__iexact=attrs['email']).exists():
            raise serializers.ValidationError({'email': "user with this email already exists."})
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = get_object_or_404(User, email=email)
        if not user.check_password(password):
            raise serializers.ValidationError({'message': 'Incorrect Login credentials'})
        if not user.is_active:
            raise serializers.ValidationError({'message': 'Please check your inbox and confirm your email address'})
        attrs['user'] = user
        return attrs


class ConfirmEmailSerializer(serializers.Serializer):
    email_verify_token = serializers.CharField(write_only=True)


class PasswordRecoverySerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        user = get_object_or_404(User, email=email)
        attrs['user'] = user
        return attrs


class SetNewPasswordSerializer(serializers.ModelSerializer):
    uid = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ('uid', 'token', 'password')

    @staticmethod
    def validate_uid_and_token(uid, token):
        def raise_invalid_user_token_error():
            raise exceptions.ValidationError({'message': 'Invalid user or token'}, 400)

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            instance = get_object_or_404(User, id=int(user_id))
            if not default_token_generator.check_token(instance, token):
                raise_invalid_user_token_error()
            return instance
        except (ValueError, TypeError):
            raise_invalid_user_token_error()

    def validate(self, attrs):
        user = self.validate_uid_and_token(attrs['uid'], attrs['token'])
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        user.set_password(validated_data['password'])
        user.save()
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ('old_password', 'new_password')

    def validate(self, attrs):
        old_password = attrs['old_password']
        new_password = attrs['new_password']
        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError({'message': 'Incorrect credentials'})
        if old_password == new_password:
            raise serializers.ValidationError({'message': "Your current password can't be with new password"})
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
