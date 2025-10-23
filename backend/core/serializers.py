from rest_framework import serializers
from .models import Election, Candidate, Vote, FraudReport

class CandidateSerializer(serializers.ModelSerializer):
    poster_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'vision', 'poster_url']
    
    def get_poster_url(self, obj):
        request = self.context.get('request')
        if obj.poster:
            if request:
                return request.build_absolute_uri(obj.poster.url)
            return obj.poster.url
        return obj.poster_url or ''

class CandidateAdminCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'election', 'name', 'vision', 'poster', 'poster_url']
        extra_kwargs = {
            'poster': {'required': False},
            'poster_url': {'required': False}
        }

class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = ['id', 'year', 'start_date', 'end_date', 'is_open', 'show_results']

class ResultSerializer(serializers.Serializer):
    candidate_id = serializers.IntegerField()
    candidate_name = serializers.CharField()
    votes = serializers.IntegerField()

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'election', 'candidate', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']

class FraudReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudReport
        fields = ['id', 'name', 'email', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

class ElectionAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = ['year', 'start_date', 'end_date', 'is_open', 'show_results']

class CandidateAdminCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'election', 'name', 'vision', 'poster_url']
