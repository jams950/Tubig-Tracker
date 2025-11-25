from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tubig_tracker_app.models import Report

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample reports for testing'

    def handle(self, *args, **options):
        # Get or create a user for the reports
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'role': 'user'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(f'Created test user: {user.username}')

        # Sample reports data with Biliran coordinates
        sample_reports = [
            {
                'title': 'Water Supply Interruption in Brgy. Centro',
                'description': 'No water supply for 3 days in our area. Residents are having difficulty accessing clean water.',
                'latitude': 11.5411,
                'longitude': 124.5405,
                'barangay': 'Centro',
                'issue_type': 'Water Supply',
                'location': 'Brgy. Centro, Naval, Biliran',
                'address': 'Centro',
                'status': 'Pending'
            },
            {
                'title': 'Broken Water Pipe on Main Street',
                'description': 'Large water pipe burst causing flooding and water wastage.',
                'latitude': 11.5500,
                'longitude': 124.5300,
                'barangay': 'Poblacion',
                'issue_type': 'Infrastructure',
                'location': 'Main Street, Poblacion, Naval',
                'address': 'Poblacion',
                'status': 'In Progress'
            },
            {
                'title': 'Low Water Pressure in Residential Area',
                'description': 'Water pressure is very low, making it difficult to use water for daily activities.',
                'latitude': 11.5300,
                'longitude': 124.5500,
                'barangay': 'San Pablo',
                'issue_type': 'Water Pressure',
                'location': 'Residential Area, San Pablo, Naval',
                'address': 'San Pablo',
                'status': 'Pending'
            },
            {
                'title': 'Contaminated Water Source',
                'description': 'Water appears cloudy and has unusual taste. Possible contamination.',
                'latitude': 11.5600,
                'longitude': 124.5200,
                'barangay': 'Libuton',
                'issue_type': 'Water Quality',
                'location': 'Libuton, Naval, Biliran',
                'address': 'Libuton',
                'status': 'Resolved'
            },
            {
                'title': 'Water Meter Not Working',
                'description': 'Water meter stopped working, unable to track water usage.',
                'latitude': 11.5450,
                'longitude': 124.5350,
                'barangay': 'Calumpang',
                'issue_type': 'Meter Issue',
                'location': 'Calumpang, Naval, Biliran',
                'address': 'Calumpang',
                'status': 'In Progress'
            }
        ]

        created_count = 0
        for report_data in sample_reports:
            report, created = Report.objects.get_or_create(
                title=report_data['title'],
                defaults={
                    **report_data,
                    'reporter': user
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created report: {report.title}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample reports')
        )
        
        total_reports = Report.objects.count()
        self.stdout.write(f'Total reports in database: {total_reports}')