from jsonrpcclient.clients.http_client import HTTPClient

client = HTTPClient("http://localhost:5000/rpc/")
response = client.request("add")
print(response.data.result)
