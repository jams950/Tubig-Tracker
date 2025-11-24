# IMPORTS
from django.shortcuts import render, redirect, get_object_or_404
import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.db.models.functions import ExtractMonth
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import date
import json
import random

from .models import User, Complaint, ComplaintPhoto, Announcement, Feedback, Report, Notification, WaterBill, Municipality

logger = logging.getLogger(__name__)
from .forms import UserRegistrationForm, ComplaintForm

# AUTHENTICATION & HOME
def intro(request):
    return render(request, 'intro.html')

def home(request):
    return render(request, 'Home.html')

def home_view(request):
    return render(request, 'login.html')



def _obsolete_login_view(request):
    """Deprecated duplicate login view kept for reference. Real implementation is below."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if getattr(user, 'role', None) == 'admin' or user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

# DASHBOARDS
@login_required
def dashboard_view(request):
    print(f"DEBUG: Dashboard view accessed")
    print(f"DEBUG: User authenticated: {request.user.is_authenticated}")
    print(f"DEBUG: User: {request.user}")
    print(f"DEBUG: User ID: {request.user.id if request.user.is_authenticated else 'None'}")
    print(f"DEBUG: Session key: {request.session.session_key}")
    
    user = request.user
    if getattr(user, 'role', None) == 'admin':
        print("DEBUG: User is admin, redirecting to admin dashboard")
        return redirect('admin_dashboard')

    # Use Report instead of Complaint
    reports = Report.objects.filter(reporter=user).order_by('-created_at')
    print(f"DEBUG: Found {reports.count()} reports for user")

    context = {
        'user': user,
        'total_reports': reports.count(),
        'pending': reports.filter(status='Pending').count(),
        'in_progress': reports.filter(status='In Progress').count(),
        'resolved': reports.filter(status='Resolved').count(),
        'recent_updates': reports[:5],  # optionally show recent reports
    }

    print("DEBUG: Rendering dashboard template")
    return render(request, 'user/dashboard.html', context)

# ------------------------------
# Admin Dashboard
# ------------------------------
@login_required
def admin_dashboard(request):
    today = timezone.localdate()
    current_year = today.year
    
    # Use Report model for all stats to match the map
    total_reports = Report.objects.count()
    resolved_reports = Report.objects.filter(status='Resolved').count()
    pending_reports = Report.objects.filter(status='Pending').count()
    in_progress_reports = Report.objects.filter(status='In Progress').count()
    active_users = User.objects.count()

    # Reports per month
    reports_per_month = (
        Report.objects.filter(created_at__year=current_year)
        .annotate(month=ExtractMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    reports_per_month_data = [0] * 12
    for entry in reports_per_month:
        reports_per_month_data[entry['month'] - 1] = entry['count']

    # User growth per month
    user_growth_per_month = (
        User.objects.filter(date_joined__year=current_year)
        .annotate(month=ExtractMonth('date_joined'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    user_growth_data = [0] * 12
    for entry in user_growth_per_month:
        user_growth_data[entry['month'] - 1] = entry['count']

    # System notifications
    system_notifications = []
    latest_user = User.objects.order_by('-date_joined').first()
    latest_report = Report.objects.order_by('-created_at').first()
    if latest_user:
        system_notifications.append(f"👤 New user registered: {latest_user.username}")
    if latest_report:
        system_notifications.append(f"📝 New report received: {latest_report.title}")
    system_notifications.append("✅ System check completed successfully.")

    context = {
        'total_users': active_users,
        'total_reports': total_reports,
        'resolved_reports': resolved_reports,
        'pending_reports': pending_reports,
        'in_progress_reports': in_progress_reports,
        'reports_per_month_data': reports_per_month_data,
        'user_growth_data': user_growth_data,
        'system_notifications': system_notifications,
    }
    return render(request, 'admin/admin_dashboard.html', context)

# USER REPORTS
@login_required
def my_reports(request):
    reports = Report.objects.filter(reporter=request.user).order_by('-created_at')
    return render(request, 'user/my_reports.html', {'reports': reports})



@login_required
def report_detail_view(request, pk):
    report = get_object_or_404(Complaint, pk=pk)
    return render(request, 'user/report_detail.html', {'report': report})

# COMPLAINT SUBMISSION
@login_required
def add_complaint_view(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            if complaint.latitude is None or complaint.longitude is None:
                messages.error(request, "Please select a location on the map before submitting.")
                return redirect('add_complaint')
            complaint.save()
            photo_file = request.FILES.get('photo')
            if photo_file:
                ComplaintPhoto.objects.create(complaint=complaint, photo=photo_file)
            
            full_location = f"Brgy. {complaint.barangay}, {complaint.area}"
            if complaint.purok:
                full_location = f"Purok {complaint.purok}, " + full_location
            
            Report.objects.create(
                title=complaint.title,
                description=complaint.description,
                reporter=request.user,
                issue_type=complaint.area or "N/A",
                location=full_location,
                address=complaint.barangay,
                barangay=complaint.barangay,
                latitude=complaint.latitude,
                longitude=complaint.longitude,
                image=photo_file if photo_file else None,
                status='Pending'
            )
            messages.success(request, "✅ Complaint submitted successfully!")
            return redirect('my_reports')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ComplaintForm()
    return render(request, 'user/add_complaint.html', {'form': form})
@login_required
def api_user_reports(request):
    # Fetch reports submitted by the logged-in user
    reports = Report.objects.filter(reporter=request.user).order_by('-created_at')

    data = [
        {
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'status': r.status,
            'latitude': r.latitude,
            'longitude': r.longitude,
            'date_submitted': r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for r in reports
    ]
    return JsonResponse({'reports': data})


# OTHER USER PAGES
@login_required
def water_status(request):
    return render(request, 'user/water_status.html')

@login_required
def my_report_summary(request):
    return render(request, 'user/my_report_summary.html')

@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'user/notifications.html', {'notifications': user_notifications})

@login_required
def profile(request):
    return render(request, 'user/profile.html')

@login_required
def settings(request):
    return render(request, 'user/settings.html')

# ADMIN USER MANAGEMENT
@login_required
def view_users(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        if user_id:
            user = get_object_or_404(User, id=user_id)
            user.username = username
            user.email = email
            user.role = role
            user.save()
        else:
            password = request.POST.get('password')
            User.objects.create_user(username=username, email=email, password=password, role=role)
        return redirect('view_users')
    users = User.objects.all()
    return render(request, 'admin/admin_manage_users.html', {'users': users})

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('view_users')

# ADMIN REPORT MANAGEMENT
@login_required
def admin_manage_reports(request):
    reports = Report.objects.all().order_by('-created_at')
    return render(request, 'admin/admin_manage_reports.html', {'reports': reports})

@require_http_methods(["POST"])
def update_report_status(request, report_id):
    try:
        data = json.loads(request.body)
        status = data.get('status')
        remarks = data.get('remarks', '')
        report = Report.objects.get(id=report_id)
        report.status = status
        report.remarks = remarks
        report.save()
        return JsonResponse({'success': True, 'status': status, 'id': report_id})
    except Report.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Report not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def delete_report_admin(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'POST':
        report.delete()
        messages.success(request, "Report deleted.")
    return redirect('admin_manage_reports')

# ADMIN COMPLAINT ACTIONS
@login_required
def update_status(request, id):
    complaint = get_object_or_404(Complaint, id=id)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status:
            complaint.status = new_status
            complaint.save()
            messages.success(request, f"Complaint '{complaint.title}' updated to {new_status}.")
    return redirect('admin_dashboard')

@login_required
def approve_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    complaint.status = 'Approved'
    complaint.save()
    messages.success(request, f"Complaint #{complaint.id} has been approved.")
    return redirect('admin_dashboard')

@login_required
def resolve_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    complaint.status = 'Resolved'
    complaint.save()
    messages.success(request, f"Complaint #{complaint.id} marked as resolved.")
    return redirect('admin_dashboard')

@login_required
def delete_complaint(request, id):
    complaint = get_object_or_404(Complaint, id=id)
    complaint.delete()
    messages.success(request, f"Complaint '{complaint.title}' deleted successfully.")
    return redirect('admin_dashboard')

# ADMIN ANNOUNCEMENT MANAGEMENT
@login_required
def admin_manage_announcements(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'admin/admin_manage_announcements.html', {'announcements': announcements})

@login_required
def create_announcement_admin(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        if title and message:
            Announcement.objects.create(title=title, message=message, created_at=timezone.now())
        return redirect('admin_manage_announcements')
    return redirect('admin_manage_announcements')

@login_required
def delete_announcement_admin(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if request.method == 'POST':
        announcement.delete()
        return redirect('admin_manage_announcements')
    return redirect('admin_manage_announcements')

# ADMIN SETTINGS & PROFILE
@login_required
def admin_settings_view(request):
    if not request.user.is_superuser and getattr(request.user, 'role', None) != 'admin':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('dashboard')
    if request.method == 'POST':
        messages.success(request, "Settings updated successfully.")
        return redirect('admin_settings_view')
    context = {
        'site_title': "Tubig Tracker",
        'contact_email': "admin@tubigtracker.com",
        'system_status_message': "Water supply is currently normal.",
    }
    return render(request, 'admin/admin_settings.html', context)

@login_required
def admin_profile_view(request):
    if not request.user.is_superuser and getattr(request.user, 'role', None) != 'admin':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('dashboard')
    user_profile = request.user
    if request.method == 'POST':
        user_profile.first_name = request.POST.get('first_name', user_profile.first_name)
        user_profile.last_name = request.POST.get('last_name', user_profile.last_name)
        user_profile.email = request.POST.get('email', user_profile.email)
        user_profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('admin_profile_view')
    return render(request, 'admin/admin_profile.html', {'user_profile': user_profile})

# ADMIN FEEDBACK MANAGEMENT
def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@staff_member_required
@csrf_exempt
def ajax_update_feedback(request, feedback_id):
    if request.method == "POST":
        feedback = get_object_or_404(Feedback, id=feedback_id)
        comment = request.POST.get('comment', '').strip()
        rating = request.POST.get('rating', '').strip()
        status = request.POST.get('status', '').strip()
        feedback.comment = comment
        feedback.rating = int(rating) if rating.isdigit() else feedback.rating
        feedback.status = status
        feedback.save()
        return JsonResponse({'success': True, 'message': 'Feedback updated successfully!'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def admin_feedback_ratings(request):
    feedback_list = Feedback.objects.all().order_by('-created_at')
    average_rating = feedback_list.aggregate(Avg('rating'))['rating__avg'] or 0
    critical_feedback_count = feedback_list.filter(rating__lte=2).count()
    areas = feedback_list.values_list('issue_area', flat=True).distinct()
    context = {
        'feedback_list': feedback_list,
        'average_rating': round(average_rating, 2),
        'critical_feedback_count': critical_feedback_count,
        'areas': areas,
    }
    return render(request, 'admin/admin_feedback_ratings.html', context)

@csrf_exempt
def update_feedback(request, feedback_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        feedback = get_object_or_404(Feedback, id=feedback_id)
        feedback.comment = data.get('comment', feedback.comment)
        feedback.rating = data.get('rating', feedback.rating)
        feedback.status = data.get('status', feedback.status)
        feedback.sentiment = feedback.sentiment_label
        feedback.save()
        return JsonResponse({'success': True, 'message': 'Feedback updated successfully.'})

# BILLS
@login_required
def mark_bill_paid(request, bill_id):
    try:
        bill = WaterBill.objects.get(id=bill_id, user=request.user)
        bill.status = 'Paid'
        bill.date_paid = date.today()
        bill.payment_method = 'GCash'
        bill.reference_no = f'TXN-{random.randint(100000, 999999)}'
        bill.save()
        return JsonResponse({'success': True})
    except WaterBill.DoesNotExist:
        return JsonResponse({'success': False}, status=404)

# API ENDPOINTS
@csrf_exempt

def get_all_complaints(request):
    reports = Report.objects.all().select_related('reporter').order_by('-created_at')
    data = [
        {
            'id': r.id,
            'user': r.reporter.username if r.reporter else 'Unknown',
            'title': r.title,
            'status': r.status,
            'latitude': float(r.latitude) if r.latitude else None,
            'longitude': float(r.longitude) if r.longitude else None,
            'area': r.issue_type or '',
            'barangay': r.barangay or '',
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for r in reports
    ]
    return JsonResponse(data, safe=False)
@login_required
def get_complaints(request):
    # Only fetch reports where the user is the reporter
    reports = Report.objects.filter(reporter=request.user)  

    data = [
        {
            "id": r.id,
            "title": r.title,
            "status": r.status.strip(),  # make sure to remove whitespace
            "latitude": float(r.latitude) if r.latitude else None,
            "longitude": float(r.longitude) if r.longitude else None,
            "date_reported": r.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for r in reports
    ]
    return JsonResponse(data, safe=False)




def api_reports(request):
    status = request.GET.get('status', '')
    user_filter = request.GET.get('user', '')
    search = request.GET.get('q', '')
    municipalities = request.GET.get('municipalities', '').split(',') if request.GET.get('municipalities') else []
    reports = Complaint.objects.all()
    if status:
        reports = reports.filter(status=status)
    if user_filter:
        reports = reports.filter(user__username__icontains=user_filter)
    if search:
        reports = reports.filter(Q(title__icontains=search) | Q(description__icontains=search))
    if municipalities:
        reports = reports.filter(area__in=municipalities)
    report_data = [
        {
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'status': r.status,
            'latitude': r.latitude,
            'longitude': r.longitude,
            'date_submitted': r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user': {'username': r.user.username, 'email': r.user.email},
            'photos': [{'url': p.photo.url} for p in r.complaintphoto_set.all()]
        }
        for r in reports
    ]
    return JsonResponse({'reports': report_data})

def api_report_detail(request, report_id):
    try:
        r = Complaint.objects.get(id=report_id)
        data = {
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'status': r.status,
            'latitude': r.latitude,
            'longitude': r.longitude,
            'date_submitted': r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user': {'username': r.user.username, 'email': r.user.email},
            'photos': [{'url': p.photo.url} for p in r.complaintphoto_set.all()],
        }
        return JsonResponse(data)
    except Complaint.DoesNotExist:
        return JsonResponse({'error': 'Report not found'}, status=404)

# PUBLIC PAGES
def report_issue(request):
    return render(request, 'report_issue.html')

def live_map(request):
    return render(request, 'live_map.html')

def view_report(request, id):
    report = get_object_or_404(Report, pk=id)
    return render(request, 'user/report_detail.html', {'report': report})

def delete_report(request, id):
    report = get_object_or_404(Report, pk=id)
    report.delete()
    return redirect('manage_reports')

@login_required
def add_report_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        photo = request.FILES.get('photo')

        if not title or not description:
            messages.error(request, "Please fill in all required fields.")
            return redirect('add_report')
        if not latitude or not longitude:
            messages.error(request, "Please select a location on the map.")
            return redirect('add_report')

        report = Report.objects.create(
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            image=photo if photo else None
        )

        messages.success(request, "Your report has been submitted successfully.")
        return redirect('dashboard')

    return render(request, 'user/add_complaint.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        print(f"Login attempt: '{username}' / '{password}'")
        
        if not username or not password:
            messages.error(request, 'Please enter username and password')
            return render(request, 'login.html')
        
        user = authenticate(request, username=username, password=password)
        print(f"Auth result: {user}")
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'user')
        
        print(f"DEBUG: Registration attempt - Username: {username}, Email: {email}, Role: {role}")
        
        # Validate required fields
        if not username or not email or not password:
            messages.error(request, 'All fields are required')
            return render(request, 'login.html')
        
        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'login.html')
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'login.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'login.html')
        
        try:
            # Create user with role
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Set role and admin status
            if role == 'admin':
                user.role = 'admin'
                user.is_staff = True
            else:
                user.role = 'user'
            
            user.save()
            print(f"DEBUG: User created successfully: {user.username} with role: {user.role}")
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
            
        except Exception as e:
            print(f"DEBUG: Registration error: {str(e)}")
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'login.html')
def technician_management(request):
    return render(request, 'technician_management.html')