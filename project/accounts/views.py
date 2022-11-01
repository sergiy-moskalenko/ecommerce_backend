from smtplib import SMTPException

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import BadHeaderError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.generics import GenericAPIView, CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.serializers import (
    RegisterSerializer,
    LoginSerializer,
    VerifyEmailSerializer,
    PasswordResetEmailSerializer,
    SetNewPasswordSerializer, ChangePasswordSerializer,
)
from accounts.utils import send_verify_email, send_reset_password


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.validated_data
        try:
            send_verify_email(user_data=user_data)
        except BadHeaderError:
            return Response({'message': 'Failed retry after some time'})
        except SMTPException:
            return Response({'message': 'Failed retry after some time'})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VerifyEmailView(GenericAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email_verify_token=serializer.validated_data['email_verify_token'])
        except User.DoesNotExist:
            return Response('Invalid activation link')
        if user.is_active:
            Response('you have already verified your account')
        else:
            user.is_active = True
            user.save()
        return Response('Congrats! you just verified your account')


class LoginView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response('User Logged out successfully')


class PasswordResetEmailView(GenericAPIView):
    serializer_class = PasswordResetEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        try:
            send_reset_password(user_data=user)
        except BadHeaderError:
            return Response({'message': 'Failed retry after some time'})
        except SMTPException:
            return Response({'message': 'Failed retry after some time'})
        return Response({'message': 'We have sent you a link to reset your password'})


class PasswordResetDoneView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request, *args, **kwargs):
        try:
            print(request.data['uid'])
            pk = force_str(urlsafe_base64_decode(request.data['uid']))
            instance = User.objects.get(id=int(pk))
            if not default_token_generator.check_token(instance, request.data['token']):
                raise AuthenticationFailed('The reset link is invalid', 401)
        except User.DoesNotExist:
            raise ValidationError("User doesn't exits")
        serializer = self.get_serializer(data=request.data, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class ChangePasswordView(UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
