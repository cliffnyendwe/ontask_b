# -*- coding: utf-8 -*-

"""Classes to represent errors while executing services."""
from ontask import OnTaskServiceException


class OnTaskWorkflowAddColumn(OnTaskServiceException):
    """Raised when an error appears in store_dataframe."""


class OnTaskWorkflowIntegerLowerThanOne(OnTaskServiceException):
    """Raised when an integer value incorrect."""


class OnTaskWorkflowStoreError(OnTaskServiceException):
    """Raised when an error appears in store_dataframe."""


class OnTaskWorkflowNoCategoryValues(OnTaskServiceException):
    """Raised when an error appears in store_dataframe."""


class OnTaskWorkflowImportError(OnTaskServiceException):
    """Raised when an error appears in store_dataframe."""


class OnTaskWorkflowIncorrectEmail(OnTaskServiceException):
    """Raised when an error appears in store_dataframe."""
