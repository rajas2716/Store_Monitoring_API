# Store Monitoring System
Video Link : https://www.loom.com/share/a110da1f72354a739a91f74d1cd02e86?sid=754544b1-456b-4432-8344-856b0689948e
## API Requirements
1)	{store_id}/trigger_report/
2)	get_report/
3)	Background task which precomputes the report for each store_id every hour and also updates it in the combined_report.csv file

Note: combined_report.csv is a file which contains report for all the stores combined in one CSV file.

Report Output Format
```
store_id, uptime_last_hour(in minutes), uptime_last_day(in hours), update_last_week(in hours), downtime_last_hour(in minutes), downtime_last_day(in hours), downtime_last_week(in hours)
```

Data provided
1)	Store Status (store_id, timestamp_utc, status)
2)	Store Timings (store_id, dayOfWeek(0=Monday, 6=Sunday), start_time_local, end_time_local)
3)	Store Zone (store_id, timezone_str)
Note: Data is loaded in the database sqlite where store_id is a foreign key in Store Status and Store Timings and primary key in Store Zone

## Tech Stack Used

Tech Stack Used
1)	Django Framework
2)	SQLite


## Packages Used

1)	Djangoreactframework
2)	Celery  (background task scheduler for precomputation)


# Logic for computing Business Hours OverLap
The logic for computing uptime is the same for past hour , day and week
1)	Uptime Last Hour
2)	Uptime Last Day
3)	Uptime Last Week

## Step 1) Fetch the Store status of the last one week as shown below 
```
last_one_week_logs = store.status_logs.filter(timestamp__gte=utc_time - datetime.timedelta(days=7)).order_by('timestamp')
```

Note: last_one_week_logs contains a list of objects which have a timestamp greater than or equal to past one week timestamp.
Note: utc_time is the current timestamp or the maximum timestamp from the status logs.


## Step 2) Fetch the Store timings for the particular store to check if the store was open for a particular Log in last_one_week_logs.

Note: This is done so that we do not have to look up in the database again and again.
```
store_hours = StoreTimings.objects.filter(store_id = store.store_id)
```

## Step 3) Traverse the last_one_week_logs array

For each log (store_id, timestamp_utc, status) we need to first check if the store was open on timestamp_utc.
```python
for log in last_one_week_logs:
        # checkig if log is in store business hours
        store_timezone = pytz_timezone(timezone)
        timestamp_utc = log.timestamp
        local_time = timestamp_utc.astimezone(store_timezone)
        log_in_store_business_hours = store_hours.filter(
            day=log.timestamp.weekday(),
            start_time__lte=local_time,
            end_time__gte=local_time
            ).exists()
```
Note: Store Timings contains time in local_time but the timestamp_utc from last_one_week_logs is in UTC time , hence timestamp_utc is converted to localtime.

log_in_store_business_hours (True or False) checks if the status timestamp lies in between the store timings or not.

## Step 4) If the timestamp does not lie in business hours on that day of the store , then we will simply go to the next log in last_one_week_logs.
```python
if not log_in_store_business_hours:
            continue
```

## Step 5) If the timestamp lies between the business hours on that day of the store , then we must check if the status was active or not active.
```python
status_interval_time = 0;
        if index != len - 1:
            status_interval_time = min(60 , ((log[log_index + 1].timestamp - log[index].timestamp).seconds)/60)
        else:
            status_interval_time = min(60 , store_time.end_time - local_time.time())
        if log.status == StoreStatus.ACTIVE:
            last_one_week_data["uptime"] += status_interval_time
        else:
            last_one_week_data["downtime"] -= status_interval_time
        index += 1
```

Note: We increment the uptime or decrement the downtime by the status_interval_time
Status_interval_time is calculated by the difference between two status or 60 mins whichever is lesser

## Step 6) Likewise we can calculate uptime for past hour and past day by checking the difference between status time and current time in the same loop

```
if log.status == StoreStatus.ACTIVE:
            if current_time - timestamp_utc <= timedelta(hours = 1):
                last_one_week_data["uptime_hour"] += status_interval_time
                last_one_week_data["uptime_day"] += status_interval_time
                last_one_week_data["uptime_week"] += status_interval_time
            if current_time - timestamp_utc <= timedelta(days = 1):
                last_one_week_data["uptime_day"] += status_interval_time
                last_one_week_data["uptime_week"] += status_interval_time
            if current_time - timestamp_utc <= timedelta(days = 7):
                last_one_week_data["uptime_week"] += status_interval_time
        else:
            if current_time - timestamp_utc <= timedelta(hours = 1):
                last_one_week_data["uptime_hour"] -= status_interval_time
                last_one_week_data["uptime_day"] -= status_interval_time
                last_one_week_data["uptime_week"] -= status_interval_time
            if current_time - timestamp_utc <= timedelta(days = 1):
                last_one_week_data["uptime_day"] -= status_interval_time
                last_one_week_data["uptime_week"] -= status_interval_time
            if current_time - timestamp_utc <= timedelta(days = 7):
                last_one_week_data["uptime_week"] -= status_interval_time
```

# Background Task (for precomputing as the store status data gets updated)

A celery task which runs every hour to check if there is any new data.
```python
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
    generate_combined_csv_file(report, csv_data)
```

Task calculates uptime and downtime for each store and stores it in the database for each store_id.

Then generate_combined_csv_file can go and update data in corresponding rows of the csv file.

Note: One Precomputation function precomputes and stores combined report of all the stores in a csv file beforehand.
Celery task just updates selected data for selected stores every hour.
## Sample Outputs
1) Trigger_report/
![trigger](https://github.com/rajas2716/Store_Monitoring_API/blob/master/Documentation/trigger.png)

2) getReport/
![getReport](https://github.com/rajas2716/Store_Monitoring_API/blob/master/Documentation/getReport.png)

3) combinedReport
![combinedReport](https://github.com/rajas2716/Store_Monitoring_API/blob/master/Documentation/combinedReport.png)
