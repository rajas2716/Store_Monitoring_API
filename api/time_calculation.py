from .models import StoreStatus,  ReportStatus , StoreStatusLog , StoreReport , Store , StoreTimings
import datetime
def get_last_one_hour_data(store, utc_time, current_day, local_time):
    last_one_hour_data = {"uptime" : 0 , "downtime" : 0}
    # checking if store is open in last one hour
    is_store_open = store.timings.filter(day=current_day,start_time__lte=local_time,end_time__gte=local_time - datetime.timedelta(hours=1)).exists()
    if not is_store_open:
        return last_one_hour_data
    last_one_hour_logs = store.status_logs.filter(timestamp__gte=utc_time - datetime.timedelta(hours=1)).order_by('timestamp')
    # checking if store is open in last one hour and last log status is active
    if last_one_hour_logs:            
        last_one_hour_log_status = last_one_hour_logs[0].status
        if last_one_hour_log_status == StoreStatus.ACTIVE:
            last_one_hour_data["uptime"] = 60
        else:
            last_one_hour_data["downtime"] = 60

    return last_one_hour_data

def get_last_one_day_data(store, utc_time, current_day, local_time):
    last_one_day_data = {"uptime" : 0 , "downtime" : 0}
    one_day_ago = current_day - 1 if current_day > 0 else 6
    # checking if store is open in last one day
    # is_store_open = store.timings.filter(day__gte=one_day_ago,day__lte=current_day,start_time__lte=local_time,end_time__gte=local_time).exists()
    # if not is_store_open:
    #     return last_one_day_data
    # getting all the logs in last one day
    last_one_day_logs = store.status_logs.filter(timestamp__gte=utc_time - datetime.timedelta(days=1)).order_by('timestamp')
    for log in last_one_day_logs:
        # checkig if log is in store business hours
        log_in_store_business_hours = store.timings.filter(
            day=log.timestamp.weekday(),
            start_time__lte=log.timestamp.time(),
            end_time__gte=log.timestamp.time()
            ).exists()
        # checking if log is in store business hours and status is active
        if not log_in_store_business_hours:
            continue
        if log.status == StoreStatus.ACTIVE:
            last_one_day_data["uptime"] += 1
        else:
            last_one_day_data["downtime"] += 1
    return last_one_day_data

def get_last_one_week_data(store, utc_time, current_day, current_time):
    last_one_week_data = {"uptime" : 0 , "downtime" : 0}
    one_week_ago = current_day - 7 if current_day > 0 else 0
    # checking if store is open in last one week
    # is_store_open = store.timings.filter(day__gte=one_week_ago,day__lte=current_day,start_time__lte=current_time,end_time__gte=current_time).exists()
    # if not is_store_open:
    #     return last_one_week_data
    # getting all the logs in last one week
    last_one_week_logs = store.status_logs.filter(timestamp__gte=utc_time - datetime.timedelta(days=7)).order_by('timestamp')
    for log in last_one_week_logs:
        # checkig if log is in store business hours
        log_in_store_business_hours = store.timings.filter(
            day=log.timestamp.weekday(),
            start_time__lte=log.timestamp.time(),
            end_time__gte=log.timestamp.time()
            ).exists()
        # checking if log is in store business hours and status is active
        if not log_in_store_business_hours:
            continue
        if log.status == StoreStatus.ACTIVE:
            last_one_week_data["uptime"] += 1
        else:
            last_one_week_data["downtime"] += 1
    
    return last_one_week_data

def get_all_data(store, utc_time, current_day, current_time):
    last_one_week_data = {"uptime" : 0 , "downtime" : 0}
    one_week_ago = current_day - 7 if current_day > 0 else 0
    # checking if store is open in last one week
    # is_store_open = store.timings.filter(day__gte=one_week_ago,day__lte=current_day,start_time__lte=current_time,end_time__gte=current_time).exists()
    # if not is_store_open:
    #     return last_one_week_data
    # getting all the logs in last one week
    last_one_week_logs = store.status_logs.filter(timestamp__gte=utc_time - datetime.timedelta(days=7)).order_by('timestamp')
    store_hours = StoreTimings.objects.filter(store_id = store.store_id)
    log_index = 0
    logs_len = len(last_one_week_logs)
    for log in last_one_week_logs:
        # checkig if log is in store business hours
        log_in_store_business_hours = store_hours.filter(
            day=log.timestamp.weekday(),
            start_time__lte=log.timestamp.time(),
            end_time__gte=log.timestamp.time()
            ).exists()
        # checking if log is in store business hours and status is active
        if not log_in_store_business_hours:
            continue
        if log.status == StoreStatus.ACTIVE:
            if index != len - 1:
                time_active = min(60 , log[log_index + 1].timestamp - log[index])
            else:
                time_active = min(60 , current_time - log.timestamp)
            last_one_week_data["uptime"] += 1
        else:
            last_one_week_data["downtime"] += 1
        index += 1
    
    return last_one_week_data