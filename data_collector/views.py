# Create your views here.
import urllib2
from BeautifulSoup import BeautifulSoup
import json

def QuoraParser(quora_username):
    # start loading topics
    # 
    browser = urllib2.urlopen("https://www.quora.com/" + quora_username +"/topics")
    soup = BeautifulSoup(browser.read())
    topics = [a.text for a in soup.findAll("a", {"class": "topic_name"})]

    # end of loading topics
    # start loading questions
    
    browser = urllib2.urlopen("https://www.quora.com/" + quora_username + "/questions")
    soup = BeautifulSoup(browser.read())
    questions = soup.findAll("a", {"class": "question_link"})

    question_text = [a.text for a in questions]
    questions_links = ["http://www.quora.com" + a.attrs[5][1] for a in questions]


    browser = urllib2.urlopen("https://www.quora.com/" + quora_username + "/answers")
    soup = BeautifulSoup(browser.read())
    questions = soup.findAll("a", {"class": "question_link"})

    question_text += [a.text for a in questions]
    questions_links += ["http://www.quora.com" + a.attrs[5][1] for a in questions]

    answer_text = [a.text for a in soup.findAll("div", {"class": "answer_content"})]

    sub_topics = []
    for link in questions_links:
        browser = urllib2.urlopen("https://www.quora.com/" + quora_username +"/topics")
        soup = BeautifulSoup(browser.read())
        sub_topics += [a.text for a in soup.findAll("a", {"class": "topic_name"})]

    return {
        "followed_topics": list(set(topics)),
        "questions": list(set(question_text)),
        "answers": list(set(answer_text)),
        "sub_topics": list(set(sub_topics)),
    }


def FBParser(fb_username_or_id, access_token):
    url = "https://graph.facebook.com/" + fb_username_or_id + "?fields=id,name,username,likes.limit(10000),location,age_range,gender&access_token=" + access_token

    browser = urllib2.urlopen(url)
    return json.loads(browser.read())

def YahooParser(yahoo_link):
    username = yahoo_link.split("show=")[1].split("&")[0]

    link = "http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20answers.getbyuser%20where%20user_id%3D%22" + username + "%22&format=json&diagnostics=true&callback=cbfunc"

    browser = urllib2.urlopen(link)
    return json.loads(browser.read()[7:-2])