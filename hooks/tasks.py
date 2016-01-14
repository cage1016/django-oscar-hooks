import decimal
import logging

import datetime
import uuid

import requests
import json
import time
import random

from Queue import Queue
from threading import Thread

from django.utils.timezone import is_aware

from oscar.core.loading import get_class, get_model

HookLog = get_model('hooks', 'HookLog')

# Set up some global variables
num_tasks_threads = 2

from django.utils.functional import Promise


class MYDjangoJSONEncoder(json.JSONEncoder):
  """
  JSONEncoder subclass that knows how to encode date/time, decimal types and UUIDs.

  [python - Why does the DjangoJSONEncoder not deal with proxy objects? - Stack Overflow](http://goo.gl/IC0dXx)
  """

  def default(self, o):
    # See "Date Time String Format" in the ECMA-262 specification.
    if isinstance(o, datetime.datetime):
      r = o.isoformat()
      if o.microsecond:
        r = r[:23] + r[26:]
      if r.endswith('+00:00'):
        r = r[:-6] + 'Z'
      return r
    elif isinstance(o, datetime.date):
      return o.isoformat()
    elif isinstance(o, datetime.time):
      if is_aware(o):
        raise ValueError("JSON can't represent timezone-aware times.")
      r = o.isoformat()
      if o.microsecond:
        r = r[:12]
      return r
    elif isinstance(o, decimal.Decimal):
      return str(o)
    elif isinstance(o, uuid.UUID):
      return str(o)
    elif isinstance(o, Promise):  # Added these lines here
      return unicode(o)
    else:
      return super(MYDjangoJSONEncoder, self).default(o)


class Tasks(object):
  def __init__(self, obj):
    self.h = obj['h']
    self.data = obj['data']
    self.headers = obj['headers']

    # Stubs for testing.
    self._sleep = time.sleep
    self._rand = random.random

  def run(self, num_retries=0):

    try:
      for retry_num in xrange(num_retries + 1):
        if retry_num > 0:
          self._sleep(self._rand() * 2 ** retry_num)
          logging.warning(
              'Retry #%d for hookevent: POST %s, following status: %d'
              % (retry_num, self.h.URL, r.status_code))

        r = requests.post(self.h.URL, data=json.dumps(self.data, cls=MYDjangoJSONEncoder), headers=self.headers)
        if r.status_code < 500:
          break

      if r.status_code in [200, 206]:
        hook_log = HookLog()
        hook_log.hook_event = self.h
        hook_log.signal_type = self.h.signal_type
        hook_log.data = self.data
        hook_log.headers = self.headers
        hook_log.request_url = self.h.URL
        hook_log.response = r.json()
        hook_log.status = r.status_code
        hook_log.retry = retry_num
        hook_log.save()

      else:
        hook_log = HookLog()
        hook_log.hook_event = self.h
        hook_log.signal_type = self.h.signal_type
        hook_log.data = self.data
        hook_log.headers = self.headers
        hook_log.request_url = self.h.URL
        hook_log.status = r.status_code
        hook_log.retry = retry_num
        hook_log.error_message = r.reason
        hook_log.save()

    except Exception as e:
      logging.warning('hookevent post error')
      logging.error(e.message)
      hook_log = HookLog()
      hook_log.hook_event = self.h
      hook_log.signal_type = self.h.signal_type
      hook_log.data = self.data
      hook_log.headers = self.headers
      hook_log.request_url = self.h.URL
      hook_log.error_message = e.message
      hook_log.save()


def sendHookEnclosures(i, q):
  while True:
    item = q.get()
    t = Tasks(item)
    t.run(num_retries=3)
    q.task_done()


def run_hook_tasks_job(qs, data):
  headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

  enclosure_queue = Queue()
  for i in range(num_tasks_threads):
    worker = Thread(target=sendHookEnclosures, args=(i, enclosure_queue))
    worker.setDaemon(True)
    worker.start()

  for h in qs:
    if h.extra_headers:
      headers.update(h.extra_headers)

    enclosure_queue.put({'h': h, 'data': data, 'headers': headers})

  enclosure_queue.join()
