# Create your views here.
import json
from pinterested.data_collector import views as data_collector
from pinterested.sorter import views as sorter
from pinterested.login.models import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def FB_handler(req):
    try:
        if req.GET.get("error"):
            return render(req, "login/error.html")
        else:
            return render(req, "login/redirecter.html")
    except:
        return render(req, "login/redirecter.html")


def finalizer(req):
    token = req.POST.get("token")
    fbdata = json.loads(req.POST.get("fb"))
    quora_link = req.POST.get("quora")
    quora_username = quora_link.split("/")[3]

    FB_data = data_collector.FBParser(fbdata["username"], token)
    quora_data = data_collector.QuoraParser(quora_username)

    interests = sorter.sorter(FB_data, quora_data)

    user = Userdata.create_user(FB_data, quora_username, interests)

    login(req, user)

    return render(req, "empty.html")

