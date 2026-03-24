from rest_framework import serializers
from django.db.models import Count
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Run, AthleteInfo

class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name']


class RunSerializer(serializers.ModelSerializer):
    athlete_data = AthleteSerializer(read_only=True, source='athlete')

    class Meta:
        model = Run
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished']

    def get_type(self, obj):
        if obj.is_staff:
            return 'coach'
        return 'athlete'
    
    def get_runs_finished(self, obj):
        return obj.__class__.objects.select_related('run').values('id').\
            annotate(runs_finished=Count('run', filter=Q(run__status='finished'))).filter(id=obj.id)[0]['runs_finished']
    

class AthleteInfoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AthleteInfo
        fields = '__all__'