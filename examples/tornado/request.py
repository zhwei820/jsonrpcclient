from tornado.ioloop import IOLoop
from jsonrpcclient.clients.tornado_client import TornadoClient

from jsonrpcclient.opentracing import open_tracing_client_interceptor
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


async def spantest():

    with tracer.start_span('command_line_client_span') as span:
        tracer_interceptor = open_tracing_client_interceptor(tracer, active_span_source=span)
        span.log_kv({'ahahaha': 'monster'})

        client = TornadoClient("http://localhost:5000/rpc/", interceptor=tracer_interceptor)
        response = await client.request("add")
        return response.data.result


res = IOLoop.current().run_sync(main)
print(res)
res = IOLoop.current().run_sync(spantest)
print(res)

import time; time.sleep(2)
tracer.close()
