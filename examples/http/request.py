from jsonrpcclient.clients.http_client import HTTPClient
#
# client = HTTPClient("http://localhost:5000/rpc/")
# response = client.request("add")
# print(response.data.result)
import time;

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


def get_client():
    tracer_interceptor = open_tracing_client_interceptor(tracer)
    client = HTTPClient("http://localhost:5000/rpc/", interceptor=tracer_interceptor)
    return client

def main(client):
    response = client.request("add")
    return response.data.result


active_span_source = FixedActiveSpanSource()
def get_client2():
    tracer_interceptor = open_tracing_client_interceptor(tracer, active_span_source=active_span_source)
    client = HTTPClient("http://localhost:5000/rpc/", interceptor=tracer_interceptor)
    return client

def main2(client):

    with tracer.start_span('command_line_client_span') as span:
        span.log_kv({'ahahaha': 'monster'})
        active_span_source.active_span = span
        response = client.request("add")
        return response.data.result

if __name__ == '__main__':

    t = time.time()
    for ii in range(1000):
        client = get_client2()
        res = main2(client)

        # client = get_client()
        # res = main(client)

        # print(ii)
        # print(res)
    print(time.time() - t)
    time.sleep(2)
    tracer.close()
