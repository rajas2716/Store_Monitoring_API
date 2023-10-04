from api.models import StoreTimings , Store
import csv , datetime
from pytz import timezone as pytz_timezone


def run():
    with open('api/csv_data/store timings.csv') as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header

        StoreTimings.objects.all().delete()
        rowNum = 0;
        for row in reader:
            print(rowNum)
            startTime = datetime.datetime.strptime(row[2], '%H:%M:%S')
            endTime = datetime.datetime.strptime(row[3], '%H:%M:%S')
            if Store.objects.filter(store_id = row[0]).exists():
                store = StoreTimings(  
                store_id=row[0],
                day = row[1],
                start_time = startTime,
                end_time = endTime
                )
                store.save()
            rowNum+=1