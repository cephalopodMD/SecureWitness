import os, re
from django.core.files import File
from django.shortcuts import render
from app.encryption import encrypt_file, hash
from app.forms import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from SecureWitness import settings
from django.db.models import Q

def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall, normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    '''
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
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
    return render(request, 'app/home.html', {'reports': reports, 'user': currUser, 'groups': groups, 'admin': is_admin(currUser)})

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
            # Send confirmation email
            subject = 'Thank you for joining SecureWitness'
            message = 'Welcome to the SecureWitness community. We love you.'
            from_email = settings.EMAIL_HOST_USER
            to_list = [currUser.email, settings.EMAIL_HOST_USER]
            send_mail(subject, message, from_email, to_list, fail_silently=True)
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

"""
  What should happen to a user's reports when they
  delete their account? Should we remove them all
  from the database or will this cause model key
  issues?
"""
@login_required
def delete_account(request, user_name_slug):

    # Validate that the user has access
    currUser = request.user
    if not hasAccess(currUser,user_name_slug):
        return HttpResponse("You are not authorized to view this page")

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
        return HttpResponse("You are not authorized to view this page")

    if request.method == 'POST':
        userID = request.POST.get('user', None)
        user = User.objects.filter(id=userID).first()
        user.is_active = False
        user.save()
        return HttpResponseRedirect('/app/group/1/')
    else:
        form = GroupUserForm()
        # Option to remove only members belonging to the group
        form.fields['user'].queryset = User.objects.all().exclude(id__in=adminGroup.user_set.all().values_list('id', flat=True))

    return render(request, 'app/suspend_user.html', {'form': form, 'user': currUser})


@login_required
def user(request, user_name_slug):

    # Validate that the user has access
    currUser = request.user
    if currUser.username != user_name_slug:
        return HttpResponse("You are not authorized to view this page")

    # Retrieve all of the user's reports that are not stored in folders
    reports = Report.objects.filter(user=currUser, folder=None)
    # Retrieve all of the user's folders
    folders = Folder.objects.filter(user=currUser)

    return render(request, 'app/user.html', {'user': currUser, 'reports': reports, 'folders': folders})

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

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def group(request, group_id):
