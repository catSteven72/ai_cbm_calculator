from django.urls import path

from .views import ProcessFormAPI

urlpatterns = [
    path('process/', ProcessFormAPI.as_view(), name="process_form")
]