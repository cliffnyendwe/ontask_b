# -*- coding: utf-8 -*-

"""Views to preview resulting text in the action."""

import json
from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from action.evaluate import (
    action_condition_evaluation, evaluate_row_action_in,
    evaluate_row_action_out, get_action_evaluation_context, get_row_values,
)
from action.models import Action
from ontask.decorators import ajax_required, get_action
from ontask.permissions import is_instructor
from workflow.models import Workflow


@csrf_exempt
@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related='actions')
def preview_next_all_false_response(
    request: HttpRequest,
    pk: Optional[int] = None,
    idx: Optional[int] = None,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> JsonResponse:
    """Preview message with all conditions evaluting to false.

    Previews the message that has all conditions incorrect in the position
    next to the one specified by idx

    The function uses the list stored in rows_all_false and finds the next
    index in that list (or the first one if it is the last. It then invokes
    the preview_response method

    :param request: HTTP Request object

    :param pk: Primary key of the action

    :param idx:

    :return:
    """
    # Get the list of indeces
    idx_list = action.rows_all_false

    if not idx_list:
        # If empty, or None, something went wrong.
        return JsonResponse({'html_redirect': reverse('home')})

    # Search for the next element bigger than idx
    next_idx = next((nxt for nxt in idx_list if nxt > idx), None)

    if not next_idx:
        # If nothing found, then take the first element
        next_idx = idx_list[0]

    # Return the rendering of the given element
    return preview_response(request, pk, idx=next_idx, action=action)


@csrf_exempt
@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related='actions')
def preview_response(
    request: HttpRequest,
    pk: int,
    idx: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> JsonResponse:
    """Preview content of action.

    HTML request and the primary key of an action to preview one of its
    instances. The request must provide and additional parameter idx to
    denote which instance to show.

    :param request: HTML request object

    :param pk: Primary key of the an action for which to do the preview

    :param idx: Index of the reponse to preview

    :param action: Might have been fetched already

    :return: JsonResponse
    """
    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)
        action.save()

    # Get the total number of items
    filter_obj = action.get_filter()
    n_items = filter_obj.n_rows_selected if filter_obj else workflow.nrows

    # Set the idx to a legal value just in case
    if not 1 <= idx <= n_items:
        idx = 1

    prv = idx - 1
    if prv <= 0:
        prv = n_items

    nxt = idx + 1
    if nxt > n_items:
        nxt = 1

    row_values = get_row_values(action, idx)

    # Obtain the dictionary with the condition evaluation
    condition_evaluation = action_condition_evaluation(action, row_values)
    # Get the dictionary containing column names, attributes and condition
    # valuations:
    context = get_action_evaluation_context(
        action,
        row_values,
        condition_evaluation)

    all_false = False
    if action.conditions.filter(is_filter=False).count():
        # If there are conditions, check if they are all false
        all_false = all(
            not bool_val for __, bool_val in condition_evaluation.items()
        )

    # Evaluate the action content.
    show_values = ''
    correct_json = True
    if action.is_out:
        action_content = evaluate_row_action_out(action, context)
        if action.action_type == Action.personalized_json:
            try:
                json.loads(action_content)
            except Exception:
                correct_json = False
    else:
        action_content = evaluate_row_action_in(action, context)
    if action_content is None:
        action_content = _(
            'Error while retrieving content for student {0}',
        ).format(idx)
    else:
        # Get the conditions used in the action content
        act_cond = action.get_used_conditions()
        # Get the variables/columns from the conditions
        act_vars = set().union(
            *[
                cond.columns.all()
                for cond in action.conditions.filter(name__in=act_cond)
            ],
        )
        # Sort the variables/columns  by position and get the name
        show_values = ', '.join(
            [
                '{0} = {1}'.format(col.name, row_values[col.name])
                for col in act_vars
            ],
        )

    uses_plain_text = (
        action.action_type == Action.personalized_canvas_email
        or action.action_type == Action.personalized_json
    )
    if uses_plain_text:
        action_content = escape(action_content)

    # See if there is prelude content in the request
    prelude = request.GET.get('subject_content')
    if prelude:
        prelude = evaluate_row_action_out(action, context, prelude)

    return JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_preview.html',
            {
                'action': action,
                'action_content': action_content,
                'index': idx,
                'n_items': n_items,
                'nxt': nxt,
                'prv': prv,
                'prelude': prelude,
                'correct_json': correct_json,
                'show_values': show_values,
                'all_false': all_false,
            },
            request=request),
    })