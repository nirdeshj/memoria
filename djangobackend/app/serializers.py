
from rest_framework import serializers
from .models import Patient, Reminder

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    reminders = ReminderSerializer(many=True, read_only=True)
    
    class Meta:
        model = Patient
        fields = '__all__'
