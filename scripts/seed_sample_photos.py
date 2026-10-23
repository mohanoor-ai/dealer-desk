"""Attach bundled licensed references to existing sample vehicles, without replacing photos."""
import argparse
import base64
import getpass
import json
from pathlib import Path
import urllib.request
import urllib.error
import http.cookiejar

def attach_photos(base_url, username, password):
    cookies=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
    def request(path, data=None):
        payload=None if data is None else json.dumps(data).encode()
        req=urllib.request.Request(base_url.rstrip('/')+path, data=payload,
            headers={'Content-Type':'application/json','X-Requested-With':'DealerDesk'})
        with opener.open(req,timeout=30) as response:
            return json.load(response) if response.status!=204 else None
    request('/api/auth/login',{'username':username,'password':password})
    folder=Path(__file__).resolve().parents[1]/'sample-assets'/'stock'
    credits=json.loads((folder/'credits.json').read_text(encoding='utf-8'))
    offset=0;vehicles=[]
    while True:
        page=request(f'/api/vehicles?limit=100&offset={offset}')
        vehicles.extend(page['items']);offset+=len(page['items'])
        if offset>=page['total']:break
    added=0
    for credit in credits:
        for vehicle in vehicles:
            if vehicle['make']!=credit['make'] or not vehicle['model'].endswith('(sample)'):
                continue
            photos=request(f"/api/vehicles/{vehicle['id']}/photos")
            if any(photo['source_url']==credit['source_url'] for photo in photos):
                continue
            result=request(f"/api/vehicles/{vehicle['id']}/photos",{
                'revision':vehicle['revision'], 'data_url':'data:image/jpeg;base64,'+
                    base64.b64encode((folder/credit['file']).read_bytes()).decode(),
                'caption':credit['caption'],'rights_confirmed':True,'illustrative':True,
                'credit':credit['credit'],'source_url':credit['source_url'],
                'license':credit['license'],'license_url':credit['license_url']})
            assert result['photo']['illustrative']
            added+=1
    request('/api/auth/logout',{})
    return added

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',default='http://127.0.0.1:8090')
    parser.add_argument('--username',required=True)
    args=parser.parse_args()
    try:
        print('Added',attach_photos(args.base_url,args.username,getpass.getpass('Password: ')),'licensed sample illustrations.')
    except urllib.error.HTTPError as error:
        raise SystemExit(f'API request failed ({error.code}); existing photos were preserved.')
