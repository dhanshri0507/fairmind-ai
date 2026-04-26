import urllib.request, urllib.error, json

req = urllib.request.Request(
    'https://fairmindai-production.up.railway.app/api/explain',
    data=json.dumps({'audit_id': 'test', 'mode': 'professional', 'audit_results': {'fairness_score': 80}}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    print(urllib.request.urlopen(req).read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(e.read().decode('utf-8'))
