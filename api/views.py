from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import action ,api_view
from .models import Store , StoreReport , ReportStatus
from .generate_report import generate_report_data , generate_csv_file
from .serializers import ReportSerializer
from rest_framework.generics import get_object_or_404
from django.conf import settings
import uuid
# Create your views here.
@api_view(['GET'])
def trigger_report(request, store_id):
    store = Store.objects.filter(store_id = store_id).first()
    report = StoreReport.objects.create(store=store, status=ReportStatus.PENDING , report_id=str(uuid.uuid4()))
    csv_data = []
    data = generate_report_data(store)
    csv_data.append(data)
    # print(csv_data)
    generate_csv_file(report, csv_data)
    return Response(status=200, data={"status" : "Running" , "report_id": {report.report_id}})

@api_view(['POST'])
def get_report(request):
    serializedRequest = ReportSerializer(data=request.data)
    serializedRequest.is_valid(raise_exception=True)
    report_id = serializedRequest.validated_data.get("report_id")
    report = get_object_or_404(StoreReport, report_id=report_id)
    if report.status == ReportStatus.COMPLETED:
        report_url = settings.MEDIA_ROOT + "/" + report.report_url.name
        return Response(status=200, data={"report_url": report_url, "status": "Complete"})
    else:
        return Response(status=200, data={"status": "Running"}) 