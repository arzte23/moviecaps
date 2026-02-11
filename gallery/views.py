from django.shortcuts import render

from .models import Screencap


def home(request):
    screencaps = Screencap.objects.select_related("title").all()
    return render(request, "gallery/home.html", {"screencaps": screencaps})
