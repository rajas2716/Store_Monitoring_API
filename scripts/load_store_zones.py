from api.models import Store
import csv


def run():
    with open('api/csv_data/store zones.csv') as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header

        Store.objects.all().delete()
        rowNum = 0;

        for row in reader:
            store = Store(  
            store_id=row[0],
            timezone_str = row[1],
            )
            store.save()