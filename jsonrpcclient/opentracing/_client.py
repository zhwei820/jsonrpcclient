"""Implementation of the invocation-side open-tracing interceptor."""

import sys
import logging

from six import iteritems

from ._utilities import get_method_type, get_deadline_millis,\
    log_or_wrap_request_or_iterator, RpcInfo
import opentracing
from opentracing.ext import tags as ot_tags


class _GuardedSpan(object):

    def __init__(self, span):
        self.span = span
        self._engaged = True

    def __enter__(self):
        self.span.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        if self._engaged:
            return self.span.__exit__(*args, **kwargs)
        else:
            return False

    def release(self):
        self._engaged = False
        return self.span


def _inject_span_context(tracer, span, metadata):
    headers = {}
    try:
        tracer.inject(span.context, opentracing.Format.HTTP_HEADERS, headers)
    except (opentracing.UnsupportedFormatException,
            opentracing.InvalidCarrierException,
            opentracing.SpanContextCorruptedException) as e:
        logging.exception('tracer.inject() failed')
        span.log_kv({'event': 'error', 'error.object': e})
        return metadata
    metadata.update(headers)
    return metadata


def get_method(sss):

    for ss in sss.split(','):
        if 'method":' in ss:
            s = ss.split(':')[1]
            return s[2:-1]
    return ''

class OpenTracingClientInterceptor():

    def __init__(self, tracer, active_span_source, log_payloads,
                 span_decorator):
        self._tracer = tracer
        self._active_span_source = active_span_source
        self._log_payloads = log_payloads
        self._span_decorator = span_decorator

    def _start_span(self, method):
        active_span_context = None
        if self._active_span_source is not None:
            active_span = self._active_span_source.get_active_span()
            if active_span is not None:
                active_span_context = active_span.context
        tags = {
            ot_tags.COMPONENT: 'jsonrpc',
            ot_tags.SPAN_KIND: ot_tags.SPAN_KIND_RPC_CLIENT
        }
        return self._tracer.start_span(
            operation_name=method, child_of=active_span_context, tags=tags)

    def _start_guarded_span(self, *args, **kwargs):
        return _GuardedSpan(self._start_span(*args, **kwargs))

    def trace_before_request(self, request, headers):
        with self._start_guarded_span(get_method(request)) as guarded_span:
            headers = _inject_span_context(self._tracer, guarded_span.span, headers)

            if self._log_payloads:
                guarded_span.span.log_kv({'request': request})

            return guarded_span, headers

    def trace_after_request(self, response, guarded_span):
        if self._log_payloads:
            guarded_span.span.log_kv({'response': response.body})
