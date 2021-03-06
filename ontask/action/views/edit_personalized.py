# -*- coding: utf-8 -*-

"""Views to edit actions that send personalized information."""
from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from ontask import models
from ontask.action import forms
from ontask.core import ajax_required, get_action, is_instructor


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@get_action(pf_related='actions')
def save_text(
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> JsonResponse:
    """Save text content of the action.

    :param request: HTTP request (POST)
    :param pk: Action ID
    :param workflow: Workflow being manipulated (set by the decorators)
    :param action: Action being saved (set by the decorators)
    :return: Nothing, changes reflected in the DB
    """
    del pk, workflow
    # Wrong type of action.
    if action.is_in:
        return JsonResponse({'html_redirect': reverse('home')})

    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)
        action.save()

    return JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
@ajax_required
@get_action()
def showurl(
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> JsonResponse:
    """Create page to show URL to access action.

    Function that given a JSON request with an action pk returns the URL used
    to retrieve the personalised message.

    :param request: Json request
    :param pk: Primary key of the action to show the URL
    :param workflow: Workflow being manipulated (set by the decorators)
    :param action: Action being manipulated (set by the decorators)
    :return: Json response with the content to show in the screen
    """
    del pk, workflow
    form = forms.EnableURLForm(request.POST or None, instance=action)

    if request.method == 'POST' and form.is_valid():
        if form.has_changed():
            # Reflect the change in the action element
            form.save()

            # Recording the event
            action.log(
                request.user,
                models.Log.ACTION_SERVE_TOGGLED,
                served_enabled=action.serve_enabled)

            return JsonResponse({'html_redirect': reverse('action:index')})

        return JsonResponse({'html_redirect': None})

    # Render the page with the absolute URI
    return JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_action_showurl.html',
            {'url_text': request.build_absolute_uri(
                reverse('action:serve_lti') + '?id=' + str(action.id)),
             'form': form,
             'action': action},
            request=request),
    })
