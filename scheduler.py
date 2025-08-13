from apscheduler.schedulers.blocking import BlockingScheduler
from zoneinfo import ZoneInfo

from main import run_broadcast


# 毎朝 7 時に配信を開始するスケジューラーを起動する
def start_schedule():
    scheduler = BlockingScheduler(timezone=ZoneInfo("Asia/Tokyo"))
    scheduler.add_job(run_broadcast, "cron", hour=7, minute=0)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        # 手動で停止した場合はそのまま終了
        pass


if __name__ == "__main__":
    start_schedule()
