import os
from django.shortcuts import render
from app.models import Report, Attachment
from app.encryption import encrypt_file
from app.forms import UserForm, ReportForm, AttachmentForm, SearchForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from SecureWitness import settings

def home(request):
    # Create a list of all visible reports
    reports = Report.objects.filter(private=False)
    # Direct the user to the SecureWitness homepage
    return render(request, 'app/home.html', {'reports': reports})

def register(request):

    registered = False

    # HTTP POST: Process form data
    if request.method == 'POST':
        # Attempt to grab information from the raw form object
        user_form = UserForm(request.POST)
        # Check if the form is valid
        if user_form.is_valid():
            # Save the user's form data to the database
            currUser = user_form.save()
            # Hash the password with the set_password method
            currUser.set_password(currUser.password)
            # Update the user object
            currUser.save()
            # Indicate that the user has successfully registered
            registered = True
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
                    os.mkdir(settings.MEDIA_ROOT+'\\'+currUser.username+'\\')
                    # Redirect the user to the home page
                    return HttpResponseRedirect('/app/')
                else:
                    # An inactive account was used
                    return HttpResponse("Your SecureWitness account is disabled.")
            else:
                # Bad login details were provided
                print("Invalid login details: {0}, {1}".format(username, password))
                return HttpResponse("Invalid login details supplied.")

        # Invalid form - prints problems to the terminal
        else:
            print(user_form.errors)

    # HTTP GET: Render the form using a ModelForm instance
    else:
        user_form = UserForm()

    # Render the template depending on the context
    return render(request, 'app/register.html', {'user_form': user_form, 'registered': registered})

def user_login(request):

    # HTTP POST: Process form data
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

    # HTTP GET: Render the login page
    else:
        # No context variables to pass to the template system
        return render(request, 'app/login.html', {})

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/app/')

@login_required
def delete_account(request, user_name_slug):

    # Obtain information about the user attempting to view the page
    currUser = request.user

    # Check if the requested home page belongs to the current user
    if currUser.username != user_name_slug:
        # Tell the user that the page is restricted
        return HttpResponse("You are not authorized to view this page")

    # Set the user's account to inactive
    currUser.is_active = False
    currUser.save();

   # Log the user out of their account
    return user_logout(request)

@login_required
def user(request, user_name_slug):

    # Obtain information about the user attempting to view the page
    currUser = request.user

    # Check if the requested home page belongs to the current user
    if currUser.username != user_name_slug:
        # Tell the user that the page is restricted
        return HttpResponse("You are not authorized to view this page")

    # Create a context dictionary which we can pass to the template
    context_dict = {}

    # Place the user's username in the context dictionary
    context_dict['user'] = currUser

    # Retrieve all of the associated reports
    # Note that filter returns >= 1 model instance
    reports = Report.objects.filter(user=currUser)
    files = Attachment.objects.filter(user=currUser)

    # Adds our results list to the template context under name reports
    context_dict['reports'] = reports
    context_dict['files'] = files

    # Go render the response and return it to the client.
    return render(request, 'app/user.html', context_dict)

@login_required
def add_report(request, user_name_slug):

    # Obtain information about the user attempting to view the page
    currUser = request.user

    # Check if the requested home page belongs to the current user
    if currUser.username != user_name_slug:
        # Tell the user that the page is restricted
        return HttpResponse("You are not authorized to view this page")

    if request.method == 'POST':
        form = ReportForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            report = form.save(commit=False)
            # Set the user and timestamp
            report.user = currUser
            report.timeCreated = datetime.now()
            # Other information should already be created
            report.save()
            # Return the user back to their homepage
            return HttpResponseRedirect('/app/user/'+user_name_slug+'/')
        else:
            print(form.errors)
    else:
        form = ReportForm()

    context_dict = {'form':form, 'user': currUser}

    return render(request, 'app/add_report.html', context_dict)

@login_required
def report(request, report_slug):

    # Obtain information about the user attempting to view the page
    currUser = request.user
    report = Report.objects.filter(id=report_slug).first()

    # Ensure that the report exists
    if not report:
        return HttpResponse("You are not authorized to view this page")

    if report.private and report.user != currUser:
        return HttpResponse("You are not authorized to view this page")

    files = Attachment.objects.filter(report=report)

    context_dict = {}
    context_dict['user'] = currUser
    context_dict['report'] = report
    context_dict['files'] = files

    return render(request, 'app/report.html', context_dict)

@login_required
def edit_report(request, user_name_slug, report_slug=None):

    # Check if the requested home page belongs to the current user
    currUser = request.user
    if currUser.username != user_name_slug:
        # Tell the user that the page is restricted
        return HttpResponse("You are not authorized to view this page")

    report = Report.objects.filter(id=report_slug).first()

    # Check if the requested report does not exist or belongs to the current user
    if not report or currUser != report.user:
        # Tell the user that the page is restricted
        return HttpResponse("You are not authorized to view this page")

    if request.method == 'POST':
        form = ReportForm(request.POST, instance=report)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the report to the database
            form.save()
            # Return the user back to their homepage
            return HttpResponseRedirect('/app/user/'+currUser.username+'/')
        else:
            print(form.errors)
    else:
        form = ReportForm(instance=report)

    context_dict = {'form':form, 'user': currUser, 'report': report}

    return render(request, 'app/add_report.html', context_dict)

@login_required
def add_file(request, report_slug=None):

    # Obtain information about the user and report
    currUser = request.user
    report = Report.objects.filter(id=report_slug).first()

    # Check if the requested report does not exist or belong to the current user
    if not report or currUser != report.user:
        # Tell the user that the page is restricted
        return HttpResponse("You are not authorized to view this page")

    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.user = currUser
            attachment.report = report
            attachment.save()
            encrypt = request.POST.get('password', None)
            if encrypt:
                # Encrypt the attachment
                fileName = os.path.join(settings.MEDIA_ROOT, currUser.username, attachment.file.name)
                encrypt_file('passwordpassword', fileName)
                attachment.file.name += '.enc'
                os.remove(fileName)
                attachment.encrypted = True
                attachment.save()

            return HttpResponseRedirect('/app/user/'+currUser.username+'/')
        else:
            print(form.errors)
    else:
        form = AttachmentForm()

    context_dict = {'form': form, 'user': currUser, 'report': report}

    return render(request, 'app/files.html', context_dict)

@login_required
def delete_report(request, user_name_slug, report_slug):

    # Obtain information about the user and report
    currUser = request.user
    report = Report.objects.filter(id=report_slug).first()

    # Check if the report does not belong to the current user
    if currUser != report.user:
        # Tell the user that the page is restricted
        return HttpResponse("You are not authorized to view this page")

    # Find the list of files associated with the report
    files = Attachment.objects.filter(report=report)
    # Remove each of the files from memory
    for f in files:
        os.remove(os.path.join(settings.MEDIA_ROOT, currUser.username, str(f.file)))
        f.delete()
    report.delete()
    return HttpResponseRedirect('/app/user/'+currUser.username+'/')

@login_required
def delete_file(request, report_slug, file_slug):
    # Obtain information about the user and report
    currUser = request.user
    report = Report.objects.filter(id=report_slug).first()
    f = Attachment.objects.filter(id=file_slug).first()

    # Check if the report does not belong to the current user
    if currUser != report.user:
        # Tell the user that the page is restricted
        return HttpResponse("You are not authorized to view this page")

    os.remove(os.path.join(settings.MEDIA_ROOT, currUser.username, str(f.file)))
    f.delete()

    return HttpResponseRedirect('/app/report/'+report_slug)


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
