from smtplib import SMTPException

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import BadHeaderError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import exceptions, generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts import serializers, schemas
from accounts.models import User
from accounts.tasks import send_verify_email_task
from core.celery import app


@extend_schema_view(
    post=extend_schema(
        summary="Creating user",
        responses=schemas.REGISTER_POST_RESPONSES,
    ),
)
class RegisterView(generics.CreateAPIView):
    serializer_class = serializers.RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.validated_data
        try:
            send_verify_email_task.delay(user_data['username'], user_data['email'])
        except (BadHeaderError, SMTPException):
            return Response({'message': 'Failed retry after some time'}, status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Confirm the user's email address",
    responses=schemas.VERIFY_EMAIL_POST_RESPONSES
)
class VerifyEmailView(generics.GenericAPIView):
    serializer_class = serializers.VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email_verify_token=serializer.validated_data['email_verify_token'])
        except User.DoesNotExist:
            return Response({'message': 'Invalid activation token'}, status.HTTP_400_BAD_REQUEST)
        if user.is_active:
            Response({'message': 'you have already verified your account'}, status.HTTP_200_OK)
        else:
            user.is_active = True
            user.save()
        return Response({'message': 'Congrats! you just verified your account'}, status.HTTP_201_CREATED)


@extend_schema_view(
    post=extend_schema(
        summary="Get token",
        responses=schemas.LOGIN_RESPONSES,
    ),
)
class LoginView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status.HTTP_201_CREATED)


@extend_schema(
    summary="Delete token",
    responses=schemas.LOGOUT_RESPONSES
)
class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response({'message': 'User Logged out successfully'}, status=status.HTTP_200_OK)


@extend_schema(
    summary="Reset password (send a verification token by email)",
    responses=schemas.PASSWORD_RESET_EMAIL_RESPONSES
)
class PasswordResetEmailView(generics.GenericAPIView):
    serializer_class = serializers.PasswordResetEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        try:
            app.send_task('accounts.tasks.send_reset_password_task', args=(user.username, user.email))
        except (BadHeaderError, SMTPException):
            return Response({'message': 'Failed retry after some time'}, status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'We have sent you a link to reset your password'}, status.HTTP_200_OK)


@extend_schema(
    summary="Reset password done",
    responses=schemas.PASSWORD_RESET_DONE_RESPONSES
)
class PasswordResetDoneView(generics.GenericAPIView):
    serializer_class = serializers.SetNewPasswordSerializer

    def patch(self, request, *args, **kwargs):
        try:
            pk = force_str(urlsafe_base64_decode(request.data['uid']))
            instance = User.objects.get(id=int(pk))
            if not default_token_generator.check_token(instance, request.data['token']):
                raise exceptions.AuthenticationFailed({'message': 'The reset link is invalid'}, 401)
        except User.DoesNotExist:
            raise exceptions.ValidationError({'message': "User doesn't exits"}, 404)
        serializer = self.get_serializer(data=request.data, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


@extend_schema_view(
    put=extend_schema(
        summary="Change password",
        responses=schemas.CHANGE_PASSWORD_RESPONSES),
    patch=extend_schema(exclude=True)
)
class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.ChangePasswordSerializer
