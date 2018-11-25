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
tracer_interceptor = open_tracing_client_interceptor(tracer)

client = TornadoClient("http://localhost:5000/rpc/", interceptor=tracer_interceptor)


async def main():
    response = await client.request("add")
    print(response.data.result)


IOLoop.current().run_sync(main)

import time; time.sleep(1)
tracer.close()
