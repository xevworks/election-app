from rest_framework import serializers
from .models import Election, Candidate, Vote, FraudReport

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'vision', 'poster_url']

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
