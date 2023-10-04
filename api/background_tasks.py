# tasks.py
from celery import task
from .models import StoreStatus,  ReportStatus , StoreStatusLog , StoreReport , Store
from datetime import datetime,timezone
from .generate_report import generate_report_data , generate_csv_file
import uuid
@task
def hourly_precomputation():
    # Your task code here
    utc_time = datetime.now(timezone.utc)
    last_one_hour_logs = store.status_logs.filter(timestamp__gte=utc_time - datetime.timedelta(hours = 1)).order_by('timestamp')
    csv_data = []
    for log in last_one_hour_logs:
        store_id = log.store_id
        store = Store.objects.filter(store_id = store_id).first()
        report = StoreReport.objects.create(store=store, status=ReportStatus.PENDING , report_id=str(uuid.uuid4()))
        data = generate_report_data(store)
        csv_data.append(data)
        generate_csv_file(report, csv_data)
