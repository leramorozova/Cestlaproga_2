import datasetter as ds
from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler()


@sched.scheduled_job('cron', hour="00, 03", minute="45")
def main():
    ds.tweet()

sched.start()