from time import sleep
import tweepy
import os


credentials = {
    "api_key": os.environ["tw_api_key"],
    "api_secret": os.environ["tw_api_secret"],
    "access_token": os.environ["tw_access_token"],
    "access_secret": os.environ["tw_access_secret"],
    "client_id": os.environ["tw_client_id"],
    "client_secret": os.environ["tw_client_secret"]
}



def build_tweet(edicte):
    msg = f"""Nou edicte - {edicte.get('data')}
Què: {edicte.get('que')}
Qui: {edicte.get("qui")}
On:  {edicte.get("on")}
"""
    
    if (len(msg) < 254):
        msg += f"ID: {edicte.get('id')}"
    
    return msg


def get_twitter_conn_v1() -> tweepy.API:
    """Get twitter conn 1.1"""

    auth = tweepy.OAuth1UserHandler(
        consumer_key=credentials["api_key"],
        consumer_secret=credentials["api_secret"]
    )
    
    auth.set_access_token(
        key=credentials["access_token"],
        secret=credentials["access_secret"]
    )
    
    return tweepy.API(auth)


def get_twitter_conn_v2() -> tweepy.Client:
    """Get twitter conn 2.0"""

    client = tweepy.Client(
        consumer_key=credentials["api_key"],
        consumer_secret=credentials["api_secret"],
        access_token=credentials["access_token"],
        access_token_secret=credentials["access_secret"],
    )

    return client

def post_tweets(edictes):
    client_v1 = get_twitter_conn_v1()
    client_v2 = get_twitter_conn_v2()

    for edicte in edictes:
        img = edicte.get("img", False)
        
        if (img):
            edicte.get("img").save("tmp.png", format="PNG")
        
            media = client_v1.media_upload(filename="tmp.png")
            media_ids = [media.media_id]
        else:
            media_ids = None

        client_v2.create_tweet(
            text=build_tweet(edicte),
            media_ids=media_ids
        )
        sleep(1)