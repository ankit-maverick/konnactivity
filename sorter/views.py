#buildkeywords.py
import json
# import sys
from topia.termextract import tag
from topia.termextract import extract

#set path=%path%;c:python27
#http://pypi.python.org/pypi/topia.termextract
#http://www.peterbe.com/plog/uniqifiers-benchmark

######################## Get Wiki Summary ###########################

from sets import Set
import urllib
import urllib2
from bs4 import BeautifulSoup
import re
import yaml
 
class Wiki2Plain:
    def __init__(self, wiki):
        self.wiki = wiki
       
        self.text = wiki
        self.text = self.unhtml(self.text)
        self.text = self.unwiki(self.text)
        self.text = self.punctuate(self.text)
   
    def __str__(self):
        return self.text
   
    def unwiki(self, wiki):
        """
       Remove wiki markup from the text.
       """
        wiki = re.sub(r'(?i)\{\{IPA(\-[^\|\{\}]+)*?\|([^\|\{\}]+)(\|[^\{\}]+)*?\}\}', lambda m: m.group(2), wiki)
        wiki = re.sub(r'(?i)\{\{Lang(\-[^\|\{\}]+)*?\|([^\|\{\}]+)(\|[^\{\}]+)*?\}\}', lambda m: m.group(2), wiki)
        wiki = re.sub(r'\{\{[^\{\}]+\}\}', '', wiki)
        wiki = re.sub(r'(?m)\{\{[^\{\}]+\}\}', '', wiki)
        wiki = re.sub(r'(?m)\{\|[^\{\}]*?\|\}', '', wiki)
        wiki = re.sub(r'(?i)\[\[Category:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'(?i)\[\[Image:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'(?i)\[\[File:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'\[\[[^\[\]]*?\|([^\[\]]*?)\]\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r'\[\[([^\[\]]+?)\]\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r'\[\[([^\[\]]+?)\]\]', '', wiki)
        wiki = re.sub(r'(?i)File:[^\[\]]*?', '', wiki)
        wiki = re.sub(r'\[[^\[\]]*? ([^\[\]]*?)\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r"''+", '', wiki)
        wiki = re.sub(r'(?m)^\*$', '', wiki)
       
        return wiki
   
    def unhtml(self, html):
        """
       Remove HTML from the text.
       """
        html = re.sub(r'(?i)&nbsp;', ' ', html)
        html = re.sub(r'(?i)<br[ \\]*?>', '\n', html)
        html = re.sub(r'(?m)<!--.*?--\s*>', '', html)
        html = re.sub(r'(?i)<ref[^>]*>[^>]*<\/ ?ref>', '', html)
        html = re.sub(r'(?m)<.*?>', '', html)
        html = re.sub(r'(?i)&amp;', '&', html)
       
        return html
   
    def punctuate(self, text):
        """
       Convert every text part into well-formed one-space
       separate paragraph.
       """
        text = re.sub(r'\r\n|\n|\r', '\n', text)
        text = re.sub(r'\n\n+', '\n\n', text)
       
        parts = text.split('\n\n')
        partsParsed = []
       
        for part in parts:
            part = part.strip()
           
            if len(part) == 0:
                continue
           
            partsParsed.append(part)
       
        return '\n\n'.join(partsParsed)
   
    def image(self):
        """
       Retrieve the first image in the document.
       """
        # match = re.search(r'(?i)\|?\s*(image|img|image_flag)\s*=\s*(<!--.*-->)?\s*([^\\/:*?<>"|%]+\.[^\\/:*?<>"|%]{3,4})', self.wiki)
        match = re.search(r'(?i)([^\\/:*?<>"|% =]+)\.(gif|jpg|jpeg|png|bmp)', self.wiki)
       
        if match:
            return '%s.%s' % match.groups()
       
        return None
 
#################################################################################################################33
 
class WikipediaError(Exception):
    pass
 
class Wikipedia:
    url_article = 'http://%s.wikipedia.org/w/index.php?action=raw&title=%s'
    url_image = 'http://%s.wikipedia.org/w/index.php?title=Special:FilePath&file=%s'
    url_search = 'http://%s.wikipedia.org/w/api.php?action=query&list=search&srsearch=%s&sroffset=%d&srlimit=%d&format=yaml'
   
    def __init__(self, lang):
        self.lang = lang
   
    def __fetch(self, url):
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
       
        try:
            result = urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            raise WikipediaError(e.code)
        except urllib2.URLError, e:
            raise WikipediaError(e.reason)
       
        return result
   
    def article(self, article):
        url = self.url_article % (self.lang, urllib.quote_plus(article))
        content = self.__fetch(url).read()
       
        if content.upper().startswith('#REDIRECT'):
            match = re.match('(?i)#REDIRECT \[\[([^\[\]]+)\]\]', content)
           
            if not match == None:
                return self.article(match.group(1))
           
            raise WikipediaError('Can\'t found redirect article.')
       
        return content
   
    def image(self, image, thumb=None):
        url = self.url_image % (self.lang, image)
        result = self.__fetch(url)
        content = result.read()
       
        if thumb:
            url = result.geturl() + '/' + thumb + 'px-' + image
            url = url.replace('/commons/', '/commons/thumb/')
            url = url.replace('/' + self.lang + '/', '/' + self.lang + '/thumb/')
           
            return self.__fetch(url).read()
       
        return content
   
    def search(self, query, page=1, limit=10):
        offset = (page - 1) * limit
        url = self.url_search % (self.lang, urllib.quote_plus(query), offset, limit)
        content = self.__fetch(url).read()
       
        parsed = yaml.load(content)
        search = parsed['query']['search']
       
        results = []
       
        if search:
            for article in search:
                title = article['title'].strip()
               
                snippet = article['snippet']
                snippet = re.sub(r'(?m)<.*?>', '', snippet)
                snippet = re.sub(r'\s+', ' ', snippet)
                snippet = snippet.replace(' . ', '. ')
                snippet = snippet.replace(' , ', ', ')
                snippet = snippet.strip()
               
                wordcount = article['wordcount']
               
                results.append({
                    'title' : title,
                    'snippet' : snippet,
                    'wordcount' : wordcount
                })
       
        # yaml.dump(results, default_style='', default_flow_style=False,
        #     allow_unicode=True)
        return results
 
#def  string_distance()

articles = Set(['a', 'an', 'the'])


# remove articels from a string
def remove_article(string):
    result = ""
    space_separated = string.split(" ")
    for i in xrange(0,len(space_separated)):
        if space_separated[i] not in articles:
            result = result + space_separated[i] + " "
    result = result[0:len(result)-1]
    return result

#remove articles from array of string 
def remove_articles(array) :
    l = []
    for i in xrange(0,len(array)):
        l.append(remove_article(array[i].lower()))
    return l

#removes duplicate features from array of string
def duplicate_feature_removal(vector_string):
    vector_string = remove_articles(vector_string)
    vector_string.sort()
    
    result = []
    result.append(vector_string[0])
    c = 1
    prev = vector_string[0]
    while c < len(vector_string) :
        if vector_string[c] != prev :
            result.append(vector_string[c])
            prev = vector_string[c]
        c+=1
    return result
    
if __name__ == "__main1__":
    test = ["Big Bang Theory", "Arbit", "The Big Bang Theory", "Friends 1", "Arbit 2", "temp", "Friends 1"] 
    x = duplicate_feature_removal(test)
    print x
    

def find_related_word(string):  
    text = urllib2.urlopen("http://semantic-link.com/related.php?word=" + string).read()
    
    result = Set()
    try:
        a = text.split("},")
        for i in xrange(len(a)):
            b = a[i].split('"v":"')[1].split('"')[0]
            result.add(b)
    except:
        pass
    return result


def wiki(article):
    article = urllib.quote(article)
    opener = urllib2.build_opener()
    urllib2.install_opener(opener)
    
    opener.addheaders = [('User-agent', 'Mozilla/5.0')] #wikipedia needs this
    resource = urllib2.urlopen("http://en.wikipedia.org/wiki/" + article)
    data = resource.read()
    resource.close()
    soup = BeautifulSoup(data)
    print soup.find('div',id="bodyContent").p

    #article= "Albert Einstein"
    #print wiki(article)
    #print find_related_word("football")
def get_wiki_summary(query):
    lang = 'simple'
    wiki = Wikipedia(lang)

    try:
        raw = wiki.article(query)
    except:
        raw = None

    if raw:
        wiki2plain = Wiki2Plain(raw)
        content = wiki2plain.text
        l = content.find("==")
        content = content[0:l]
        return content
    else:
        return ''



########################   Extract Keywords   ################################################################

def uniqify(seq, idFun=None):
    # order preserving
    if idFun is None:
        def idFun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idFun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


def get_keywords(text, language='english'):
    # initialize the tagger with the required language
    tagger = tag.Tagger(language)
    tagger.initialize()
  
    # create the extractor with the tagger
    extractor = extract.TermExtractor(tagger=tagger)
    # invoke tagging the text
    extractor.tagger(text)
    # extract all the terms, even the &amp;quot;weak&amp;quot; ones
    extractor.filter = extract.DefaultFilter(singleStrengthMinOccur=1)
    # extract
    resultList = []
    result = extractor(text)

    for r in result:
    # discard the weights for now, not using them at this point and defaulting to lowercase keywords/tags
        resultList.append(r[0].lower())
    string = json.dumps(sorted(uniqify(resultList)))
    string = string[1:-1]
    string = string.replace(", ", ",")
    string = string.replace("\"", "")
    keywords = string.split(",")
    if '' in keywords:
        keywords.remove('')
    return Set(keywords)


###################### 


def get_imp_fb_likes(fb_user_dictionary):
    # define category_list
    category_list = ["Album","Animal","App","Appliances","Arts/entertainment/nightlife","Attractions/things to do","Bar","Book","Book genre","Book store","Camera/photo","Cars","Church/religious organization","Clothing","Club","Computers","Computers/technology","Concert tour","Drink","Drugs","Education","Electronics","Fictional character","Field of study","Food","Food/beverages","Games/toys","Health/beauty","Home decor","Interest","Internet/software","Kitchen/cooking","Landmark","Language","Legal/law","Media/news/publishing","Movie","Movie genre","Movies/music","Museum/art gallery","Music","Music video","Musical genre","Musical instrument","Organization","Patio/garden","Playlist","Political ideology","Professional sports team","Public places","Real estate","Religion","Restaurant/cafe","School","Shopping/retail","Software","Sport","Sports/recreation/activities","Studio","Tours/sightseeing","Travel/leisure","Tv genre","Tv show","University","Work position"]
    imp_likes = []
    for i in range(len(fb_user_dictionary['likes']['data'])):
        if fb_user_dictionary['likes']['data'][i]['category'] in category_list:
            imp_likes.append(fb_user_dictionary['likes']['data'][i]['name'])
    return Set(imp_likes)


def get_keywords_from_yahoo_answers(yahoo_answers_dict):
    try:
        for i in yahoo_answers_dict["query"]["results"]["Question"]:
            txt = ""
            if i["type"] == "Answered":
                txt += i["Subject"] + i["Content"] + i["ChosenAnswer"] + " "
            else:
                txt += i["Subject"] + i["Content"] + " "
    except:
        try:
            i = yahoo_answers_dict["query"]["results"]["Question"]
            txt = ""
            if i["type"] == "Answered":
                txt += i["Subject"] + i["Content"] + i["ChosenAnswer"] + " "
            else:
                txt += i["Subject"] + i["Content"] + " "
        except:
            txt = ""
    keywords = get_keywords(txt)
    return keywords


def get_keywords_from_quora_text(quora_dictionary):
    text = ""
    for i in quora_dictionary["answers"]:
        text += i + " "
    for i in quora_dictionary["questions"]:
        text += i + " "
    keywords = get_keywords(text)
    return keywords


def get_quora_topics(quora_dictionary):
    quora_topics = quora_dictionary['followed_topics'] + quora_dictionary['sub_topics']
    return Set(quora_topics)


def get_yahoo_topics(yahoo_answers_dict):
    yahoo_topics = []
    try:
        for i in yahoo_answers_dict["query"]["results"]["Question"]:
            topic = yahoo_answers_dict["query"]["results"]["Question"]["Category"]["content"]
            if "Other - " in topic:
                yahoo_topics.append(topic[8:])
            else:
                yahoo_topics.append(topic)
    except:
        try:
            topic = yahoo_answers_dict["query"]["results"]["Question"]["Category"]["content"]
            if "Other - " in topic:
                yahoo_topics.append(topic[8:])
            else:
                yahoo_topics.append(topic)
        except:
            yahoo_topics = []
    return Set(yahoo_topics)


def get_similarity_between_topic_and_text(topic_keywords, text_keywords):
    score = 0
    for i in topic_keywords:
        if i in text_keywords:
            score += 1
    return score


def get_similarity_of_all_topics_and_text(fb_user_dictionary, quora_dictionary, yahoo_answers_dict):
    fb_likes = get_imp_fb_likes(fb_user_dictionary)
    quora_topics = get_quora_topics(quora_dictionary)
    yahoo_topics = get_yahoo_topics(yahoo_answers_dict)
    all_topics = fb_likes.union(quora_topics.union(yahoo_topics))
    text_keywords = get_keywords_from_quora_text(quora_dictionary).union(get_keywords_from_yahoo_answers(yahoo_answers_dict))
    topic_score = {}
    for i in all_topics:
        if len(i.split()) > 1:
            try:
                txt = get_wiki_summary(i)
                if txt != "":
                    topic_keywords = get_keywords(txt)
                    topic_score[i] = get_similarity_between_topic_and_text(topic_keywords, text_keywords)
            except:
                topic_score[i] = 0
        else:
            topic_keywords = find_related_word(i)
            topic_score[i] = get_similarity_between_topic_and_text(topic_keywords, text_keywords)

    sorted_interest_topic = sorted(topic_score.iterkeys(), key=lambda k: topic_score[k], reverse=True)
    if len(sorted_interest_topic) < 20 :
        return sorted_interest_topic
    else:
        return sorted_interest_topic[0:20]


def match_interest_score(interests1, interests2):
    weights = [48.09, 46.37, 44.81, 43.40, 42.13, 40.97, 39.93, 38.98,
               38.13, 37.35, 36.65, 36.02, 35.45, 34.93, 34.46, 34.03,
               33.65, 33.30, 32.99, 34.11]
 
    total = 0
    for ii, i in enumerate(interests1):
        for jj, j in enumerate(interests2):
            if i == j:
                total += weights[ii] * weights[jj]
    minimum_features = min(len(interests1), len(interests2))
    normalizing_factor = 0
    for i in range(minimum_features):
        normalizing_factor += weights[i]**2
    score = total / normalizing_factor
    return score
