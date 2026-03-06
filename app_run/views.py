from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from django.conf import settings
from .models import Run
from django.contrib.auth.models import User
from .serializers import RunSerializer, UserSerializer

# Create your views here.
@api_view(['GET'])
def company_details(request):
    details = {'company_name': settings.COMPANY_NAME,
               'slogan': settings.SLOGAN,
               'contacts': settings.CONTACTS}
    return Response(details)


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get('type', None)
        if type == 'athlete':
            qs = qs.filter(is_staff=False)
        elif type == 'coach':
            qs = qs.filter(is_staff=True)
        return qs.exclude(is_superuser=True)