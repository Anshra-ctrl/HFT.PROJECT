import json, time, random, urllib.request, ssl, datetime, base64

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

creds = base64.b64encode(b'elastic:anshra2008').decode()

def send(doc):
    data = json.dumps(doc).encode()
    req = urllib.request.Request('https://localhost:9200/market-data/_doc', data=data, headers={'Content-Type': 'application/json', 'Authorization': 'Basic ' + creds}, method='POST')
    urllib.request.urlopen(req, context=ctx)

i = 0
while True:
    latency = random.randint(1, 50) if i % 20 != 0 else random.randint(500, 2000)
    doc = {'symbol': random.choice(['AAPL','GOOG','MSFT','TSLA']), 'price': round(random.uniform(100,500),2), 'volume': random.randint(100,5000), 'latency_us': latency, '@timestamp': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
    send(doc)
    print('Sent:', doc)
    i += 1
    time.sleep(0.5)