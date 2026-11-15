"""Run-scoped options shared by nested engines; never mutate GIS global environments."""
from contextvars import ContextVar

RUN_OPTIONS = ContextVar('atiaf_run_options', default={})
