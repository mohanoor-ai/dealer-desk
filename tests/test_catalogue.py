from backend.models import Vehicle,VehiclePhoto,Enquiry

def test_catalogue_exposes_only_sample_fields_and_illustrative_photos(client,app):
    with app.state.sessions() as db:
        cars=[Vehicle(make='Ford',model='Puma (sample)',year=2026,price_pence=2714500,approved_facts=['Private staff note']),Vehicle(make='Private',model='Actual stock',year=2025,price_pence=100),Vehicle(make='Archived',model='Hidden (sample)',year=2024,price_pence=100,archived=True)]
        cars.append(Vehicle(make='Deployment',model='Verification (sample)',year=2025,price_pence=100))
        db.add_all(cars);db.flush()
        def photo(v,illustrative):
            p=VehiclePhoto(vehicle_id=v.id,caption='Reference photo',credit='Photographer',source_url='https://example.com/photo',license='CC BY-SA',license_url='https://example.com/license',illustrative=illustrative,is_cover=True,width=1,height=1,content=b'image',thumbnail=b'thumb');db.add(p);db.flush();return p.id
        allowed=photo(cars[0],True);private=photo(cars[1],True);nonillustration=photo(cars[0],False);archived=photo(cars[2],True);operational=photo(cars[3],True)
        db.add(Enquiry(vehicle_id=cars[0].id,customer='Private person',message='Do not expose'));db.commit()
    r=client.get('/api/catalogue');assert r.status_code==200
    rows=r.json()['items'];assert len(rows)==1
    assert set(rows[0])=={'id','make','model','year','price_pence','status','photos'}
    assert [p['id'] for p in rows[0]['photos']]==[allowed]
    assert 'Private person' not in r.text and 'Private staff note' not in r.text
    assert client.get(f'/api/catalogue/photos/{allowed}').content==b'image'
    assert client.get(f'/api/catalogue/photos/{allowed}?thumbnail=true').content==b'thumb'
    for denied in [private,nonillustration,archived,operational,99999]:assert client.get(f'/api/catalogue/photos/{denied}').status_code==404
    assert client.get('/api/vehicles').status_code==401
    assert client.get('/api/enquiries').status_code==401
    assert client.post('/api/catalogue',json={}).status_code==405
