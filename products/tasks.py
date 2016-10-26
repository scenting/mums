from celery import shared_task


@shared_task
def clean_order(order_id):
    print('Cleaning order')
