from django.contrib import admin
from app.models import Report, Attachment, Folder, UserGroupRequest, Registration

admin.site.register(Report)
admin.site.register(Attachment)
admin.site.register(Folder)
admin.site.register(UserGroupRequest)
admin.site.register(Registration)
