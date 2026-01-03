from django.urls import path,include
from . import views
from .views import PatientAPIView


urlpatterns=[
    path('',views.home,name='home'),
    path('camera/',views.camera,name='camera'),
    path('patient/',PatientAPIView.as_view()),
    path('check-reminder/', views.check_reminder, name='check_reminder'),
    path('camera/video_feed/', views.video_feed, name='video_feed')
]