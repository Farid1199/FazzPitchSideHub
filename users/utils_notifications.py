"""
Helper function for creating notifications throughout the app.
"""
from .models import Notification


def create_notification(user, message, notification_type='system', action_url=''):
    """
    Create an in-app notification for a user.
    """
    Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
        action_url=action_url
    )
