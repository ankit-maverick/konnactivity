# Create your views here.
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from pinterested.login.models import *
from pinterested.sorter import views as sorter

@login_required
def home(req):
    user = req.user
    userdata = Userdata.objects.select_related().get(user=user)

    all_users = list(Userdata.objects.select_related().all())
    all_users.remove(userdata)
    score_list = []

    for u in all_users:
        score_list.append(sorter.match_interest_score(userdata.interests.all(), u.interests.all()))

    users = [x.widget() for (y,x) in sorted(zip(score_list,all_users), reverse=True)]

    users = users if len(users) <= 5 else users[:5]

    return render(req, "home/home.html", {
        "user": user,
        "userdata": userdata,
        "users": users
    })


@login_required
def profile(req):
    user = req.user
    userdata = Userdata.objects.select_related().get(user=user)

    return render(req, "home/profile.html", {
        "user": user,
        "userdata": userdata
    })

def user(req, user_id=None):
    if user_id is None:
        return redirect("/profile")

    userdata = Userdata.objects.select_related().get(id=user_id)
    user = userdata.user

    return render(req, "home/profile.html", {
        "user": user,
        "userdata": userdata
    })
