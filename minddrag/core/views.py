from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from core import models

def index(request):
    """
    The minddrag homepage
    """
    return render_to_response('index.html',
                              {},
                              context_instance=RequestContext(request))


@login_required
def my_dragables(request):
    """
    The page where users can view their dragables.
    """
    dragables = models.Dragable.objects.filter(created_by=request.user)
    return render_to_response('members/my_dragables.html',
                              {'dragables': dragables},
                              context_instance=RequestContext(request))
