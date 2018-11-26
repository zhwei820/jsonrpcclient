from tornado.ioloop import IOLoop
from functools import partial
import random
from jsonrpcclient.clients.tornado_client import TornadoClient

from jsonrpcclient.opentracing import open_tracing_client_interceptor, FixedActiveSpanSource
from jaeger_client import Config

config = Config(
    config={
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'logging': True,
    },
    service_name='trivial-client')

tracer = config.initialize_tracer()

async def main():
    tracer_interceptor = open_tracing_client_interceptor(tracer)

    client = TornadoClient("http://localhost:5000/rpc/", interceptor=tracer_interceptor)
    response = await client.request("add")
    return response.data.result
res = IOLoop.current().run_sync(main)
print(res)


active_span_source = FixedActiveSpanSource()
tracer_interceptor = open_tracing_client_interceptor(tracer, active_span_source=active_span_source)
client = TornadoClient("http://localhost:5000/rpc/", interceptor=tracer_interceptor)

async def spantest(test_para=''):

    with tracer.start_span('command_line_client_span') as span:
        span.log_kv({'ahahaha': 'monster'})
        active_span_source.active_span = span
        response = await client.request("add")
        return response.data.result

for ii in range(1000):
    ss = ''.join(random.choices('qwertyuiop', k=5)) + str(ii)
    print(ss)
    spantest1 = partial(spantest, test_para=ss)
    res = IOLoop.current().run_sync(spantest)
    print(res)

import time; time.sleep(2)
tracer.close()
