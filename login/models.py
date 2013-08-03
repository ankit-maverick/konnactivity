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

    CHOICES = (
        (True, "Male"),
        (False, "Female")
    )
    gender = models.BooleanField(choices=CHOICES)
    city = models.ForeignKey(City)
    age = models.ForeignKey(AgeRange)

    interests = models.ManyToManyField(Interest)

    created_at          = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at          = models.DateTimeField(auto_now=True, editable=False)

    @staticmethod
    def create_user(fb_data, quora_name, interests):
        user, flag = User.objects.get_or_create(username=fb_data["username"], password="pinterested")
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
            "age": AgeRange.get_or_add(**age_dict)[0]
        }

        userdata = Userdata.objects.create(**user_data_dict)

        saved_interests = Interest.bulk_get_or_create(interests)

        t = [userdata.interests.add(s) for s in saved_interests]

        return user