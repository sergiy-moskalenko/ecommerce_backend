from drf_spectacular.utils import OpenApiResponse, OpenApiExample, inline_serializer

from accounts import serializers

# RESPONSES

properties_msg = {'message': {'type': 'string'}}

REGISTER_POST_RESPONSES = {
    201: serializers.RegisterSerializer(),
    400: OpenApiResponse(description='Bad request (something invalid)',
                         response=inline_serializer(
                             name='register_msg',
                             fields={
                                 'message': serializers.serializers.CharField()
                             },
                         ),
                         examples=[
                             OpenApiExample(
                                 name="Bad request 1",
                                 value={'message': 'Failed retry after some time'},
                             ),
                             OpenApiExample(
                                 name="Bad request 2",
                                 value={'email': "Email fields didn't match."},
                             ),
                         ]),
}

VERIFY_EMAIL_POST_RESPONSES = {
    200: {
        'properties': properties_msg,
        'example': {'message': 'you have already verified your account'}
    },
    201: {
        'properties': properties_msg,
        'example': {'message': 'Congrats! you just verified your account'}
    },
    400: {
        'properties': properties_msg,
        'example': {'message': 'Invalid activation token'}
    },
}

LOGIN_RESPONSES = {
    201: {
        'properties': {'token': {'type': 'string'}},
        'example': {'token': 'af4e8dfb16c8fba49ada96ef48e1f7a287cada99'}
    },
    400: OpenApiResponse(description='Bad request (something invalid)',
                         response=inline_serializer(
                             name='login_msg',
                             fields={
                                 'message': serializers.serializers.CharField()
                             },
                         ),
                         examples=[
                             OpenApiExample(
                                 name="Bad request 1",
                                 value={'email': "User with this email doesn't exits"},
                             ),
                             OpenApiExample(
                                 name="Bad request 2",
                                 value={'message': "Incorrect Login credentials"},
                             ),
                             OpenApiExample(
                                 name="Bad request 3",
                                 value={'message': "Please check your inbox and verify your email address"},
                             ),
                         ]),
}

LOGOUT_RESPONSES = {
    200: {
        'properties': properties_msg,
        'example': {'message': 'User Logged out successfully'}
    },
}

PASSWORD_RESET_EMAIL_RESPONSES = {
    200: {
        'properties': properties_msg,
        'example': {'message': 'We have sent you a link to reset your password'}
    },
    400: OpenApiResponse(description='Bad request (something invalid)',
                         response=inline_serializer(
                             name='password_reset_email_msg',
                             fields={
                                 'message': serializers.serializers.CharField()
                             },
                         ),
                         examples=[
                             OpenApiExample(
                                 name="Bad request 1",
                                 value={'message': 'Failed retry after some time'},
                             ),
                             OpenApiExample(
                                 name="Bad request 2",
                                 value={'email': "User with this email doesn't exits"},
                             ),
                         ]),
}

PASSWORD_RESET_DONE_RESPONSES = {
    200: {
        'properties': {'success': {'type': 'bool'}, 'message': {'type': 'string'}},
        'example': {'success': True, 'message': 'Password reset success'}
    },
    400: {
        'properties': properties_msg,
        'example': {'message': 'Failed retry after some time'}
    },
    401: {
        'properties': properties_msg,
        'example': {'message': 'The reset link is invalid'}
    },
    404: {
        'properties': properties_msg,
        'example': {'message': "User doesn't exits"}
    },
}

CHANGE_PASSWORD_RESPONSES = {
    201: serializers.ChangePasswordSerializer(),
    400: OpenApiResponse(description='Bad request (something invalid)',
                         response=inline_serializer(
                             name='change_password_msg',
                             fields={
                                 'message': serializers.serializers.CharField()
                             },
                         ),
                         examples=[
                             OpenApiExample(
                                 name="Bad request 1",
                                 value={'message': 'Incorrect credentials'},
                             ),
                             OpenApiExample(
                                 name="Bad request 2",
                                 value={'message': "Your current password can't be with new password"},
                             ),
                         ]),
}
