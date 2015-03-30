from django.shortcuts import render
from app.models import Report
from django.contrib.auth.models import User
from app.forms import UserForm, ReportForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

def index(request):
    # Render the response and send it back
    return render(request, 'app/index.html', {})

def register(request):

    # A boolean value for telling the template whether the registration was successful
    # Set to False initially. Code changes value to True when registration succeeds
    registered = False

    # If it's a HTTP POST, we're interested in processing form data
    if request.method == 'POST':
        # Attempt to grab information from the raw form information
        user_form = UserForm(data=request.POST)

        # If the form is valid
        if user_form.is_valid():
            # Save the user's form data to the database
            user = user_form.save()

            # Now we hash the password with the set_password method
            # Once hashed, we can update the user object
            user.set_password(user.password)
            user.save()

            # Update our variable to tell the template registration was successful.
            registered = True

            username = request.POST.get('username')
            password = request.POST.get('password')

            # Use Django's machinery to attempt to see if the username/password
            # combination is valid - a User object is returned if it is.
            user = authenticate(username=username, password=password)

            # If we have a User object, the details are correct.
            # If None (Python's way of representing the absence of a value), no user
            # with matching credentials was found.
            if user:
                # Is the account active? It could have been disabled.
                if user.is_active:
                    # If the account is valid and active, we can log the user in.
                    # We'll send the user back to the homepage.
                    login(request, user)
                    return HttpResponseRedirect('/app/')
                else:
                    # An inactive account was used - no logging in!
                    return HttpResponse("Your SecureWitness account is disabled.")
            else:
                # Bad login details were provided. So we can't log the user in.
                print("Invalid login details: {0}, {1}".format(username, password))
                return HttpResponse("Invalid login details supplied.")


        # Invalid form - mistake or something else?
        # Print problems to the terminal
        # They'll also be shown to the user
        else:
            print(user_form.errors)

    # Not a HTTP POST, so we render our form using a ModelForm instance
    # This form will be blank, ready for user input
    else:
        user_form = UserForm()

    # Render the template depending on the context.
    return render(request, 'app/register.html', {'user_form': user_form, 'registered': registered})

def user_login(request):

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        
        # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
        # because the request.POST.get('<variable>') returns None, if the value does not exist,
        # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/app/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your SecureWitness account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'app/login.html', {})

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/app/')

@login_required
def user(request, user_name_slug):

    # Obtain information about the user attempting to view the page
    user = request.user

    # Check if the requested home page belongs to the current user
    if user.username != user_name_slug:
        # Tell the user that the page is restricted
        return HttpResponse("You are not authorized to view this page")

    # Create a context dictionary which we can pass to the template
    context_dict = {}

    # Place the user's username in the context dictionary
    context_dict['username'] = user.username

    # Retrieve all of the associated reports
    # Note that filter returns >= 1 model instance
    reports = Report.objects.filter(user=user)

    # Adds our results list to the template context under name reports
    context_dict['reports'] = reports

    # Go render the response and return it to the client.
    return render(request, 'app/user.html', context_dict)

@login_required
def add_report(request, user_name_slug):

    # Obtain information about the user attempting to view the page
    user = request.user

    # Check if the requested home page belongs to the current user
    if user.username != user_name_slug:
        # Tell the user that the page is restricted
        return HttpResponse("You are not authorized to view this page")

    if request.method == 'POST':
        form = ReportForm(data=request.POST)
        
        # Have we been provided with a valid form?
        if form.is_valid():
            report = form.save()
            # Set the user
            report.user = user
            # Other information should already be created or given default value
            report.save()
            return user(request, user_name_slug)
        else:
            print(form.errors)
    else:
        form = ReportForm()

    context_dict = {'form':form, 'user': user}

    return render(request, 'app/add_report.html', context_dict)                        