# Create your views here.
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from pinterested.login.models import *
from pinterested.sorter import views as sorter
from django.http import HttpResponse
import json

@login_required
def home(req):
    user = req.user
    userdata = Userdata.objects.select_related().get(user=user)
    all_interests = Interest.objects.order_by("interest").all()

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
        "users": users,
        "all_interests": all_interests
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

@login_required
def find(req):
    active_userdata = Userdata.objects.select_related().get(user=req.user)
    f1 = req.POST.get("field1")
    f2 = req.POST.get("field2")
    f3 = req.POST.get("field3")

    users1 = list(Userdata.objects.select_related().filter(interests__interest=f1)) if f1 != "" else []
    users2 = list(Userdata.objects.select_related().filter(interests__interest=f2)) if f1 != "" else []
    users3 = list(Userdata.objects.select_related().filter(interests__interest=f3)) if f1 != "" else []

    all_users = users1 + users2 + users3

    if len(all_users) > 0:
        users = []
        frequency = []

        for u in all_users:
            if u == active_userdata:
                continue
            if u in users:
                ind = users.index(u)
                frequency[ind] += 1
            else:
                users.append(u)
                frequency.append(1)

        sorted_users = [x.small_widget() for (y,x) in sorted(zip(frequency,users), reverse=True)]
        return HttpResponse(json.dumps({"results": sorted_users}), mimetype="application/json")
    else:
        return HttpResponse(json.dumps({"results": []}), mimetype="application/json")
