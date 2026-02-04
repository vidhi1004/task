from celery import shared_task
import time

@shared_task
def send_conformation(order_id):
    time.sleep(10) 
    print(f"Order {order_id} confirmation email sent.")