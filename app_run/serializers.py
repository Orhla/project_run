from rest_framework import serializers
from django.db.models import Count
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Run, AthleteInfo, Challenge

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
        # return obj.__class__.objects.select_related('run').values('id').\
        #     annotate(runs_finished=Count('run', filter=Q(run__status='finished'))).filter(id=obj.id)[0]['runs_finished']

        temp_runs_finished = obj.__class__.objects.select_related('run').filter(id=obj.id).filter(run__status='finished').count()
        if temp_runs_finished == 10 and not Challenge.objects.filter(athlete=obj).exists():
            Challenge.objects.create(full_name='Сделай 10 Забегов!', athlete=obj)
        return temp_runs_finished
    
        # return obj.__class__.objects.select_related('run').filter(id=obj.id).filter(run__status='finished').count()
    

class AthleteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AthleteInfo
        fields = '__all__'


class ChallengeSerializer(serializers.ModelSerializer):
    athlete_data = UserSerializer(read_only=True, source='athlete')

    class Meta:
        model = Challenge
        fields = '__all__'

    # def create(self, validated_data):
    #     # finished_runs_count = obj.__class__.objects.select_related('user').filter(runs_finished=10)
    #     finished_runs_count = validated_data.pop('athlete_data')
    #     return Challenge.objects.create(full_name='Сделай 10 Забегов!', athlete=self.athlete_data.id)
    #     print(finished_runs_count)
    #     if self.athlete_data.runs_finished == 10:
    #         challenge = Challenge.objects.create(full_name='Сделай 10 Забегов!', athlete=self.athlete_data.id)
    #         return challenge
        

# class ChallengeForAthleteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Challenge
#         fields = '__all__'