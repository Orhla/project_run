from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.filters import SearchFilter
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


class StartRunView(APIView):
    def patch(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        serializer = RunSerializer(run)
        if run.status != 'init':
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = RunSerializer(run, data={'status': 'in_progress'}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        

class StopRunView(APIView):
    def patch(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        serializer = RunSerializer(run)
        if run.status != 'in_progress':
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = RunSerializer(run, data={'status': 'finished'}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get('type', None)
        if type == 'athlete':
            qs = qs.filter(is_staff=False)
        elif type == 'coach':
            qs = qs.filter(is_staff=True)
        return qs.exclude(is_superuser=True)