# Create your views here.
import json
from pinterested.data_collector import views as data_collector
from pinterested.sorter import views as sorter
from pinterested.login.models import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
import urllib

def FB_handler(req):
    return render(req, "login/check_login.html")

def error(req):
    return render(req, "login/error.html")

def signup(req):
    try:
        fb_data = json.loads(urllib.unquote_plus(req.POST.get("response")))
        if User.objects.filter(username=fb_data["username"]).count() == 0:
            return render(req, "login/redirecter.html", {"access_token": req.POST.get("access_token"), "response": req.POST.get("response")})
        else:
            user = authenticate(username=fb_data["username"], password="pinterested")
            if user is not None:
                login(req, user)
            return redirect("/")
    except:
        return redirect("/login/error")

def finalizer(req):
    token = req.POST.get("access_token")
    fbdata = json.loads(urllib.unquote_plus(req.POST.get("fb")))

    quora_link = req.POST.get("quora")
    yahoo_link = req.POST.get("ansyahoo")
    quora_username = quora_link.split("/")[3]

    FB_data = data_collector.FBParser(fbdata["username"], token)
    quora_data = data_collector.QuoraParser(quora_username)
    yahoo_data = data_collector.YahooParser(yahoo_link)

    interests = sorter.get_similarity_of_all_topics_and_text(FB_data, quora_data, yahoo_data)

    user = Userdata.create_user(FB_data, quora_username, yahoo_link, interests)

    user = authenticate(username=user.username, password="pinterested")

    login(req, user)

    return redirect("/")


def logout_call(req):
    logout(req)
    return redirect("/")
