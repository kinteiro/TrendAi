#### ---- IMPORTS ---- ####

# import json
# import webbrowser
from datetime import datetime, timedelta
import pandas as pd
from instaloader import Profile, instaloader # , resumable_iteration, FrozenNodeIterator
import logging
logger = logging.getLogger()

L = instaloader.Instaloader()


#### ---- GLOBALS ---- ####

INGEST_DATE = datetime.now().strftime("%Y-%m-%d %H:%M")
# YESTERDAY = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')


#### ---- FUNCTIONS ---- ####

def get_profile(username: str) -> Profile:
    print(f"Getting profile {username}")
    profile = Profile.from_username(L.context, username)
    return profile


def get_urls_to_df(username, inputlen: int) -> list:
    """
    Get the urls of the images of a profile.
    :param profile: Profile object
    :return: list of urls
    """
    post_iterator = get_profile(username).get_posts()
    data_to_df = []
    for post in post_iterator:
        try:
            post_data = {
                'Image_date': post.date.strftime('%Y-%m-%d'),
                'Image_Profile': post.profile,
                'Image_URL': post.url,
                'Ingest_Date': INGEST_DATE,
                'Caption': post.caption
            }
            data_to_df.append(post_data)
            print.info(f"Getting post {post_data['Image_URL']}")
            if len(data_to_df) > inputlen:
                print.info(f"Reached {inputlen} posts")
                break
        except Exception as e:
            print(f"--ERROR ITERANDO EN LA API--\n{e}")
            continue
    return data_to_df


def create_df(data: list) -> pd.DataFrame:
    """
    Create a DataFrame from a list of dictionaries.
    :param data: list of dictionaries
    :return: DataFrame
    """
    df = pd.DataFrame(data)
    return df
