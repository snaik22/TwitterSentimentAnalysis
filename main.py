# Import libraries
import tweepy # Twitter
import numpy
import pandas
import matplotlib
from textblob import TextBlob, Word # Text pre-processing
import re # Regular expressions
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator # Word clouds
from PIL import Image
from pyspark.sql import SparkSession # Spark

# Import Twitter authentication file
from twitter_auth import *

# Twitter authentication
def twitter_auth():
    # Uses hardcoded Twitter credentials and returns a request handler
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    return tweepy.API(auth)

# Retrieve Tweets
def get_tweets():
    # Creates a Tweet list and extracts Tweets
    account = '@BarackObama' # You can change this to any Twitter account you wish
    extractor = twitter_auth() # Twitter handler object
    tweets = []
    for tweet in tweepy.Cursor(extractor.user_timeline, id = account).items():
        tweets.append(tweet)
    print('Number of Tweets extracted: {}.\n'.format(len(tweets)))
    return tweets

# Create dataframe
def make_dataframe(tweets):
    # This function returns a dataframe containing the text in the Tweets
    return pandas.DataFrame(data = tweets, columns = ['Tweets'])                 # edited

# Pre-process Tweets
def clean_tweets(data):
    # Pre-processes the text in the Tweets and runs in parallel
    spark = SparkSession\
    .builder\
    .appName("PythonPi")\
    .getOrCreate()
    sc = spark.sparkContext
    paralleled = sc.parallelize(data)
    return paralleled.map(text_preprocess).collect()

# Pre-process text in Tweet
def text_preprocess(tweet):
    # This function returns a Tweet that consists of only lowercase characters
    
    t = re.sub(r"[^a-zA-Z0-9]+",' ', tweet.text)
    
    twit = []
    for word in t.split():
        a = Word(word)
        a = a.lemmatize()
        twit.append(a.lower())
    teet = ' '.join(word for word in twit)
    return teet

# Retrieve sentiment of Tweets
def generate_sentiment(data):
    # Returns the sentiment of the Tweets and runs in parallel
    spark = SparkSession\
    .builder\
    .appName("PythonPi")\
    .getOrCreate()
    sc = spark.sparkContext
    paralleled = sc.parallelize(data)
    return paralleled.map(data_sentiment).collect()

# Retrieve sentiment of Tweet
def data_sentiment(tweet):
    # This function returns 1, 0, or -1 depending on the value of text.sentiment.polarity
    text = TextBlob(tweet)
    if text.sentiment.polarity > 0.05:
        return 1                                                   # Edited
    elif text.sentiment.polarity > -0.05 and text.sentiment.polarity < 0.05:
        return 0
    else:
        return -1

# Classify Tweets
def classify_tweets(data):
    # Given the cleaned Tweets and their sentiment,
    # this function returns a list of good, neutral, and bad Tweets
    good_tweets = ""
    neutral_tweets = ""
    bad_tweets = ""
    
    good_tweets = list(data[data['sentiment'] == 1]['cleaned_tweets'])
    neutral_tweets = list(data[data['sentiment']==0]['cleaned_tweets'])
    bad_tweets = list(data[data['sentiment'] == -1]['cleaned_tweets'])                            
    
    good_tweets = ','.join(good_tweets)
    neutral_tweets = ','.join(neutral_tweets)                           
    bad_tweets = ','.join(bad_tweets)
                               
    return [good_tweets, neutral_tweets, bad_tweets]

# Create word cloud
def create_word_cloud(classified_tweets) :
    # Given the list of good, neutral, and bad Tweets,
    # creates a word cloud for each list
    good_tweets = classified_tweets[0]
    neutral_tweets = classified_tweets[1]
    bad_tweets = classified_tweets[2]
    stopwords = set(STOPWORDS)
    good_cloud = WordCloud(width = 800, height = 500).generate(good_tweets)
    neutral_cloud = WordCloud(width = 800, height = 500).generate(neutral_tweets)
    bad_cloud = WordCloud(width = 800, height = 500).generate(bad_tweets)
    produce_plot(good_cloud, "Good.png")
    produce_plot(neutral_cloud, "Neutral.png")
    produce_plot(bad_cloud, "Bad.png")

# Produce plot
def produce_plot(cloud, name):
    matplotlib.pyplot.axis("off")
    matplotlib.pyplot.imshow(cloud, interpolation='bilinear')
    fig = matplotlib.pyplot.figure(1)
    fig.savefig(name)
    matplotlib.pyplot.clf()

# Task 01: Retrieve Tweets
tweets = get_tweets()
# Task 02: Create dataframe 
df = make_dataframe(tweets)
# Task 03: Pre-process Tweets
df['cleaned_tweets'] = df['Tweets'].apply(text_preprocess)
# Task 04: Retrieve sentiments
df['sentiment'] = df['cleaned_tweets'].apply(data_sentiment)
# Task 05: Classify Tweets
classified_tweets = classify_tweets(df)
# Task 06: Create Word Cloud
create_word_cloud(classified_tweets)
