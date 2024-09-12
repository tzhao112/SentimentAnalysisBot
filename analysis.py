from flask import Blueprint, render_template, request
import matplotlib.pyplot as plt
import os

import tweepy
import csv
import re
from textblob import TextBlob
import matplotlib
matplotlib.use('agg')

second = Blueprint("second", __name__, static_folder="static", template_folder="template")

@second.route("/sentiment_analyzer")
def sentiment_analyzer():
	return render_template("sentiment_analyzer.html")

class SentimentAnalysis:

	def __init__(self):
		self.tweets = []
		self.tweetText = []

	def DownloadData(self, keyword, tweets):
		consumerKey = '//get from Tweepy'
		consumerSecret = '//get from Tweepy'
		accessToken = '//insert your access token here'
		accessTokenSecret = '//Tweepy AccessToken secret here'
		auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
		auth.set_access_token(accessToken, accessTokenSecret)
		api = tweepy.API(auth, wait_on_rate_limit=True)

		tweets = int(tweets)
		self.tweets = tweepy.Cursor(api.search, q=keyword, lang="en").items(tweets)

		csvFile = open('result.csv', 'a')
		csvWriter = csv.writer(csvFile)

		polarity = 0
		positive = 0
		wpositive = 0
		spositive = 0
		negative = 0
		wnegative = 0
		snegative = 0
		neutral = 0

		for tweet in self.tweets:
			self.tweetText.append(self.cleanTweet(tweet.text).encode('utf-8'))
			analysis = TextBlob(tweet.text)
			polarity += analysis.sentiment.polarity

			if analysis.sentiment.polarity == 0:
				neutral += 1
			elif analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3:
				wpositive += 1
			elif analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6:
				positive += 1
			elif analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1:
				spositive += 1
			elif analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity <= 0:
				wnegative += 1
			elif analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3:
				negative += 1
			elif analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6:
				snegative += 1

		csvWriter.writerow(self.tweetText)
		csvFile.close()

		positive = self.percentage(positive, tweets)
		wpositive = self.percentage(wpositive, tweets)
		spositive = self.percentage(spositive, tweets)
		negative = self.percentage(negative, tweets)
		wnegative = self.percentage(wnegative, tweets)
		snegative = self.percentage(snegative, tweets)
		neutral = self.percentage(neutral, tweets)
		polarity = polarity / tweets

		if polarity == 0:
			htmlpolarity = "Neutral"
		elif polarity > 0 and polarity <= 0.3:
			htmlpolarity = "Weakly Positive"
		elif polarity > 0.3 and polarity <= 0.6:
			htmlpolarity = "Positive"
		elif polarity > 0.6 and polarity <= 1:
			htmlpolarity = "Strongly Positive"
		elif polarity > -0.3 and polarity <= 0:
			htmlpolarity = "Weakly Negative"
		elif polarity > -0.6 and polarity <= -0.3:
			htmlpolarity = "Negative"
		elif polarity > -1 and polarity <= -0.6:
			htmlpolarity = "Strongly Negative"

		self.plotPieChart(positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets)
		return polarity, htmlpolarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets

	def cleanTweet(self, tweet):
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())

	def percentage(self, part, whole):
		temp = 100 * float(part) / float(whole)
		return format(temp, '.2f')

	def plotPieChart(self, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets):
		fig = plt.figure()
		labels = ['Positive [' + str(positive) + '%]', 'Weakly Positive [' + str(wpositive) + '%]', 'Strongly Positive [' + str(spositive) + '%]',
				'Neutral [' + str(neutral) + '%]', 'Negative [' + str(negative) + '%]', 'Weakly Negative [' + str(wnegative) + '%]', 
				'Strongly Negative [' + str(snegative) + '%]']
		sizes = [positive, wpositive, spositive, neutral, negative, wnegative, snegative]
		colors = ['yellowgreen', 'lightgreen', 'darkgreen', 'gold', 'red', 'lightsalmon', 'darkred']
		patches, texts = plt.pie(sizes, colors=colors, startangle=90)
		plt.legend(patches, labels, loc="best")
		plt.axis('equal')
		plt.tight_layout()
		strFile = r"C:\Users\LENOVO\PycharmProjects\SentimentAnalysis\static\images\plot1.png"
		if os.path.isfile(strFile):
			os.remove(strFile)
		plt.savefig(strFile)
		plt.show()

@second.route('/sentiment_logic', methods=['POST', 'GET'])
def sentiment_logic():
	keyword = request.form.get('keyword')
	tweets = request.form.get('tweets')
	sa = SentimentAnalysis()
	polarity, htmlpolarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword1, tweet1 = sa.DownloadData(keyword, tweets)
	return render_template('sentiment_analyzer.html', polarity=polarity, htmlpolarity=htmlpolarity, positive=positive, wpositive=wpositive, spositive=spositive,
						negative=negative, wnegative=wnegative, snegative=snegative, neutral=neutral, keyword=keyword1, tweets=tweet1)

@second.route('/visualize')
def visualize():
	return render_template('PieChart.html')
