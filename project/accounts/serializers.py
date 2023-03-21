import uuid

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=6,
                                     write_only=True,
                                     style={'input_type': 'password'},
                                     trim_whitespace=False,
                                     validators=[validate_password])

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'date_of_birth', 'password')

    def validate(self, attrs):
        if User.objects.filter(email__iexact=attrs['email']).exists():
            raise serializers.ValidationError({'email': "Email fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            date_of_birth=validated_data['date_of_birth'],
            email_verify_token=str(uuid.uuid4()),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


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
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': "User with this email doesn't exits"})
        if not user.check_password(password):
            raise serializers.ValidationError({'message': 'Incorrect Login credentials'})
        if not user.is_active:
            raise serializers.ValidationError({'message': 'Please check your inbox and verify your email address'})
        attrs['user'] = user
        return attrs


class VerifyEmailSerializer(serializers.Serializer):
    email_verify_token = serializers.CharField(write_only=True)


class PasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': "User with this email doesn't exits"})
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

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


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
