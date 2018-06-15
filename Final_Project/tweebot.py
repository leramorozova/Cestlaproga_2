import tweepy
import datasetter as ds
from apscheduler.schedulers.blocking import BlockingScheduler

API_KEY = "CFvvE8BNcONOSGopm5UAphRdR"
API_SECRET = "AtWO6LIGP4XfuGW6OVegZIYh36Se8ySd9fNk4O8crORU3nPYfy"

ACCESS_TOKEN = "1006262723691405313-Bvg2U7D6daqNqjgOvA5w8xiqzukQoc"
ACCESS_TOKEN_SECRET = "OC2UP4JR4gedwvXQbrR2dbLFLJEtDTeNRVev3L8NRsa4r"


def tweet():
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    api.update_status(ds.validation())


sched = BlockingScheduler()


@sched.scheduled_job('cron', hour='9,12', minute='5')
def main():
    tweet()


sched.start()