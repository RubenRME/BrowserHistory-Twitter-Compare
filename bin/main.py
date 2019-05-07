import tweepy
import datetime
import yaml
import unicodedata
import browserhistory as bh

with open("../config.yml", "r") as ymlfile:
    data = yaml.load(ymlfile, Loader=yaml.FullLoader)

if not data['EULA']:
    print('YOU NEED TO ACCEPT THE EULA IN CONFIG.YML')
    exit()

# Initiating Tweepy
auth = tweepy.OAuthHandler(data['api']['consumer_key'], data['api']['consumer_secret'])

auth.set_access_token(data['api']['access_token'], data['api']['access_secret'])

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

print('Twitter API initiated')


def gettimesetting():
    if data['search_from'] == "Now":
        return datetime.datetime.now()
    else:
        return datetime.datetime.strptime(data['search_from'], '%Y-%M-%d')


print('Settings loaded from config.yml')

# Creating dictionaries to handle found tweets
tweets = {}
urls = {}

# Loop to get only recent tweets
for status in tweepy.Cursor(api.user_timeline, id=data['subject_username']).items():
    delta = gettimesetting() - datetime.datetime.strptime(status._json['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    tweets[str(status._json['id'])] = status._json['text']
    if len(status._json['entities']['urls']) != 0:
        for link in status._json['entities']['urls']:
            urls[link['url']] = link['expanded_url']
    if delta.days > data['search_days']:
        break
print(urls)
print('Got tweets from the last ' + str(data['search_days']) + ' days from ' + data['search_from'])

history_dict = bh.get_browserhistory()
history = history_dict['chrome']
history_new = []

print('Loaded Browser history from chrome')

for website in history:
    delta = gettimesetting() - datetime.datetime.strptime(website[2], '%Y-%m-%d %H:%M:%S')
    if delta.days > data['search_days']:
        # For some reason this if takes an extra day, but I'm now calling it a feature as it's actually logical to do so
        break
    history_new.append(website)
print('Filtered browser history from last ' + str(data['search_days'] + 1) + ' days from ' + data['search_from'])

urls_filtered = []

# Check url list against history and filter out those that aren't in history
for website in history_new:
    for url in urls.items():
        if website[0] == url[1]:
            urls_filtered.append(url)

print('Filtered URLs to only contain those found in the browser history')
print(urls_filtered)
results = []
# Use the filtered url list to check urls against tweets, and put tweets that include the url into the results list
for url in urls_filtered:
    for tweet in tweets.items():
        if url[0] in tweet[1]:
            results.append(tweet)
print('Filtered tweets to only include the ones that contain the url')

# The least sexy way to write results into an HTML file but it works and I cba

strTable = "<html><table border=\"1\"><tr><th>Tweet</th><th>Link</th></tr>"

for result in results:
    strRow = "<tr><td><i>" + result[1] + "</i></td><td><a href=\"https://twitter.com/" + data[
        'subject_username'] + "/status/" + result[0] + "\" target=\"_new\">https://twitter.com/" + data[
                 'subject_username'] + "/status/" + result[0] + "</a></td></tr>"
    strTable = strTable + strRow

strTable = strTable + "</table></html>"

hs = open("../results.html", "w")
hs.write(str(unicodedata.normalize('NFKD', strTable).encode('ascii', 'ignore')))
hs.close()

print('Saved results in results.html!')
