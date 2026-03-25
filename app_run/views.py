from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from .models import Run, AthleteInfo
from django.contrib.auth.models import User
from .serializers import RunSerializer, UserSerializer, AthleteInfoSerializer


# Paginations classes
class RunPagination(PageNumberPagination):
    page_size_query_param = 'size'

class UserPagination(PageNumberPagination):
    page_size_query_param = 'size'


# Views
@api_view(['GET'])
def company_details(request):
    details = {'company_name': settings.COMPANY_NAME,
               'slogan': settings.SLOGAN,
               'contacts': settings.CONTACTS}
    return Response(details)


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer
    pagination_class = RunPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']


class StartRunView(APIView):
    def post(self, request, run_id):
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
    def post(self, request, run_id):
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
    pagination_class = UserPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get('type', None)
        if type == 'athlete':
            qs = qs.filter(is_staff=False)
        elif type == 'coach':
            qs = qs.filter(is_staff=True)
        return qs.exclude(is_superuser=True)
    

class AthleteInfoSet(APIView):
    queryset = AthleteInfo.objects.all()
    serializer_class = AthleteInfoSerializer
    
    def put(self, request, user_id):
        athlete = get_object_or_404(User, id=user_id)
        data = request.data
        weight = data.get('weight', None)
        if weight:
            if not weight.isdigit() or not (0 < int(weight) < 900):
                return Response(weight, status=status.HTTP_400_BAD_REQUEST)
        goals = data.get('goals', None)
        athlete_info, created = AthleteInfo.objects.update_or_create(user_id=athlete, defaults={'weight': weight, 'goals': goals})
        return Response(self.serializer_class(athlete_info).data, status=status.HTTP_201_CREATED)

    def get(self, request, user_id):
        athlete = get_object_or_404(User, id=user_id)
        athlete_info, created = AthleteInfo.objects.get_or_create(user_id=athlete, defaults={'weight': None, 'goals': None})
        return Response(self.serializer_class(athlete_info).data)