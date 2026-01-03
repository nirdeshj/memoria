from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Patient, Reminder

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'id')
    search_fields = ('name',)
    list_filter = ('age',)

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'time','repeat_weekly', 'is_sent','is_completed')
    list_filter = ('is_completed', 'time')
    search_fields = ('title', 'patient__name')
    
