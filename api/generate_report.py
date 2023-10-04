from .models import StoreStatus,  ReportStatus , StoreStatusLog , StoreReport , Store
from pytz import timezone as pytz_timezone
from datetime import timedelta
import csv
import os
import tempfile
from .time_calculation import get_last_one_hour_data , get_last_one_day_data , get_last_one_week_data

def generate_report_data(store):
    
    tz = store.timezone_str or 'America/Chicago'
    target_timezone = pytz_timezone(tz)
    
    # hard coding current time as max of all the logs
    time = StoreStatusLog.objects.all().order_by('-timestamp').first().timestamp
    local_time = time.astimezone(target_timezone)
    utc_timezone = pytz_timezone('UTC')
    utc_time = time.astimezone(utc_timezone)
    current_day = local_time.weekday()
    current_time = local_time

    
    # last one hour 
    last_one_hour_data = get_last_one_hour_data(store, utc_time, current_day, current_time)

    # last one day
    last_one_day_data = get_last_one_day_data(store, utc_time, current_day, current_time)

    # last week data
    last_one_week_data = get_last_one_week_data(store, utc_time, current_day, current_time)
    data = []
    data.append(store.pk)
    data.extend(list(last_one_hour_data.values()))
    data.extend(list(last_one_day_data.values()))
    data.extend(list(last_one_week_data.values()))
    return data


def generate_csv_file(report, csv_data):
    with tempfile.TemporaryDirectory() as temp_dir:
        # print(report)
        file_name = f"{report.report_id}.csv"
        temp_file_path = os.path.join(temp_dir, file_name)
        # print(csv_data)
        with open(temp_file_path, "w", newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["store_id", "last_one_hour uptime", "last_one_hour downtime", "last_one_day uptime", "last_one_day downtime", "last_one_week uptime", "last_one_week downtime"])
            for data in csv_data:
                csv_writer.writerow(data)
        report.report_url.save(file_name, open(temp_file_path, "rb"))
        report.status = ReportStatus.COMPLETED
        report.save()