# -*- coding: utf-8 -*-

"""Functions to save the different types of scheduled actions."""

from datetime import datetime

from django import http
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext, ugettext_lazy as _
import pytz

from ontask import models
from ontask.core import SessionPayload
from ontask.scheduler import forms, services


class ScheduledOperationSaveBase:
    """Base class for all the scheduled operation save producers."""

    def __init__(self, form_class: forms.ScheduleBasicForm):
        """Assign the form class."""
        self.form_class = form_class

    def process(
        self,
        operation_type: str,
        request: http.HttpRequest,
        action: models.Action,
        schedule_item: models.ScheduledOperation,
        prev_url: str,
    ) -> http.HttpResponse:
        """Process the request."""
        op_payload = services.create_payload(
            request,
            operation_type,
            prev_url,
            schedule_item,
            action)

        form = self.form_class(
            form_data=request.POST or None,
            action=action,
            instance=schedule_item,
            columns=action.workflow.columns.filter(is_key=True),
            form_info=op_payload)
        if request.method == 'POST' and form.is_valid():
            return self.process_post(request, schedule_item, op_payload)

        # Render the form
        return render(
            request,
            'scheduler/edit.html',
            {
                'action': action,
                'form': form,
                'now': datetime.now(pytz.timezone(settings.TIME_ZONE)),
                'valuerange': range(2),
            },
        )

    def process_post(
        self,
        request: http.HttpRequest,
        schedule_item: models.ScheduledOperation,
        op_payload: SessionPayload,
    ):
        """Process a POST request."""
        del request, schedule_item, op_payload
        raise ValueError('Incorrect  invocation of process_post method')

    def finish(
        self,
        request: http.HttpRequest,
        payload: SessionPayload,
        schedule_item: models.ScheduledOperation = None,
    ) -> http.HttpResponse:
        """Finalize the creation of a scheduled operation.

        All required data is passed through the payload.

        :param request: Request object received

        :param schedule_item: ScheduledOperation item being processed. If None,
        it has to be extracted from the information in the payload.

        :param payload: Dictionary with all the required data coming from
        previous requests.

        :return: Http Response
        """
        # Get the scheduled operation
        s_item_id = payload.pop('schedule_id', None)
        action = models.Action.objects.get(pk=payload.pop('action_id'))
        column_pk = payload.pop('item_column', None)
        column = None
        if column_pk:
            column = action.workflow.columns.filter(pk=column_pk).first()

        # Remove some parameters from the payload
        for key in [
            'button_label',
            'valuerange',
            'step',
            'prev_url',
            'post_url',
            'confirm_items',
        ]:
            payload.pop(key, None)
        operation_type = payload.pop('operation_type')

        if s_item_id:
            # Get the item being processed
            if not schedule_item:
                schedule_item = models.ScheduledOperation.objects.filter(
                    id=s_item_id).first()
            if not schedule_item:
                messages.error(
                    request,
                    _('Incorrect request for operation scheduling'))
                return redirect('action:index')
        else:
            schedule_item = models.ScheduledOperation(
                user=request.user,
                workflow=action.workflow,
                action=action,
                operation_type=operation_type)

        # Check for exclude
        schedule_item.name = payload.pop('name')
        schedule_item.description_text = payload.pop('description_text')
        schedule_item.item_column = column
        schedule_item.execute = parse_datetime(payload.pop('execute'))
        schedule_item.execute_until = parse_datetime(
            payload.pop('execute_until'))
        schedule_item.exclude_values = payload.pop('exclude_values', [])

        schedule_item.status = models.scheduler.STATUS_PENDING
        schedule_item.payload = payload.get_store()
        schedule_item.save()

        schedule_item.log(models.Log.SCHEDULE_EDIT)

        # Reset object to carry action info throughout dialogs
        SessionPayload.flush(request.session)

        # Successful processing.
        tdelta = services.create_timedelta_string(
            schedule_item.execute,
            schedule_item.execute_until)
        return render(
            request,
            'scheduler/schedule_done.html',
            {'tdelta': tdelta, 's_item': schedule_item})


class ScheduledOperationSaveActionRun(ScheduledOperationSaveBase):
    """Base class for those saving Action Run operations."""

    def process_post(
        self,
        request: http.HttpRequest,
        schedule_item: models.ScheduledOperation,
        op_payload: SessionPayload,
    ) -> http.HttpResponse:
        """Process the valid form."""
        if op_payload.get('confirm_items'):
            # Update information to carry to the filtering stage
            op_payload['button_label'] = ugettext('Schedule')
            op_payload['valuerange'] = 2
            op_payload['step'] = 2
            op_payload.store_in_session(request.session)

            return redirect('action:item_filter')

        # Go straight to the final step
        return self.finish(request, op_payload, schedule_item)


class SchedulerCRUDFactory:
    """Factory to manipulate a scheduled operation."""

    def __init__(self):
        """Initialize the set of _creators."""
        self._producers = {}

    def _get_creator(self, operation_type):
        """Get the creator for the tiven operation_type and args."""
        creator_obj = self._producers.get(operation_type)
        if not creator_obj:
            raise ValueError(operation_type)
        return creator_obj

    def register_producer(self, operation_type: str, saver_obj):
        """Register the given object that will perform the save operation."""
        self._producers[operation_type] = saver_obj

    def crud_process(self, operation_type, **kwargs):
        """Execute the corresponding process function.

        :param operation_type: Type of scheduled item being processed. If the
        type is RUN_ACTION, the method explands its type looking at the type of
        action (either as a parameter, or within the schedule_item)

        :param kwargs: Dictionary with the following fields:
        - request: HttpRequest that prompted the process
        - action: Optional field stating the action being considered
        - schedule_item: Item being processed (if it exists)
        - prev_url: String with the URL to "go back" in case there is an
          intermediate step

        :return: HttpResponse
        """
        try:
            return self._get_creator(operation_type).process(
                operation_type,
                **kwargs)
        except ValueError:
            return render(kwargs.get('request'), 'base.html', {})

    def crud_finish(self, operation_type, **kwargs):
        """Execute the corresponding finish function.

        :param operation_type: Type of scheduled item being processed. If the
        type is RUN_ACTION, the method explands its type looking at the type
        of action (either as a parameter, or within the schedule_item)

        :param kwargs: Dictionary with the following fields:
        - request: HttpRequest that prompted the process
        - schedule_item: Item being processed (if it exists)
        - payload: Dictionary with all the additional fields for the request

        :return: HttpResponse
        """
        try:
            return self._get_creator(operation_type).finish(**kwargs)
        except ValueError:
            return render(kwargs.get('request'), 'base.html', {})


schedule_crud_factory = SchedulerCRUDFactory()
email_processor = ScheduledOperationSaveActionRun(forms.ScheduleEmailForm)
schedule_crud_factory.register_producer(
    models.Action.PERSONALIZED_TEXT,
    email_processor)
schedule_crud_factory.register_producer(
    models.Action.RUBRIC_TEXT,
    email_processor)
schedule_crud_factory.register_producer(
    models.Action.PERSONALIZED_JSON,
    ScheduledOperationSaveActionRun(forms.ScheduleJSONForm))
schedule_crud_factory.register_producer(
    models.Action.EMAIL_LIST,
    ScheduledOperationSaveActionRun(forms.ScheduleSendListForm))
schedule_crud_factory.register_producer(
    models.Action.JSON_LIST,
    ScheduledOperationSaveActionRun(forms.ScheduleJSONListForm))
