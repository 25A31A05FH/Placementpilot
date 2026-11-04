from django.contrib import admin
from .models import Profile, Company, PlacementDrive, Application, Notification

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "department", "cgpa", "graduation_year", "leetcode_solved_count", "leetcode_verified")
    list_filter = ("role", "department", "leetcode_verified")
    search_fields = ("user__username", "user__email", "user__first_name", "leetcode_username")

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "industry", "location")
    search_fields = ("name", "industry")

@admin.register(PlacementDrive)
class PlacementDriveAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "deadline", "min_cgpa", "min_leetcode_solved", "is_active")
    list_filter = ("is_active", "company")
    search_fields = ("title", "company__name")

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("student", "drive", "status", "applied_at")
    list_filter = ("status",)

admin.site.register(Notification)
