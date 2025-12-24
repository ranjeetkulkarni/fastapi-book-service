from celery import Celery
from config import Config

# 1. Initialize Celery
# "c_worker" is just a name we give this worker instance
c_celery = Celery(
    "c_worker",
    broker=Config.REDIS_URL,
    backend=Config.REDIS_URL
)

# 2. Define the Task
# @c_celery.task() tells Celery "This is a job you can accept"
@c_celery.task()
def send_email_task(email: str, link: str):
    """
    This runs in the Background Worker process.
    It receives the email and link, and prints them.
    """
    # Simulate sending email by printing to the worker console
    print(f"--------------------------------")
    print(f"CELERY WORKER: VERIFICATION LINK FOR {email}:")
    print(link)
    print(f"--------------------------------")
    
    # FUTURE: When you want to send real emails, you will use asgiref here
    # from asgiref.sync import async_to_sync
    # from mail import send_verification_email
    # async_to_sync(send_verification_email)(email, link)