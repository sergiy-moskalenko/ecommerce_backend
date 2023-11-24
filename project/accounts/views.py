from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts import serializers, schemas
from accounts.models import User


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
        validated_data = serializer.validated_data
        user = User.objects.create_user(**validated_data)
        user.send_confirm_email()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Confirm the user's email address",
    responses=schemas.VERIFY_EMAIL_POST_RESPONSES
)
class ConfirmEmailView(generics.GenericAPIView):
    serializer_class = serializers.ConfirmEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email_verify_token=serializer.validated_data['email_verify_token'])
        except User.DoesNotExist:
            return Response({'message': 'Invalid activation token'}, status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            user.is_active = True
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        return Response({'token': user.regenerate_auth_token()}, status.HTTP_201_CREATED)


@extend_schema(
    summary="Delete token",
    responses=schemas.LOGOUT_RESPONSES
)
class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    summary="Password recovery",
    responses=schemas.PASSWORD_RESET_EMAIL_RESPONSES
)
class PasswordRecoveryView(generics.GenericAPIView):
    serializer_class = serializers.PasswordRecoverySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.send_password_recovery()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    summary="Set new password",
    responses=schemas.PASSWORD_RESET_DONE_RESPONSES
)
class SetNewPasswordView(generics.GenericAPIView):
    serializer_class = serializers.SetNewPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    put=extend_schema(
        summary="Change password",
        responses=schemas.CHANGE_PASSWORD_RESPONSES),
    patch=extend_schema(exclude=True)
)
class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.ChangePasswordSerializer

    def get_object(self):
        return self.request.user
