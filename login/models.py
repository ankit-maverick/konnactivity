from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# 

class City(models.Model):
    city = models.CharField(max_length=255, unique=True)

    created_at          = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at          = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.city

    __str__ = __unicode__

class AgeRange(models.Model):
    age = models.CharField(max_length=10, unique=True)

    created_at          = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at          = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.age

    __str__ = __unicode__

    @staticmethod
    def get_or_add(min=0, max=1000):
        if min == 0:
            return AgeRange.objects.get_or_create(age=(str(max) + "+"))
        elif max == 1000:
            return AgeRange.objects.get_or_create(age=(">" + str(min)))
        elif min != 0 and max != 1000:
            return AgeRange.objects.get_or_create(age=(str(min) + "-" + str(max)))

class Interest(models.Model):
    interest = models.CharField(max_length=255, unique=True)

    created_at          = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at          = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.interest

    __str__ = __unicode__

    @staticmethod
    def bulk_get_or_create(interests):
        interests = [i.lower() for i in interests]
        all_interests = Interest.objects.filter(interest__in=interests).values_list("interest", flat=True)

        new_interests = [Interest(interest=i) for i in interests if i not in all_interests]

        Interest.objects.bulk_create(new_interests)

        return Interest.objects.filter(interest__in=interests)

class Userdata(models.Model):

    user = models.OneToOneField(User)
    name = models.CharField(max_length=255)
    quora_name = models.CharField(max_length=255)

    ansyahoo = models.CharField(max_length=255)

    CHOICES = (
        (True, "Male"),
        (False, "Female")
    )
    gender = models.BooleanField(choices=CHOICES)
    city = models.ForeignKey(City)
    age = models.ForeignKey(AgeRange)

    interests = models.ManyToManyField(Interest, through="UserInterest")

    created_at          = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at          = models.DateTimeField(auto_now=True, editable=False)

    def widget(self):
        import random
        a = [i.interest for i in self.interests.all()[:2]]
        random_likes = ", ".join(a[:2])
        return '<br><div class="pure-g-r" style="background: #ededed; min-height: 112px"><div class="pure-u-1" style="margin: 4px"><div class="pure-u-1-3"><img src="https://graph.facebook.com/' + self.user.username +'/picture?type=normal" alt=""></div><div class="pure-u-1-2"><br><a href="user/' + str(self.id) + '">' + self.name + '</a><br><small>' + self.city.city + '<br></small>likes ' + random_likes + '</div></div></div>'

    @staticmethod
    def create_user(fb_data, quora_name, yahoo, interests):
        try:
            user = User.objects.create_user(fb_data["username"], fb_data["username"] + "@facebook.com", "pinterested")
        except:
            user = User.objects.get(username=fb_data["username"])
        age_dict = {
                "min": fb_data["age_range"]["min"] if fb_data["age_range"].has_key("min") else 0,
                "max": fb_data["age_range"]["max"] if fb_data["age_range"].has_key("max") else 1000,
            }
        user_data_dict = {
            "user": user,
            "name": fb_data["name"],
            "quora_name": quora_name,
            "gender": True if fb_data["gender"] is "male" else "Female",
            "city": City.objects.get_or_create(city=fb_data["location"]["name"])[0],
            "ansyahoo": yahoo,
            "age": AgeRange.get_or_add(**age_dict)[0]
        }

        userdata = Userdata.objects.create(**user_data_dict)

        saved_interests = Interest.bulk_get_or_create(interests)

        activities = [UserInterest(userdata=userdata, interest=s) for s in saved_interests]

        UserInterest.objects.bulk_create(activities)

        return user

class UserInterest(models.Model):
    interest = models.ForeignKey(Interest)
    userdata = models.ForeignKey(Userdata)

    weight = models.IntegerField(default=1)

    created_at          = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at          = models.DateTimeField(auto_now=True, editable=False)