
import json
import tweepy

import os
from datetime import datetime, timezone, timedelta
import requests
import time
from dotenv import load_dotenv

# from docs.docs.integrations.llms.google_ai import api_key




# Load the archive file (tweets.js starts with 'window.YTD.tweets.part0 = ', so strip it)

load_dotenv()

# Your API credentials (from Step 1)
consumer_key = os.getenv("X_APP_CONSUMER_KEY_TOKEN")  # 'YOUR_CONSUMER_KEY'
consumer_secret =os.getenv("X_APP_CONSUMER_KEY_TOKEN_SECRET")  # 'YOUR_CONSUMER_SECRET'
access_token = os.getenv("X_APP_ACCESS_TOKEN")  # 'YOUR_ACCESS_TOKEN'
access_token_secret = os.getenv("X_APP_ACCESS_TOKEN_SECRET")  #'YOUR_ACCESS_TOKEN_SECRET'
access_token_bearer = os.getenv("X_APP_BEARER_TOKEN")
# Path to your extracted tweets.js file from the archive
archive_path = 'tweets.js'
# archive_path = input("Enter the full path to tweets.js: ").strip()



# Load the archive file (tweets.js starts with 'window.YTD.tweets.part0 = ', so strip it)


try:
    with open(archive_path, 'r', encoding='utf-8') as f:
        data = f.read()
        json_start = data.find('[')
        json_end = data.rfind(']') + 1
        json_data = data[json_start:json_end]
        tweets = json.loads(json_data)
    print(f"Loaded {len(tweets)} tweets from archive.")
except FileNotFoundError:
    print(f"File not found: {archive_path}")
    # exit(1)
except Exception as e:
    print(f"Error loading archive: {e}")
     #exit(1)

# Optional: Set a cutoff date to delete only tweets before this (e.g., all tweets: set to a future date or remove the check)
# To delete ALL, comment out the if condition or set a very old date
cutoff_date = datetime.now(timezone.utc) - timedelta(days=365 * 1)

try:
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    user = client.get_me().data
    print(f"Authenticated User: {user.username}")
    user_id = client.get_me().data.id  # Get your user ID
    print(f"Authenticated User-ID: {user_id}")
except tweepy.errors.Unauthorized as e:
    print(f"Authentication failed: {e}. Check credentials and permissions.")
    exit(1)
except Exception as e:
    print(f"Setup error: {e}")
    exit(1)    # exit(1)  # Stop if auth fails





#-----

client0 = tweepy.Client(bearer_token= access_token_bearer)
# Note: There is no direct 'get_my_reposts' endpoint in Tweepy v2; instead, we can fetch the user's timeline and filter for retweets.
# To get recent reposts, use client.get_users_tweets with expansions.
response = client0.get_users_tweets(id=user_id, max_results=100, tweet_fields=['created_at', 'referenced_tweets'])
reposts = [tweet for tweet in response.data if tweet.referenced_tweets and any(ref.type == 'retweeted' for ref in tweet.referenced_tweets)]
for repost in reposts:
    print(repost.text)



def make_request(url, headers):
    while True:
        response0 = requests.get(url, headers=headers)
        if response.status_code == 429:
            reset_time = int(response.headers.get('x-rate-limit-reset', 0))
            wait = max(reset_time - time.time(), 1) + 1  # Add buffer
            print(f"Rate limited. Waiting {wait} seconds.")
            time.sleep(wait)
        else:
            return response0
#-----


try:
    with open(archive_path, 'r', encoding='utf-8') as f:
        data = f.read()
        json_start = data.find('[')
        json_end = data.rfind(']') + 1
        json_data = data[json_start:json_end]
        tweets = json.loads(json_data)
    print(f"Loaded {len(tweets)} tweets from archive.")
except FileNotFoundError:
    print(f"File not found: {archive_path}")
    # exit(1)
except Exception as e:
    print(f"Error loading archive: {e}")
     #exit(1)

# Optional: Set a cutoff date to delete only reposts before this (e.g., all reposts: set to a future date or remove the check)
# To delete ALL reposts, comment out the if condition or set a very old date
cutoff_date = datetime.now(timezone.utc) - timedelta(days=365 * 1)

try:
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    user = client.get_me().data
    print(f"Authenticated User: {user.username}")
    user_id = client.get_me().data.id  # Get your user ID
    print(f"Authenticated User-ID: {user_id}")
except tweepy.errors.Unauthorized as e:
    print(f"Authentication failed: {e}. Check credentials and permissions.")
    exit(1)
except Exception as e:
    print(f"Setup error: {e}")
    exit(1)    # exit(1)  # Stop if auth fails





#-----



client0 = tweepy.Client(bearer_token= access_token_bearer)
# Note: There is no direct 'get_my_reposts' endpoint in Tweepy v2; instead, we can fetch the user's timeline and filter for retweets.
# To get recent reposts, use client.get_users_tweets with expansions.
response = client0.get_users_tweets(id=user_id, max_results=429, tweet_fields=['created_at', 'referenced_tweets'])
reposts = [tweet for tweet in response.data if tweet.referenced_tweets and any(ref.type == 'retweeted' for ref in tweet.referenced_tweets)]
for repost in reposts:
    print(repost.text)



def make_request(url, headers):
    while True:
        response0 = requests.get(url, headers=headers)
        if response.status_code == 429:
            reset_time = int(response.headers.get('x-rate-limit-reset', 0))
            wait = max(reset_time - time.time(), 1) + 1  # Add buffer
            print(f"Rate limited. Waiting {wait} seconds.")
            time.sleep(wait)
        else:
            return response0

#-----

# Delete reposts from archive
deleted_count = 0
for tweet in tweets:
    tweet_data = tweet['tweet']
    tweet_id = tweet_data['id_str']
    created_at = datetime.strptime(tweet_data['created_at'], '%a %b %d %H:%M:%S %z %Y').replace(tzinfo=timezone.utc)

    # Check if it's a repost (retweet)
    if 'retweeted_status' not in tweet_data:
        continue  # Skip if not a repost

    if created_at >= cutoff_date:
        continue

    try:
        client.delete_tweet(tweet_id)
        print(f"Deleted repost {tweet_id} from {created_at}")
        deleted_count += 1
        time.sleep(2)  # Adjust for rate limits (e.g., 15 for Basic tier)
    except tweepy.errors.Unauthorized as e:
        print(f"Auth error deleting {tweet_id}: {e}")
    except tweepy.errors.TweepyException as e:
        print(f"Error deleting {tweet_id}: {e}")

print(f"Deleted {deleted_count} reposts successfully.")
#-----

