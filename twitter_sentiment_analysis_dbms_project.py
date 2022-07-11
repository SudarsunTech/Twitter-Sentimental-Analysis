import sys,tweepy,re
from textblob import TextBlob
import matplotlib.pyplot as plt
import mysql.connector as db

print("""
_____________________________________________________________________________________________________________________________________________________________


\t\t\t\t\t\t***********************************************************
\t\t\t\t\t\t*                                                         *
\t\t\t\t\t\t*                                                         *
\t\t\t\t\t\t*                                                         *
\t\t\t\t\t\t*             TWITTER SENTIMENTAL ANALYSIS                *
\t\t\t\t\t\t*                                                         *
\t\t\t\t\t\t*                                                         *
\t\t\t\t\t\t*                                                         *
\t\t\t\t\t\t***********************************************************

_____________________________________________________________________________________________________________________________________________________________
""")

#connection into mysql
conn = db.connect(host="localhost",
                  user="root",
                  password="1234",
                  database="sentimental_analysis")
cur=conn.cursor()


class SentimentAnalysis:

    def __init__(self):
        self.tweets = []
        self.tweetText = []

    def DownloadData(self):
        # authenticating
        consumerKey = 'ad7I1YjV9CprDr7AXbL9THjLO'
        consumerSecret = 'jxwImhtUThM4ErE6POvUwpGCoKwtXzKbZlCkzJnKYqWOeBDs3D'
        accessToken = '1956556794-idqpfskYMTDsQADV169vRmcESc7QaBOBc3N60vW'
        accessTokenSecret = '6Vjx9mS94NcT85v6rySHv8TYQ0HywZIH5Yj4PmSja9SFJ'
        auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
        auth.set_access_token(accessToken, accessTokenSecret)
        api = tweepy.API(auth)      


        # input for term to be searched and how many tweets to search
        searchTerm = input("\t\t\t\t\t\t   Enter any Keyword / HashTag to search in Twitter: ")
        NoOfTerms = int(input("\n\t\t\t\t\t\t\tEnter how many tweets to  be searched: "))

        # searching for tweets
        self.tweets = tweepy.Cursor(api.search, q=searchTerm, lang = "en").items(NoOfTerms)

        # creating some variables to store info
        polarity = 0
        positive = 0
        wpositive = 0
        spositive = 0
        negative = 0
        wnegative = 0
        snegative = 0
        neutral = 0
        report = ""

        # iterating through tweets fetched
        for tweet in self.tweets:
            #Append to temp so that we can insert in sql later. We use encode UTF-8
            self.tweetText.append(self.cleanTweet(tweet.text).encode('utf-8'))
            analysis = TextBlob(tweet.text)
            polarity += analysis.sentiment.polarity  # adding up polarities to find the average later

            if (analysis.sentiment.polarity == 0):  # adding reaction of how people are reacting to find average later
                neutral += 1
            elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3):
                wpositive += 1
            elif (analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6):
                positive += 1
            elif (analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1):
                spositive += 1
            elif (analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity <= 0):
                wnegative += 1
            elif (analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3):
                negative += 1
            elif (analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6):
                snegative += 1

        # finding average of how people are reacting
        positive = self.percentage(positive, NoOfTerms)
        wpositive = self.percentage(wpositive, NoOfTerms)
        spositive = self.percentage(spositive, NoOfTerms)
        negative = self.percentage(negative, NoOfTerms)
        wnegative = self.percentage(wnegative, NoOfTerms)
        snegative = self.percentage(snegative, NoOfTerms)
        neutral = self.percentage(neutral, NoOfTerms)

        # finding average reaction
        polarity = polarity / NoOfTerms

        # printing out data
        print("""_____________________________________________________________________________________________________________________________________________________________
""")
        print(f"\n\t\t\t\t\tLet us get to know how people are expressing on {searchTerm} by analyzing {NoOfTerms} tweets\n")
        print("\t\t\t\t\t\t\t\t","\u0332".join("General Report"),": ", end='')

        if (polarity == 0):
            report = "Neutral"
            print(report)
        elif (polarity > 0 and polarity <= 0.3):
            report = "Weakly Positive"
            print(report)
        elif (polarity > 0.3 and polarity <= 0.6):
            report = "Positive"
            print(report)
        elif (polarity > 0.6 and polarity <= 1):
            report = "Strongly Positive"
            print(report)
        elif (polarity > -0.3 and polarity <= 0):
            report = "Weakly Negative"
            print(report)
        elif (polarity > -0.6 and polarity <= -0.3):
            report = "Negative"
            print(report)
        elif (polarity > -1 and polarity <= -0.6):
            report = "Strongly Negative"
            print(report)
        
        #inserting into sql
        truncate_stmt = ("TRUNCATE TABLE TWITTER_REVIEWS")
        cur.execute(truncate_stmt)
        truncate_ex = ("TRUNCATE TABLE EXTRACTED_TWEETS")
        cur.execute(truncate_ex)
        insert_stmt = (
           "INSERT INTO TWITTER_REVIEWS(HASHTAG, NO_OF_TWEETS, POSITIVE,WPOSITIVE, SPOSITIVE, NEGATIVE, WNEGATIVE, SNEGATIVE, NEUTRAL, GEN_REPORT)"
           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        data = (searchTerm, NoOfTerms, positive, wpositive, spositive, negative, wnegative, snegative, neutral, report)
        cur.execute(insert_stmt, data)
        conn.commit()
        select_stmt = ("SELECT * FROM TWITTER_REVIEWS")
        cur.execute(select_stmt)
        details = cur.fetchall()
        info=[a for a in details[0]]
        for a in self.tweetText:
            insert=("INSERT INTO EXTRACTED_TWEETS(TWEET_TEXTS)"
                    "VALUES (%s)")
            val=(a,)
            cur.execute(insert,val)
            conn.commit()
        conn.close()
           
        print("\n\n\t\t\t\t\t\t\t\t\tDETAILED REPORT")
        print(f"""
_____________________________________________________________________________________________________________________________________________________________
                                                            

\t\t\t\t\t\t       1) {str(positive)} % people thought it was positive              
\t\t\t\t\t\t       2) {str(wpositive)} % people thought it was weakly positive        
\t\t\t\t\t\t       3) {str(spositive)} % people thought it was strongly positive      
\t\t\t\t\t\t       4) {str(negative)} % people thought it was negative                
\t\t\t\t\t\t       5) {str(wnegative)} % people thought it was weakly negative        
\t\t\t\t\t\t       6) {str(snegative)} % people thought it was strongly negative      
\t\t\t\t\t\t       7) {str(neutral)} % people thought it was neutral                  
                                                                          
_____________________________________________________________________________________________________________________________________________________________
""")

        self.plotPieChart(info[2], info[3], info[4], info[5], info[6], info[7], info[8], info[0], info[1])

    def cleanTweet(self, tweets):
        # Remove Links, Special Characters etc from tweet
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweets).split())

    # function to calculate percentage
    def percentage(self, sentiment, no_of_terms):
        temp = 100 * float(sentiment) / float(no_of_terms)
        return format(temp, '.2f')

    def plotPieChart(self, positive, wpositive, spositive, negative, wnegative, snegative, neutral, searchTerm, noOfSearchTerms):
        labels = ['Positive [' + str(positive) + '%]', 'Weakly Positive [' + str(wpositive) + '%]','Strongly Positive [' + str(spositive) + '%]', 'Neutral [' + str(neutral) + '%]',
                  'Negative [' + str(negative) + '%]', 'Weakly Negative [' + str(wnegative) + '%]', 'Strongly Negative [' + str(snegative) + '%]']
        sizes = [positive, wpositive, spositive, neutral, negative, wnegative, snegative]
        colors = ['yellowgreen','lightgreen','darkgreen', 'gold', 'red','lightsalmon','darkred']
        patches, texts = plt.pie(sizes, colors=colors, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.title('How people are reacting on ' + searchTerm + ' by analyzing ' + str(noOfSearchTerms) + ' Tweets.')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()

if __name__== "__main__":
    sa = SentimentAnalysis()
    sa.DownloadData()
