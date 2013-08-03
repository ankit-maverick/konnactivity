# Create your views here.
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from pinterested.login.models import *

@login_required
def home(req):
    user = req.user
    userdata = Userdata.objects.get(user=user).select_related()


@login_required
def profile(req):
    user = req.user
    userdata = Userdata.objects.select_related().get(user=user)

    return render(req, "home/profile.html", {
        "user": user,
        "userdata": userdata
    })