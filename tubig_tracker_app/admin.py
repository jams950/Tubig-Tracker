# tubig_tracker_app/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Complaint, ComplaintPhoto


# ------------------------------
# Inline for Complaint Photos
# ------------------------------
class ComplaintPhotoInline(admin.TabularInline):
    model = ComplaintPhoto
    extra = 1  # show one empty form for new photo upload
    fields = ('photo',)
    readonly_fields = []  # you can add ['photo'] here if you want view-only


# ------------------------------
# Complaint Admin
# ------------------------------
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'area', 'user', 'status', 'created_at')
    list_filter = ('status', 'area', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    inlines = [ComplaintPhotoInline]
    ordering = ('-created_at',)

    # Optional: display recent status color-coded
    def get_status_display_colored(self, obj):
        color_map = {
            'pending': 'orange',
            'in_progress': 'blue',
            'completed': 'green',
            'false': 'red',
        }
        color = color_map.get(obj.status, 'black')
        return format_html(f'<b><span style="color:{color}">{obj.get_status_display()}</span></b>')
    get_status_display_colored.short_description = "Status"


# ------------------------------
# Complaint Photo Admin
# ------------------------------
@admin.register(ComplaintPhoto)
class ComplaintPhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'complaint', 'photo')
    search_fields = ('complaint__title',)
