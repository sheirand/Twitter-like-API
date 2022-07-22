from core.celery import app
from page.services import PostService


@app.task
def send_notification(email_list: list, page: str):
    """Email notification task for Celery"""
    PostService.send_email(email_list, page)

