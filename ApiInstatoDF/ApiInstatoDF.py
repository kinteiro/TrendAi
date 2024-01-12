#### ---- IMPORTS ---- ####

# import json
# import webbrowser
from datetime import datetime, timedelta
import pandas as pd
from instaloader import Profile, instaloader # , resumable_iteration, FrozenNodeIterator

L = instaloader.Instaloader()


#### ---- GLOBALS ---- ####

INGEST_DATE = datetime.now().strftime("%Y-%m-%d %H:%M")
# YESTERDAY = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')


#### ---- FUNCTIONS ---- ####

def get_profile(username: str) -> Profile:
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
        post_data = {
            'Image_date': post.date.strftime('%Y-%m-%d'),
            'Image_Profile': post.profile,
            'Image_URL': post.url,
            'Ingest_Date': INGEST_DATE,
            'Caption': post.caption
        }
        data_to_df.append(post_data)
        if len(data_to_df) > inputlen:
            break
    return data_to_df


def create_df(data: list) -> pd.DataFrame:
    """
    Create a DataFrame from a list of dictionaries.
    :param data: list of dictionaries
    :return: DataFrame
    """
    df = pd.DataFrame(data)
    return df
