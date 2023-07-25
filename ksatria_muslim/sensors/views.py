from django.shortcuts import render


def water_control(request):
    return render(request, "sensors/index.html")
