import os, re, string, random
from django.core.files import File
from django.shortcuts import render
import errno
from app.encryption import encrypt_file, hash
from app.forms import *
from app.models import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from SecureWitness import settings
from django.db.models import Q


def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    '''
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

def report_group(currUser, report):
    for g1 in list(currUser.groups.all()):
        for g2 in list(report.groups.all()):
            if g1 == g2:
                return True
    return False

def hasAccess(currUser, user_name_slug=None, folder_slug=None, report_slug=None, edit=False):
    if user_name_slug and currUser.username != user_name_slug:
        return False
    if report_slug:
        report = Report.objects.filter(id=report_slug).first()
        if not report:
            return False
        if report.private and report.user != currUser and not is_admin(currUser) and not report_group(currUser, report):
            return False
        if edit and report.user != currUser:
            return False
    return True


def is_admin(user):
    return user.groups.filter(id=1).exists()


def home(request):
    currUser = request.user
    # Create a list of all reports
    if is_admin(currUser):
        reports = Report.objects.all()
    else:
        reports = Report.objects.filter(private=False)
    groups = currUser.groups.all()
    # Direct the user to the SecureWitness homepage
    return render(request, 'app/home.html',
                  {'reports': reports, 'user': currUser, 'groups': groups, 'admin': is_admin(currUser)})


def register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            # Save the user's form data to the database
            currUser = user_form.save()
            # Hash the password with the set_password method
            currUser.set_password(currUser.password)
            # Deactivate the user until the complete email confirmation
            currUser.is_active = False
            regstr = Registration()
            regstr.user = currUser
            regstr.key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            regstr.save()
            # Update the user object
            currUser.save()
            # Grab information about the user's credentials
            username = request.POST.get('username')
            password = request.POST.get('password')
            # Send confirmation email
            subject = 'Thank you for joining SecureWitness'
            message = 'Welcome to the SecureWitness community. To enable your account, please click on the following link:\nhttp://still-oasis-3935.herokuapp.com/app/user/' + currUser.username + '/enable/\nYour username is: ' + regstr.user.username + '\nYour code is: ' + regstr.key
            from_email = settings.EMAIL_HOST_USER
            to_list = [currUser.email, settings.EMAIL_HOST_USER]
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            # Create a folder for the user in the file system
            try:
                os.mkdir(os.path.join(settings.MEDIA_ROOT, currUser.username))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise e
                pass
            # Redirect the user to the enable page
            return HttpResponseRedirect('/app/enable/')
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()

    return render(request, 'app/register.html', {'user_form': user_form})


def enable(request):
    if request.method == 'POST':
        reg_form = RegistrationForm(request.POST)
        if reg_form.is_valid():
            user_str = request.POST.get('user', None)
            key_str = request.POST.get('key', None)
            password_str = request.POST.get('password', None)
            entered_user = User.objects.filter(username=user_str).first()
            regstr = Registration.objects.filter(user=entered_user, key=key_str).first()
            currUser = authenticate(username=user_str, password=password_str)
            if currUser:
                if regstr:
                    regstr.delete()
                    currUser.is_active = True
                    currUser.save()
                    login(request, currUser)
                    return HttpResponseRedirect('/app/')
                else:
                    return HttpResponseRedirect('/app/enable/')
            else:
                # Bad login details were provided
                print("Invalid login details: {0}, {1}".format(user_str, password_str))
                return HttpResponse("Invalid login details supplied.")

        else:
            print(reg_form.errors)
    else:
        reg_form = RegistrationForm()
    return render(request, 'app/enable.html', {'form': reg_form})


def user_login(request):
    if request.method == 'POST':
        # Grab information about the user's credentials
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Validate the user's credentials
        currUser = authenticate(username=username, password=password)
        # Check if the user's credentials were valid
        if currUser:
            # Check if the user account is active
            if currUser.is_active:
                # Log the user in
                login(request, currUser)
                # Redirect the user to the homepage
                return HttpResponseRedirect('/app/')
            else:
                # An inactive account was used
                return HttpResponse("Your SecureWitness account is disabled.")
        else:
            # Bad login details were provided
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    else:
        # No context variables to pass to the template system
        return render(request, 'app/login.html', {})


@login_required
def user_logout(request):
    # Log the user out
    logout(request)
    # Take the user back to the homepage
    return HttpResponseRedirect('/app/')


@login_required
def change_password(request, user_name_slug):
    currUser = request.user
    if currUser.username != user_name_slug:
        return render(request, 'app/access_denied.html', {})

    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            oldPassword = request.POST.get('oldPassword')
            currUser = authenticate(username=user_name_slug, password=oldPassword)
            if currUser:
                currUser.set_password(request.POST.get('newPassword'))
                currUser.save()
                login(request, currUser)
                return HttpResponseRedirect('/app/user/' + user_name_slug + '/')
            else:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            print(form.errors)
    else:
        form = ChangePasswordForm()

    return render(request, 'app/change_password.html', {'form': form, 'user': currUser})


@login_required
def delete_account(request, user_name_slug):
    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser, user_name_slug):
        return render(request, 'app/access_denied.html', {})

    # Set the user's account to inactive
    currUser.is_active = False
    currUser.save()

    # Log the user out of their account
    return user_logout(request)


@login_required
def suspend_user(request):
    currUser = request.user
    adminGroup = Group.objects.filter(id=1).first()
    if not is_admin(currUser):
        return render(request, 'app/access_denied.html', {})

    if request.method == 'POST':
        userID = request.POST.get('user', None)
        user = User.objects.filter(id=userID).first()
        user.is_active = False
        user.save()
        return HttpResponseRedirect('/app/group/1/')
    else:
        form = GroupUserForm()
        # Option to remove only members belonging to the group
        form.fields['user'].queryset = User.objects.all().exclude(id__in=adminGroup.user_set.all().values_list('id', flat=True)).exclude(is_active=False)

    return render(request, 'app/suspend_user.html', {'form': form, 'user': currUser})

@login_required
def unsuspend_user(request):
    currUser = request.user
    adminGroup = Group.objects.filter(id=1).first()
    if not is_admin(currUser):
        return render(request, 'app/access_denied.html', {})

    if request.method == 'POST':
        userID = request.POST.get('user', None)
        user = User.objects.filter(id=userID).first()
        user.is_active = True
        user.save()
        return HttpResponseRedirect('/app/group/1/')
    else:
        form = GroupUserForm()
        # Option to remove only members belonging to the group
        form.fields['user'].queryset = User.objects.filter(is_active=False)

    return render(request, 'app/suspend_user.html', {'form': form, 'user': currUser, 'unsuspend': True})


@login_required
def user(request, user_name_slug):
    # Validate that the user has access
    currUser = request.user
    if currUser.username != user_name_slug:
        return render(request, 'app/access_denied.html', {})

    # Retrieve all of the user's reports that are not stored in folders
    reports = Report.objects.filter(user=currUser, folder=None)
    # Retrieve all of the user's folders
    folders = Folder.objects.filter(user=currUser)

    return render(request, 'app/user.html', {'user': currUser, 'reports': reports, 'folders': folders})


@login_required
def folder(request, user_name_slug, folder_slug):
    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser, user_name_slug):
        return render(request, 'app/access_denied.html', {})

    # Retrieve all of the user's reports that are stored in the given folder
    folder = Folder.objects.filter(user=currUser, slug=folder_slug).first()
    reports = Report.objects.filter(user=currUser, folder=folder)

    return render(request, 'app/folder.html', {'user': currUser, 'folder': folder, 'reports': reports})


@login_required
def add_folder(request, user_name_slug):
    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser, user_name_slug):
        return render(request, 'app/access_denied.html', {})

    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            # Set fields not specified by form
            folder.user = currUser
            folder.save()
            # Create a corresponding folder in the file system
            try:
                os.mkdir(os.path.join(settings.MEDIA_ROOT, currUser.username, folder.name))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise e
                pass
            return HttpResponseRedirect('/app/user/' + user_name_slug + '/')
        else:
            print(form.errors)
    else:
        form = FolderForm()

    return render(request, 'app/add_folder.html', {'form': form, 'user': currUser})


@login_required
def delete_folder(request, user_name_slug, folder_slug):
    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser, user_name_slug):
        return render(request, 'app/access_denied.html', {})

    # Obtain information about the folder and reports
    folder = Folder.objects.filter(user=currUser, slug=folder_slug).first()
    reports = Report.objects.filter(folder=folder)

    # Delete each of the reports
    for report in reports:
        delete_report(request, user_name_slug, report.id)
    # Remove the folder from the database
    folder.delete()
    # Remove the folder from the file system
    os.rmdir(os.path.join(settings.MEDIA_ROOT, user_name_slug, folder.name))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def group(request, group_id):
    # Validate that the user has access
    currUser = request.user
    # User does not belong to the group
    if not currUser.groups.filter(id=group_id).exists():
        return render(request, 'app/access_denied.html', {})

    # Retrieve reports shared with the group
    currGroup = Group.objects.filter(id=group_id).first()
    reports = currGroup.report_set.all()
    requests = UserGroupRequest.objects.all()

    return render(request, 'app/group.html',
                  {'user': currUser, 'reports': reports, 'group': currGroup, 'admin': currGroup.id == 1,
                   'requests': requests})


@login_required
def add_group(request):
    # Validate that the user has access
    currUser = request.user
    if not currUser.groups.filter(id=1).exists():
        return render(request, 'app/access_denied.html', {})

    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            # Create a group based on the fom
            group = Group()
            group.name = request.POST.get('name', None)
            group.save()
            # Automatically make the admins members of the group
            admins = Group.objects.filter(id=1).first().user_set.all()
            for admin in admins:
                admin.groups.add(group)
                admin.save()
            return HttpResponseRedirect('/app/group/1/')
    else:
        form = GroupForm
    return render(request, 'app/add_group.html', {'form': form, 'user': currUser})


@login_required
def add_to_group(request, group_id):
    # Validate that the user has access - any member can add a new member
    currUser = request.user
    if not currUser.groups.filter(id=group_id).exists():
        return render(request, 'app/access_denied.html', {})

    # Get information about the current group
    group = Group.objects.filter(id=group_id).first()

    if request.method == 'POST':
        userID = request.POST.get('user', None)
        user = User.objects.filter(id=userID).first()
        user.groups.add(group)
        # Delete a pending request if necessary
        pendingRequests = UserGroupRequest.objects.filter(user=user, group=group)
        if pendingRequests:
            for pendingRequest in pendingRequests:
                pendingRequest.delete()
        return HttpResponseRedirect('/app/group/' + str(group.id) + '/')
    else:
        form = GroupUserForm()
        # Option to add any member not in the group
        form.fields['user'].queryset = User.objects.exclude(id__in=group.user_set.all().values_list('id', flat=True))

    return render(request, 'app/add_to_group.html', {'form': form, 'user': currUser, 'add': True, 'group': group})


@login_required
def remove_from_group(request, group_id):
    # Validate that the user has access - an admin can remove a member
    currUser = request.user
    if not currUser.groups.filter(id=1).exists():
        return render(request, 'app/access_denied.html', {})

    # Get information about the current group
    group = Group.objects.filter(id=group_id).first()
    adminGroup = Group.objects.filter(id=1).first()

    if request.method == 'POST':
        userID = request.POST.get('user', None)
        user = User.objects.filter(id=userID).first()
        user.groups.remove(group)
        return HttpResponseRedirect('/app/group/' + str(group.id) + '/')
    else:
        form = GroupUserForm()
        # Option to remove only members belonging to the group
        form.fields['user'].queryset = group.user_set.all().exclude(
            id__in=adminGroup.user_set.all().values_list('id', flat=True))

    return render(request, 'app/add_to_group.html', {'form': form, 'user': currUser, 'add': False, 'group': group})


@login_required
def share_report(request, user_name_slug, report_slug):
    # Obtain information about the user and report
    currUser = request.user
    report = Report.objects.filter(id=report_slug).first()

    # Check if the report does not belong to the current user
    if currUser != report.user:
        # Tell the user that the page is restricted
        return render(request, 'app/access_denied.html', {})

    if request.method == 'POST':
        dest = request.POST.get('dest', None)
        destGroup = Group.objects.filter(id=dest).first()
        report.groups.add(destGroup)
        report.save()
        return HttpResponseRedirect('/app/user/' + user_name_slug + '/')
    else:
        form = ShareReportForm()
        form.fields['dest'].queryset = currUser.groups.all()

    return render(request, 'app/share_report.html', {'form': form, 'user': currUser, 'report': report})


@login_required
def remove_report(request, group_id, report_slug):
    # Obtain information about the user and report
    currUser = request.user
    report = Report.objects.filter(id=report_slug).first()

    # Check if the report does not belong to the current user
    if currUser != report.user:
        # Tell the user that the page is restricted
        return render(request, 'app/access_denied.html', {})

    currGroup = Group.objects.filter(id=group_id).first()

    report.groups.remove(currGroup)
    report.save()

    return HttpResponseRedirect('/app/group/' + group_id + '/')


@login_required
def report(request, report_slug):
    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser, None, None, report_slug):
        return render(request, 'app/access_denied.html', {})

    # Obtain information about the specified report
    report = Report.objects.filter(id=report_slug).first()
    files = Attachment.objects.filter(report=report)

    """ *** This passes in the current user --> Not the report's creator *** """
    return render(request, 'app/report.html', {'user': currUser, 'report': report, 'files': files})


@login_required
def add_report(request, user_name_slug, folder_slug=None):
    # Validate that the user has access
    currUser = request.user
    if currUser.username != user_name_slug:
        return render(request, 'app/access_denied.html', {})

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            # Set fields not specified by the form
            report.user = currUser
            report.timeCreated = datetime.now()
            # Specify whether the report should be placed in a folder
            if folder_slug:
                folder = Folder.objects.filter(user=currUser, slug=folder_slug).first()
                report.folder = folder
                report.save()
                return HttpResponseRedirect('/app/user/' + user_name_slug + '/folder/' + folder_slug + '/')
            else:
                report.folder = None
                report.save()
                return HttpResponseRedirect('/app/user/' + user_name_slug + '/')
        else:
            print(form.errors)
    else:
        form = ReportForm()

    return render(request, 'app/add_report.html', {'form': form, 'user': currUser, 'folder_slug': folder_slug})


@login_required
def edit_report(request, user_name_slug, report_slug=None):
    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser, user_name_slug, None, report_slug, True):
        return render(request, 'app/access_denied.html', {})

    report = Report.objects.filter(id=report_slug).first()

    if request.method == 'POST':
        form = ReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            # Return the user back to their homepage
            if report.folder:
                return HttpResponseRedirect('/app/user/' + user_name_slug + '/folder/' + report.folder.slug + '/')
            else:
                return HttpResponseRedirect('/app/user/' + user_name_slug + '/')
        else:
            print(form.errors)
    else:
        form = ReportForm(instance=report)

    return render(request, 'app/add_report.html', {'form': form, 'user': currUser, 'report': report})


@login_required
def copy_report(request, user_name_slug, report_slug):
    # Obtain information about the user and report
    currUser = request.user
    report = Report.objects.filter(id=report_slug).first()

    # Check if the report does not belong to the current user
    if currUser != report.user:
        # Tell the user that the page is restricted
        return render(request, 'app/access_denied.html', {})

    if request.method == 'POST':
        dest = request.POST.get('dest', None)
        if dest:
            # User entered a folder name
            if report.folder and str(report.folder.id) == str(dest):
                # Destination = current location
                return render(request, 'app/access_denied.html', {})
            else:
                wasInFolder = False
                if report.folder:
                    wasInFolder = True
                    folderSlug = report.folder.slug
                folder = Folder.objects.filter(user=currUser, id=dest).first()
                old_files = Attachment.objects.filter(report=report)
                newReport = report
                newReport.pk = None
                newReport.save()
                newReport.folder = folder
                newReport.save()
                for old_file in old_files:
                    new_file = Attachment()
                    new_file.user = currUser
                    new_file.report = newReport
                    new_file.encrypted = old_file.encrypted
                    new_file.hash = old_file.hash
                    new_file.file = File(old_file.file,
                                         os.path.join(settings.MEDIA_ROOT, currUser.username, folder.name,
                                                      os.path.split(old_file.file.name)[1]))
                    new_file.save()
                if wasInFolder:
                    return HttpResponseRedirect('/app/user/' + user_name_slug + '/folder/' + folderSlug + '/')
                else:
                    return HttpResponseRedirect('/app/user/' + user_name_slug + '/')
        else:
            # User entered the home folder
            if not report.folder:
                # Destination = current location
                return HttpResponse("This report already exists in the given location")
            else:
                folderSlug = report.folder.slug
                old_files = Attachment.objects.filter(report=report)
                newReport = report
                newReport.pk = None
                newReport.save()
                newReport.folder = None
                newReport.save()
                for old_file in old_files:
                    new_file = Attachment()
                    new_file.user = currUser
                    new_file.report = newReport
                    new_file.encrypted = old_file.encrypted
                    new_file.file = File(old_file.file, os.path.join(settings.MEDIA_ROOT, currUser.username,
                                                                     os.path.split(old_file.file.name)[1]))
                    new_file.save()
                return HttpResponseRedirect('/app/user/' + user_name_slug + '/folder/' + folderSlug)
    else:
        form = CopyMoveReportForm()
        if report.folder:
            form.fields['dest'].queryset = Folder.objects.filter(user=currUser).exclude(id=report.folder.id)
        else:
            form.fields['dest'].queryset = Folder.objects.filter(user=currUser)

    return render(request, 'app/copymove_report.html', {'form': form, 'user': currUser, 'report': report})


@login_required
def move_report(request, user_name_slug, report_slug):
    # Obtain information about the user and report
    currUser = request.user
    report = Report.objects.filter(id=report_slug).first()

    # Check if the report does not belong to the current user
    if currUser != report.user:
        # Tell the user that the page is restricted
        return render(request, 'app/access_denied.html', {})

    if request.method == 'POST':
        dest = request.POST.get('dest', None)
        if dest:
            # User entered a folder name
            if report.folder and report.folder.name == dest:
                # Destination = current location
                return HttpResponseRedirect('/app/user/' + user_name_slug + '/folder/' + report.folder.slug + '/')
            else:
                folder = Folder.objects.filter(user=currUser, id=dest).first()
                oldFolder = report.folder
                oldRoot = os.path.join(settings.MEDIA_ROOT, currUser.username)
                if oldFolder:
                    oldRoot = os.path.join(oldRoot, oldFolder.name)
                report.folder = folder
                report.save()
                files = Attachment.objects.filter(report=report)
                for f in files:
                    oldLocation = os.path.join(oldRoot, str(f))
                    newLocation = os.path.join(settings.MEDIA_ROOT, currUser.username, folder.name, str(f))
                    os.rename(oldLocation, newLocation)
                    f.file.name = os.path.join(settings.MEDIA_ROOT, user_name_slug, folder.name, str(f))
                if oldFolder:
                    return HttpResponseRedirect('/app/user/' + user_name_slug + '/folder/' + oldFolder.slug)
                else:
                    return HttpResponseRedirect('/app/user/' + user_name_slug + '/')
        else:
            # User entered the home folder
            if not report.folder:
                # Destination = current location
                return HttpResponseRedirect('/app/user/' + user_name_slug + '/')
            else:
                folder = report.folder
                report.folder = None
                report.save()
                files = Attachment.objects.filter(report=report)
                for f in files:
                    oldLocation = os.path.join(settings.MEDIA_ROOT, currUser.username, folder.name, str(f))
                    newLocation = os.path.join(settings.MEDIA_ROOT, currUser.username, str(f))
                    os.rename(oldLocation, newLocation)
                    f.file.name = os.path.join(settings.MEDIA_ROOT, currUser.username, str(f))
                return HttpResponseRedirect('/app/user/' + user_name_slug + '/folder/' + folder.slug + '/')

    else:
        form = CopyMoveReportForm()
        if report.folder:
            form.fields['dest'].queryset = Folder.objects.filter(user=currUser).exclude(id=report.folder.id)
        else:
            form.fields['dest'].queryset = Folder.objects.filter(user=currUser)

    return render(request, 'app/copymove_report.html', {'form': form, 'user': currUser, 'report': report, 'move': True})


@login_required
def delete_report(request, user_name_slug, report_slug):
    # Validate that the user has access
    currUser = request.user
    report = Report.objects.filter(id=report_slug).first()
    if report.user != currUser and not is_admin(currUser):
        return render(request, 'app/access_denied.html', {})

    # Access information about the given report
    files = Attachment.objects.filter(report=report)

    for file in files:
        if (file.folder):
            # Remove the file from memory
            os.remove(os.path.join(settings.MEDIA_ROOT, currUser.username, str(file.folder), str(fiie.file)))
        else:
            # Remove the file from memory
            os.remove(os.path.join(settings.MEDIA_ROOT, currUser.username, str(file.file)))
    # Remove the file from the database
    file.delete()
    # Remove the report from the database
    report.delete()

    # Redirect the user to the appropriate page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def add_file(request, report_slug=None):
    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser, None, None, report_slug, True):
        return render(request, 'app/access_denied.html', {})

    report = Report.objects.filter(id=report_slug).first()

    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            # Set fields not specified by the form
            attachment.user = currUser
            attachment.report = report
            attachment.save()
            attachment.hash = hash(attachment.file.name)
            attachment.save()
            # Encrypt the file if necessary
            key = request.POST.get('key', None)
            if key:
                # Find the name of the original file
                fileName = os.path.join(settings.MEDIA_ROOT, currUser.username, attachment.file.name)
                # Encrypt the file and update the file name in the database
                attachment.encrypted = True
                encrypt_file(key, fileName)
                attachment.file.name += '.enc'
                # Remove the original file from memory
                os.remove(fileName)
                # Save updates to the database
                attachment.save()
                attachment.hash = hash(attachment.file.name)
                attachment.save()
            # Update the file's location in memory if necessary
            if report.folder:
                oldLocation = os.path.join(settings.MEDIA_ROOT, currUser.username, str(attachment))
                newLocation = os.path.join(settings.MEDIA_ROOT, currUser.username, report.folder.name, str(attachment))
                os.rename(oldLocation, newLocation)
                return HttpResponseRedirect('/app/user/' + currUser.username + '/folder/' + report.folder.slug + '/')
            return HttpResponseRedirect('/app/user/' + currUser.username + '/')
        else:
            print(form.errors)
    else:
        form = AttachmentForm()

    return render(request, 'app/files.html', {'form': form, 'user': currUser, 'report': report})


@login_required
def delete_file(request, report_slug, file_slug):
    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser, None, None, report_slug, True):
        return render(request, 'app/access_denied.html', {})

    # Access information about the given file
    file = Attachment.objects.filter(id=file_slug).first()

    # Determine where the file is stored in the file system
    folder = file.report.folder
    # Remove the file from the file system
    if folder:
        os.remove(os.path.join(settings.MEDIA_ROOT, currUser.username, folder.name, str(file)))
    else:
        os.remove(os.path.join(settings.MEDIA_ROOT, currUser.username, str(file)))
    # Remove the file from the database
    file.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def search(request):
    if request.method == 'POST':
        reports = Report.objects.all()
        if not is_admin(request.user):
            reports = reports.filter(private=False)
        basic_text = request.POST.get('search', None)
        short = request.POST.get('shortDesc', None)
        if basic_text or (basic_text == "" and not short):
            if basic_text == "":
                return render(request, 'app/home.html', {'reports': reports, 'admin': is_admin(request.user)})
            # POST request from basic search
            entry_query = get_query(basic_text, ['shortDesc', 'detailedDesc', 'keywords', ])
            reports = reports.filter(entry_query)
            return render(request, 'app/home.html', {'reports': reports, 'admin': is_admin(request.user)})
        else:
            # POST request from advanced search
            if short:
                entry_query = get_query(short, ['shortDesc', ])
                reports = reports.filter(entry_query)

            long = request.POST.get('detailedDesc', None)
            if long:
                entry_query = get_query(long, ['detailedDesc', ])
                reports = reports.filter(entry_query)

            keywords = request.POST.get('keywords', None)
            if keywords:
                entry_query = get_query(keywords, ['keywords', ])
                reports = reports.filter(entry_query)

            location = request.POST.get('location', None)
            if location:
                entry_query = get_query(location, ['location', ])
                reports = reports.filter(entry_query)

            # This doesn't work correctly - evaluates to None
            dateOfIncident_day = int(request.POST.get('dateOfIncident_day', None))
            dateOfIncident_month = int(request.POST.get('dateOfIncident_month', None))
            dateOfIncident_year = int(request.POST.get('dateOfIncident_year', None))
            if dateOfIncident_day != 0:
                reports = reports.filter(dateOfIncident__day=dateOfIncident_day)
            if dateOfIncident_month != 0:
                reports = reports.filter(dateOfIncident__month=dateOfIncident_month)
            if dateOfIncident_year != 0:
                reports = reports.filter(dateOfIncident__year=dateOfIncident_year)

            return render(request, 'app/home.html', {'reports': reports, 'admin': is_admin(request.user)})
    else:
        form = SearchForm()

    return render(request, 'app/search.html', {'form': form})


@login_required
def group_request(request):
    if request.method == 'POST':
        form = UserGroupRequestForm(request.POST)
        if form.is_valid():
            groupRequest = form.save(commit=False)
            # Set fields not specified by the form
            groupRequest.user = request.user
            groupRequest.save()
            return HttpResponseRedirect('/app/')
        else:
            print(form.errors)
    else:
        form = UserGroupRequestForm()
        # Request access only to groups which one is not a member
        form.fields['group'].queryset = Group.objects.exclude(
            id__in=request.user.groups.all().values_list('id', flat=True))

    return render(request, 'app/request.html', {'form': form})


@login_required
def confirm_request(request, request_id):
    currUser = request.user
    if not is_admin(currUser):
        return render(request, 'app/access_denied.html', {})

    groupRequest = UserGroupRequest.objects.filter(id=request_id).first()

    requestUser = groupRequest.user
    requestGroup = groupRequest.group

    requestUser.groups.add(requestGroup)
    requestUser.save()

    groupRequest.delete()

    return HttpResponseRedirect('/app/group/1/')


@login_required
def delete_request(request, request_id):
    currUser = request.user
    if not is_admin(currUser):
        return render(request, 'app/access_denied.html', {})

    groupRequest = UserGroupRequest.objects.filter(id=request_id).first()
    groupRequest.delete()

    return HttpResponseRedirect('/app/group/1/')
