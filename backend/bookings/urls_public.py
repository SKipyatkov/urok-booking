"""Public booking URL routes."""

from django.urls import path

from . import views_public

app_name = "public"

urlpatterns = [
    path("<slug:slug>/book/", views_public.PublicBookView.as_view(), name="book"),
]
