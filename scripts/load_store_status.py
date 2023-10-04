from api.models import StoreStatusLog , Store
import csv , datetime
from pytz import timezone as pytz_timezone


def run():
    with open('api/csv_data/store status.csv') as file:
        reader = csv.reader(file)
        all_rows = list(reader)
        print(len(all_rows))
        for row in reversed(all_rows):
            timestamp_without_utc = row[2].replace(" UTC", "")
            utc_timezone = pytz_timezone('UTC')
            timestamp_without_utc = datetime.datetime.strptime(timestamp_without_utc, '%Y-%m-%d %H:%M:%S.%f')
            timestamp_without_utc = timestamp_without_utc.astimezone(utc_timezone)
            if row[1] == "active":
                break
            if Store.objects.filter(store_id = row[0]).exists():
                store = StoreStatusLog(  
                store_id=row[0],
                status = (1 if row[1] == "active" else 0),
                timestamp = timestamp_without_utc
                )
                store.save()
            # print(row[0] , row[1] , timestamp_without_utc)