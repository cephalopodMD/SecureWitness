__author__ = 'acl3qb'

from django.template import RequestContext
from django.shortcuts import render_to_response

def index(request):
    context = RequestContext(request)
    context_dict = {}
    return render_to_response('index.html', context_dict, context)