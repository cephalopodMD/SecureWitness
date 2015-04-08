import os, shutil
from django.core.files import File
from django.shortcuts import render
from app.models import Report, Attachment, Folder
from app.encryption import encrypt_file
from app.forms import UserForm, ReportForm, AttachmentForm, SearchForm, FolderForm, CopyMoveReportForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from SecureWitness import settings

def hasAccess(currUser, user_name_slug=None, folder_slug=None, report_slug=None, edit=False):
    if user_name_slug and currUser.username != user_name_slug:
        return False
    if report_slug:
        report = Report.objects.filter(id=report_slug).first()
        if not report:
            return False
        if report.private and report.user != currUser:
            return False
        if edit and report.user != currUser:
            return False
    return True

def home(request):
    # Create a list of all public reports
    reports = Report.objects.filter(private=False)
    # Direct the user to the SecureWitness homepage
    return render(request, 'app/home.html', {'reports': reports})

def register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            # Save the user's form data to the database
            currUser = user_form.save()
            # Hash the password with the set_password method
            currUser.set_password(currUser.password)
            # Update the user object
            currUser.save()
            # Grab information about the user's credentials
            username = request.POST.get('username')
            password = request.POST.get('password')
            # Validate the user's credentials
            currUser = authenticate(username=username, password=password)
            # Check if the user's credentials were valid
            if currUser:
                # Check if the user account is active
                if currUser.is_active:
                    # Log the user in.
                    login(request, currUser)
                    # Create a folder for the user in the media directory
                    os.mkdir(os.path.join(settings.MEDIA_ROOT,currUser.username))
                    # Redirect the user to the home page
                    return HttpResponseRedirect('/app/')
                else:
                    # An inactive account was used
                    return HttpResponse("Your SecureWitness account is disabled.")
            else:
                # Bad login details were provided
                print("Invalid login details: {0}, {1}".format(username, password))
                return HttpResponse("Invalid login details supplied.")
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()

    return render(request, 'app/register.html', {'user_form': user_form})

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
def delete_account(request, user_name_slug):

    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser,user_name_slug):
        return HttpResponse("You are not authorized to view this page")

    # Set the user's account to inactive
    currUser.is_active = False
    currUser.save();

    # Log the user out of their account
    return user_logout(request)

@login_required
def user(request, user_name_slug):

    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser,user_name_slug):
        return HttpResponse("You are not authorized to view this page")

    # Retrieve all of the user's reports that are not stored in folders
    reports = Report.objects.filter(user=currUser, folder=None)
    # Retrieve all of the user's folders
    folders = Folder.objects.filter(user=currUser)

    return render(request, 'app/user.html', {'user': currUser, 'reports': reports, 'folders': folders})

@login_required
def add_report(request, user_name_slug, folder_slug=None):

    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser,user_name_slug):
        return HttpResponse("You are not authorized to view this page")

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
                return HttpResponseRedirect('/app/user/'+user_name_slug+'/folder/'+folder_slug+'/')
            else:
                report.folder = None
                report.save()
                return HttpResponseRedirect('/app/user/'+user_name_slug+'/')
        else:
            print(form.errors)
    else:
        form = ReportForm()

    return render(request, 'app/add_report.html', {'form': form, 'user': currUser, 'folder_slug': folder_slug})

@login_required
def report(request, report_slug):

    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser, None, None, report_slug):
        return HttpResponse("You are not authorized to view this page")

    # Obtain information about the specified report
    report = Report.objects.filter(id=report_slug).first()
    files = Attachment.objects.filter(report=report)

    """ *** This passes in the current user --> Not the report's creator *** """
    return render(request, 'app/report.html', {'user': currUser, 'report': report, 'files': files})

@login_required
def edit_report(request, user_name_slug, report_slug=None):

    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser, user_name_slug, None, report_slug, True):
        return HttpResponse("You are not authorized to view this page")

    report = Report.objects.filter(id=report_slug).first()

    if request.method == 'POST':
        form = ReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            # Return the user back to their homepage
            if report.folder:
                return HttpResponseRedirect('/app/user/'+user_name_slug+'/folder/'+report.folder.slug+'/')
            else:
                return HttpResponseRedirect('/app/user/'+user_name_slug+'/')
        else:
            print(form.errors)
    else:
        form = ReportForm(instance=report)

    return render(request, 'app/add_report.html', {'form': form, 'user': currUser, 'report': report})

@login_required
def add_file(request, report_slug=None):

    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser, None, None, report_slug, True):
        return HttpResponse("You are not authorized to view this page")

    report = Report.objects.filter(id=report_slug).first()

    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            # Set fields not specified by the form
            attachment.user = currUser
            attachment.report = report
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
            # Update the file's location in memory if necessary
            if report.folder:
                oldLocation = os.path.join(settings.MEDIA_ROOT, currUser.username, str(attachment))
                newLocation = os.path.join(settings.MEDIA_ROOT, currUser.username, report.folder.name, str(attachment))
                os.rename(oldLocation,newLocation)
                return HttpResponseRedirect('/app/user/'+currUser.username+'/folder/'+report.folder.slug+'/')
            return HttpResponseRedirect('/app/user/'+currUser.username+'/')
        else:
            print(form.errors)
    else:
        form = AttachmentForm()

    return render(request, 'app/files.html', {'form': form, 'user': currUser, 'report': report})

@login_required
def delete_report(request, user_name_slug, report_slug):

    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser, user_name_slug, None, report_slug, True):
        return HttpResponse("You are not authorized to view this page")

    # Access information about the given report
    report = Report.objects.filter(id=report_slug).first()
    files = Attachment.objects.filter(report=report)

    for file in files:
        # Remove the file from memory
        os.remove(os.path.join(settings.MEDIA_ROOT, currUser.username, str(file.file)))
        # Remove the file from the database
        file.delete()
    # Remove the report from the database
    report.delete()

    # Redirect the user to the appropriate page
    if report.folder:
        return HttpResponseRedirect('/app/user/'+currUser.username+'/folder/'+report.folder.slug+'/')
    else:
        return HttpResponseRedirect('/app/user/'+currUser.username+'/')

@login_required
def delete_file(request, report_slug, file_slug):

    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser, None, None, report_slug, True):
        return HttpResponse("You are not authorized to view this page")

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

    return HttpResponseRedirect('/app/report/'+report_slug)

@login_required
def search(request):
    if request.method == 'POST':
        reports = Report.objects.filter(private=False)

        short = request.POST.get('shortDesc', None)
        if short:
            shortWords = short.split()
            for word in shortWords:
                reports = reports.filter(shortDesc__icontains=word)

        long = request.POST.get('detailedDesc', None)
        if long:
            longWords = long.split()
            for word in longWords:
                reports = reports.filter(detailedDesc__icontains=word)

        keywords = request.POST.get('keywords', None)
        if keywords:
            keywordWords = keywords.split()
            for word in keywordWords:
                reports = reports.filter(keywords__icontains=word)

        location = request.POST.get('location', None)
        if location:
            reports = reports.filter(location__icontains=location)

        dateOfIncident = request.POST.get('dateOfIncident', None)
        if dateOfIncident:
            reports = reports.filter(dateOfIndicent=dateOfIncident)

        return render(request, 'app/home.html', {'reports': reports})

    else:
       form = SearchForm()

    return render(request, 'app/search.html', {'form': form})

@login_required
def folder(request, user_name_slug, folder_slug):

    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser,user_name_slug):
        return HttpResponse("You are not authorized to view this page")

    # Retrieve all of the user's reports that are stored in the given folder
    folder = Folder.objects.filter(user=currUser, slug=folder_slug).first()
    reports = Report.objects.filter(user=currUser, folder=folder)

    return render(request, 'app/folder.html', {'user': currUser, 'folder': folder, 'reports': reports})

@login_required
def add_folder(request, user_name_slug):

    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser,user_name_slug):
        return HttpResponse("You are not authorized to view this page")

    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            # Set fields not specified by form
            folder.user = currUser
            folder.save()
            # Create a corresponding folder in the file system
            os.mkdir(os.path.join(settings.MEDIA_ROOT,currUser.username,folder.name))
            return HttpResponseRedirect('/app/user/'+user_name_slug+'/')
        else:
            print(form.errors)
    else:
        form = FolderForm()

    return render(request, 'app/add_folder.html', {'form': form, 'user': currUser})

@login_required
def delete_folder(request, user_name_slug, folder_slug):

    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser,user_name_slug):
        return HttpResponse("You are not authorized to view this page")

    # Obtain information about the folder and reports
    folder = Folder.objects.filter(user=currUser, slug=folder_slug).first()
    reports = Report.objects.filter(folder=folder)

    # Delete each of the reports
    for report in reports:
        delete_report(request, user_name_slug, report.id)
    # Remove the folder from the database
    folder.delete()
    # Remove the folder from the file system
    os.rmdir(os.path.join(settings.MEDIA_ROOT,user_name_slug,folder.name))

    return HttpResponseRedirect('/app/user/'+currUser.username+'/')

@login_required
def move_report(request, user_name_slug, report_slug):

    # Obtain information about the user and report
    currUser = request.user
    report = Report.objects.filter(id=report_slug).first()

    # Check if the report does not belong to the current user
    if currUser != report.user:
        # Tell the user that the page is restricted
        return HttpResponse("You are not authorized to view this page")

    if request.method == 'POST':
        dest = request.POST.get('dest', None)
        if dest:
            # User entered a folder name
            if report.folder and report.folder.name == dest:
                # Destination = current location
                return HttpResponseRedirect('/app/user/'+user_name_slug+'/')
            else:
                folder = Folder.objects.filter(name=dest).first()
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
                    os.rename(oldLocation,newLocation)
                    f.file.name = os.path.join(settings.MEDIA_ROOT, user_name_slug, folder.name, str(f))
        else:
            # User entered the home folder
            if not report.folder:
                # Destination = current location
                return HttpResponseRedirect('/app/user/'+user_name_slug+'/')
            else:
                folder = report.folder
                report.folder = None
                report.save()
                files = Attachment.objects.filter(report=report)
                for f in files:
                    oldLocation = os.path.join(settings.MEDIA_ROOT, currUser.username, folder.name, str(f))
                    newLocation = os.path.join(settings.MEDIA_ROOT, currUser.username, str(f))
                    os.rename(oldLocation,newLocation)
                    f.file.name = os.path.join(settings.MEDIA_ROOT, currUser.username, str(f))

        return HttpResponseRedirect('/app/user/'+user_name_slug+'/')

    else:
        form = CopyMoveReportForm()

    return render(request, 'app/copymove_report.html', {'form': form, 'user': currUser, 'report': report, 'move': True})

@login_required
def copy_report(request, user_name_slug, report_slug):

    # Obtain information about the user and report
    currUser = request.user
    report = Report.objects.filter(id=report_slug).first()

    # Check if the report does not belong to the current user
    if currUser != report.user:
        # Tell the user that the page is restricted
        return HttpResponse("You are not authorized to view this page")

    if request.method == 'POST':
        dest = request.POST.get('dest', None)
        if dest:
            # User entered a folder name
            if report.folder and report.folder.name == dest:
                # Destination = current location
                return HttpResponse("This report already exists in the given location")
            else:
                folder = Folder.objects.filter(user=currUser,name=dest).first()
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
                    new_file.file = File(old_file.file, os.path.join(settings.MEDIA_ROOT, currUser.username, folder.name, os.path.split(old_file.file.name)[1]))
                    new_file.save()
                return HttpResponseRedirect('/app/user/'+user_name_slug+'/folder/'+folder.slug+'/')
        else:
            # User entered the home folder
            if not report.folder:
                # Destination = current location
                return HttpResponse("This report already exists in the given location")
            else:
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
                    new_file.file = File(old_file.file, os.path.join(settings.MEDIA_ROOT, currUser.username, os.path.split(old_file.file.name)[1]))
                    new_file.save()
                return HttpResponseRedirect('/app/user/'+user_name_slug+'/')
    else:
        form = CopyMoveReportForm()

    return render(request, 'app/copymove_report.html', {'form': form, 'user': currUser, 'report': report})