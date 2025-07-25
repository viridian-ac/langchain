import os
import tweepy
from datetime import datetime, timezone, timedelta
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Your API credentials
consumer_key = os.getenv("X_APP_CONSUMER_KEY_TOKEN")
consumer_secret = os.getenv("X_APP_CONSUMER_KEY_TOKEN_SECRET")
access_token = os.getenv("X_APP_ACCESS_TOKEN")
access_token_secret = os.getenv("X_APP_ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("X_APP_BEARER_TOKEN")

# Optional: Set a cutoff date to delete only reposts before this
# To delete ALL reposts, comment out or set a very old date
cutoff_date = datetime.now(timezone.utc) - timedelta(days=365 * 3)

def tweet_count():
    print('--- def tweet_count')
    while True:
        try:
            user_response = client.get_me(user_fields=['public_metrics'])
            print("Full API Response:", user_response)  # Debug: Inspect raw response

            if user_response.data is None:
                print("Error: No user data returned. Check API permissions or credentials.")
                exit(1)

            user = user_response.data
            print(f"Authenticated User: {user.username}")
            print(f"Authenticated User-ID: {user.id}")

            if user.public_metrics is None:
                print("Error: public_metrics not available. Likely due to API tier (Free) or app not in a project.")
                print("Raw user data for debugging:", user)
                exit(1)

            tweet_count = user.public_metrics['tweet_count']
            print(f"Number of tweets (including replies and reposts): {tweet_count}")
            break  # Suc
            # cess

        except tweepy.errors.TooManyRequests as e:
            if e.response is not None:
                reset_time = int(e.response.headers.get('x-rate-limit-reset', time.time() + 60))
                wait = max(reset_time - time.time() + 5, 1)
                print(f"Rate limited. Waiting {wait} seconds.")
                time.sleep(wait)
            else:
                print("Rate limit error without response. Waiting 60 seconds.")
                time.sleep(60)


        except tweepy.errors.Forbidden as e:
            print(f"Forbidden error: {e}. Check if app is attached to a project or upgrade tier.")
            exit(1)
        except tweepy.errors.Unauthorized as e:
            print(f"Authentication failed: {e}. Check credentials and permissions.")
            exit(1)


def tweet_fetch():
    print('--- def tweet_fetch')
    # Fetch user's tweets and filter for reposts with rate limit handling
    try:
        deleted_count = 0
        pagination_token = None
        while True:
            while True:  # Retry loop for fetch
                try:
                    response = client.get_users_tweets(
                        id=user_id,
                        max_results=100,
                        tweet_fields=['created_at', 'referenced_tweets'],
                        pagination_token=pagination_token
                    )

                    break  # Successful fetch

                except Exception as e:
                    print(f"Error fetching tweets: {e}")
                    raise

            if not response.data:
                print("No more tweets found.")
                break

            # Filter for reposts
            reposts = [
                tweet for tweet in response.data
                if tweet.referenced_tweets and any(ref.type == 'retweeted' for ref in tweet.referenced_tweets)
            ]

            for repost in reposts:
                tweet_id = repost.id
                created_at = repost.created_at

                # Skip if repost is newer than cutoff_date
                if created_at >= cutoff_date:
                    continue

                while True:  # Retry loop for delete
                    try:
                        client.delete_tweet(tweet_id)
                        print(f"Deleted repost {tweet_id} from {created_at}")
                        deleted_count += 1
                        time.sleep(2)  # Base delay
                        break  # Successful delete
                    except tweepy.errors.TooManyRequests as e:
                        if e.response is not None:
                            reset_time = int(e.response.headers.get('x-rate-limit-reset', time.time() + 60))
                            wait = max(reset_time - time.time() + 5, 1)
                            print(f"Rate limited on delete. Waiting {wait} seconds.")
                            time.sleep(wait)
                        else:
                            print("Rate limit error without response. Waiting 60 seconds.")
                            time.sleep(60)
                    except tweepy.errors.Unauthorized as e:
                        print(f"Auth error deleting {tweet_id}: {e}")
                        break
                    except tweepy.errors.TweepyException as e:
                        print(f"Error deleting {tweet_id}: {e}")
                        break  # Don't retry other errors

            if 'next_token' in response.meta:
                pagination_token = response.meta['next_token']
            else:
                break

        print(f"Deleted {deleted_count} reposts successfully.")
    except Exception as e:
        print(f"Error fetching or deleting reposts: {e}")






try:
    # Initialize Tweepy Client
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        bearer_token=bearer_token
    )
    # Authenticate and get user info
    user = client.get_me().data
    print(f"Authenticated User: {user.username}")
    user_id = user.id
    print(f"Authenticated User-ID: {user_id}")

    #tweet_count()
    #tweet_fetch()

except Exception as e:
    print(f"Error fetching user data: {e}")
    exit(1)

