from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # ------------------------------
    # LANDING PAGE & AUTHENTICATION
    # ------------------------------
    path('', views.intro, name='intro'),  # intro animation page
    path('home/', views.home, name='home'),  # main home page
    #path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # ------------------------------
    # DASHBOARDS
    # ------------------------------
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ------------------------------
    # USER REPORTS
    # ------------------------------
    path('my-reports/', views.my_reports, name='my_reports'),
    # path('report/<int:pk>/', views.report_detail_view, name='report-detail'),
    path('report/<int:pk>/delete/', views.delete_report, name='delete_report'),

    # ------------------------------
    # COMPLAINT SUBMISSION
    # ------------------------------
    path('complaint/add/', views.add_complaint_view, name='add_complaint'),

    # ------------------------------
    # ADMIN STATUS UPDATES
    # ------------------------------
    
    path('complaint/<int:complaint_id>/approve/', views.approve_complaint, name='approve_complaint'),
    path('complaint/<int:complaint_id>/resolve/', views.resolve_complaint, name='resolve_complaint'),
    path('delete_complaint/<int:id>/', views.delete_complaint, name='delete_complaint'),

    # ------------------------------
    # ADMIN REPORT MANAGEMENT
    # ------------------------------
   path('update-report-status/<int:report_id>/', views.update_report_status, name='update_report_status_ajax'),
    path('manage/reports/delete/<int:report_id>/', views.delete_report_admin, name='delete_report_admin'),

    # ------------------------------
    # ADMIN ANNOUNCEMENT MANAGEMENT
    # ------------------------------
    path('manage/announcements/', views.admin_manage_announcements, name='admin_manage_announcements'),
    path('manage/announcements/create/', views.create_announcement_admin, name='create_announcement_admin'),
    # path('manage/announcements/edit/<int:announcement_id>/', views.edit_announcement_admin, name='edit_announcement_admin'),
    path('manage/announcements/delete/<int:announcement_id>/', views.delete_announcement_admin, name='delete_announcement_admin'),

    # ------------------------------
    # ADMIN SETTINGS & PROFILE
    # ------------------------------
    path('manage/settings/', views.admin_settings_view, name='admin_settings_view'),
    path('manage/profile/', views.admin_profile_view, name='admin_profile_view'),

    # ------------------------------
    # USER FEATURES / PAGES
    # ------------------------------
    path('water_status/', views.water_status, name='water_status'),
    path('my_report_summary/', views.my_report_summary, name='my_report_summary'),
    path('notifications/', views.notifications, name='notifications'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),

    # ------------------------------
    # ADMIN USER MANAGEMENT
    # ------------------------------
    path('manage/users/', views.view_users, name='view_users'),
    path('manage/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('mark-bill-paid/<int:bill_id>/', views.mark_bill_paid, name='mark_bill_paid'),
    

    # ------------------------------
    # REPORT & COMPLAINT API
    # ------------------------------
    path('api/complaints/', views.get_complaints, name='get_complaints'),
   path('api/all-complaints/', views.get_all_complaints, name='get_all_complaints'),

    # ------------------------------
    # ADDITIONAL REPORT PAGES
    # ------------------------------
    path('add-complaint/', views.add_complaint_view, name='add_complaint'),
    path('add_report/', views.add_report_view, name='add_report'),
   path('manage/reports/', views.admin_manage_reports, name='admin_manage_reports'),

    #path('manage-reports/', views.manage_reports, name='manage_reports'),
    path('report/<int:id>/', views.view_report, name='view_report'),
    path('report/<int:id>/delete/', views.delete_report, name='delete_report'),
    path('api/my-reports/', views.api_user_reports, name='api_user_reports'),
    



    # Authentication
    #path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Dashboards
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # path('features/', views.features, name='features'),
    # path('how-it-works/', views.how_it_works, name='how_it_works'),
    # path('about/', views.about, name='about'),
    # path('contact/', views.contact, name='contact'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('report-issue/', views.report_issue, name='report_issue'),
    path('live-map/', views.live_map, name='live_map'),
    # ... (keep all your other URL patterns exactly as they are)
   path('technician_management/', views.technician_management, name='technician_management'),
]