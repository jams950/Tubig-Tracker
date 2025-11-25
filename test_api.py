import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tubig_tracker.settings')
django.setup()

from tubig_tracker_app.models import Report
from tubig_tracker_app.views import get_all_complaints
from django.http import HttpRequest
import json

def test_api_locally():
    print("Testing API endpoint locally...")
    
    # Create a mock request
    request = HttpRequest()
    
    # Call the view function directly
    response = get_all_complaints(request)
    
    # Parse the JSON response
    data = json.loads(response.content.decode('utf-8'))
    
    print(f"API returned {len(data)} reports")
    
    for i, report in enumerate(data[:3]):  # Show first 3 reports
        print(f"\nReport {i+1}:")
        print(f"  ID: {report['id']}")
        print(f"  Title: {report['title']}")
        print(f"  Status: {report['status']}")
        print(f"  User: {report['user']}")
        print(f"  Coordinates: {report['latitude']}, {report['longitude']}")
        print(f"  Area: {report['area']}")
        print(f"  Barangay: {report['barangay']}")

if __name__ == "__main__":
    test_api_locally()