from api.models import StoreStatus,  ReportStatus , StoreStatusLog , StoreReport , Store
from datetime import datetime,timezone
from api.generate_report import generate_report_data , generate_csv_file
import tempfile , csv , os

def run():
    # Your task code here
    store_ids = Store.objects.values_list('store_id', flat=True).distinct()[:10]
    csv_data = []
    for store_id in store_ids:
        store = Store.objects.filter(store_id = store_id).first()
        data = generate_report_data(store)
        csv_data.append(data)
        # print(csv_data)
        print("YES")
    generate_combined_csv(csv_data)

def generate_combined_csv(csv_data):
    print(csv_data)
    with tempfile.TemporaryDirectory() as temp_dir:
        # print(report)
        file_name = "combined_report.csv"
        temp_file_path = os.path.join(temp_dir, file_name)
        # print(csv_data)
        temp_file_path = "/home/rajas/LoopInterview/StoreMonitor/reports/combined_report.csv"
        with open(temp_file_path, "w", newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["store_id", "last_one_hour uptime", "last_one_hour downtime", "last_one_day uptime", "last_one_day downtime", "last_one_week uptime", "last_one_week downtime"])
            for data in csv_data:
                print(data)
                csv_writer.writerow(data)
        # report.report_url.save(file_name, open(temp_file_path, "rb"))
        # report.status = ReportStatus.COMPLETED
        # report.save()