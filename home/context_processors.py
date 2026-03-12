from .models import Notification, PickupRequest

def sidebar_counts(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()

        pending_orders = PickupRequest.objects.filter(
            collector=request.user,
            status="pending"
        ).count()

        return {
            "unread_notifications": unread_notifications,
            "pending_orders": pending_orders
        }

    return {}