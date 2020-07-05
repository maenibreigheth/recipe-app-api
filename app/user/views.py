from rest_framework import generics
from .serializers import UserSerializer, AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


class CreateUserView(generics.CreateAPIView):
    '''
        View to create a new user
    '''
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    '''
        View to create a new auth token for the user
    '''

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
