import base64
from io import BytesIO
from PIL import Image
from fastapi.testclient import TestClient
from backend.app import create_app
from conftest import sign_in

def picture(color='green', exif=False):
    image=Image.new('RGB',(120,80),color)
    output=BytesIO()
    metadata=Image.Exif()
    if exif:
        metadata[271]='Private camera metadata'
        metadata[274]=6
    image.save(output,'JPEG',exif=metadata)
    return 'data:image/jpeg;base64,'+base64.b64encode(output.getvalue()).decode()

def vehicle(client):
    return client.post('/api/vehicles',json={'make':'Demo','model':'Photo Test','year':2026,'price_pence':12300}).json()

def upload(client, vehicle_id, revision=1, **changes):
    return client.post(f'/api/vehicles/{vehicle_id}/photos',json={
        'revision':revision,'caption':'Fictional test photo','rights_confirmed':True,
        'data_url':picture(),**changes})

def test_photo_persists_and_metadata_is_removed(signed_client, app):
    client=signed_client;stock=vehicle(client)
    response=upload(client,stock['id'],data_url=picture(exif=True))
    assert response.status_code==201,response.text
    photo=response.json()['photo']
    assert (photo['width'],photo['height'])==(80,120)
    assert response.json()['vehicle_revision']==2
    assert 'content' not in photo
    read=client.get(f"/api/photos/{photo['id']}/image")
    assert read.headers['content-type']=='image/jpeg'
    with Image.open(BytesIO(read.content)) as decoded:
        assert not decoded.getexif()
    summary=client.get(f"/api/vehicles/{stock['id']}").json()
    assert summary['photo_count']==1 and summary['cover_photo']['id']==photo['id']
    restarted=create_app(app.state.engine.url.render_as_string(hide_password=False))
    with TestClient(restarted,headers={'X-Requested-With':'DealerDesk'}) as second:
        sign_in(second)
        assert second.get(f"/api/photos/{photo['id']}/image").content==read.content
        assert second.get(f"/api/photos/{photo['id']}/image?thumbnail=true").status_code==200

def test_cover_selection_has_one_cover_and_revision_guard(signed_client):
    client=signed_client;stock=vehicle(client)
    first=upload(client,stock['id']).json()['photo']
    second=upload(client,stock['id'],2,data_url=picture('blue')).json()['photo']
    path=f"/api/vehicles/{stock['id']}/photos/{second['id']}/cover"
    result=client.patch(path,json={'revision':3})
    assert result.status_code==200,result.text
    assert result.json()['photo']['is_cover'] is True
    assert client.patch(path,json={'revision':3}).status_code==409
    photos=client.get(f"/api/vehicles/{stock['id']}/photos").json()
    assert [photo['id'] for photo in photos if photo['is_cover']]==[second['id']]
    other=vehicle(client)
    assert client.patch(f"/api/vehicles/{other['id']}/photos/{first['id']}/cover",json={'revision':1}).status_code==404

def test_photo_validation_and_rights(signed_client,monkeypatch):
    client=signed_client;stock=vehicle(client)
    for changes in [{'data_url':'data:image/svg+xml;base64,PHN2Zz4='},
        {'data_url':'data:image/jpeg;base64,bm90IGEgcGhvdG8='},
        {'rights_confirmed':False},{'source_url':'javascript:alert(1)'},
        {'license_url':'http://example.com/license'}]:
        assert upload(client,stock['id'],**changes).status_code==422
    monkeypatch.setattr('backend.photos.MAX_PIXELS',100)
    assert upload(client,stock['id']).status_code==422
    assert client.get(f"/api/vehicles/{stock['id']}").json()['revision']==1

def test_photo_quota_and_stale_upload_are_transactional(signed_client):
    client=signed_client;stock=vehicle(client)
    assert upload(client,stock['id']).status_code==201
    assert upload(client,stock['id']).status_code==409
    for revision in range(2,13):
        assert upload(client,stock['id'],revision).status_code==201
    assert upload(client,stock['id'],13).status_code==409
    current=client.get(f"/api/vehicles/{stock['id']}").json()
    assert current['revision']==13 and current['photo_count']==12

def test_photo_access_is_enforced_by_server(client,signed_client):
    stock=vehicle(signed_client)
    photo=upload(signed_client,stock['id']).json()['photo']
    client.post('/api/auth/logout')
    assert client.get(f"/api/photos/{photo['id']}/image").status_code==401
    sign_in(client,'viewer')
    assert client.get(f"/api/photos/{photo['id']}/image").status_code==200
    assert upload(client,stock['id'],2).status_code==403
    assert client.patch(f"/api/vehicles/{stock['id']}/photos/{photo['id']}/cover",json={'revision':2}).status_code==403

def test_oversized_body_rejected_before_decode(signed_client):
    response=signed_client.post('/api/vehicles/1/photos',content=b'x'*3_000_001,
                               headers={'Content-Type':'application/json'})
    assert response.status_code==413
