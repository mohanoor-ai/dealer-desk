import {afterEach,expect,test,vi} from 'vitest';
import {request,photoUrl} from './api';
import {startDemo,endDemo,demoActive} from './demo';
const seed=[{id:1,make:'Ford',model:'Puma',year:2026,price_pence:2714500,status:'available' as const}];

afterEach(()=>{endDemo();vi.useRealTimers();vi.unstubAllGlobals();});
test('demo journeys never send business requests to the server',async()=>{
  vi.stubGlobal('fetch',vi.fn());startDemo('dealer',seed);
  const enquiry=await request<{id:number}>('/api/enquiries','POST',{vehicle_id:1,customer:'Sample buyer',message:'Test drive'});
  await request('/api/tasks','POST',{enquiry_id:enquiry.id,due_date:'2026-10-25',note:'Sample follow-up'});
  await request('/api/vehicles/1','PATCH',{revision:1,status:'reserved'});
  await expect(request('/api/vehicles/1','PATCH',{revision:1,status:'sold'})).rejects.toThrow('Record changed');
  await expect(request('/api/auth/login','POST',{})).rejects.toThrow('unavailable');
  expect(fetch).not.toHaveBeenCalled();
});
test('customer cannot modify stock; reset isolates data and ending discards it',async()=>{
  startDemo('customer',seed);
  await expect(request('/api/vehicles/1','PATCH',{revision:1,status:'sold'})).rejects.toThrow('Customers');
  await request('/api/enquiries','POST',{vehicle_id:1,customer:'Fictional',message:'Hello'});
  startDemo('dealer',seed);
  expect(await request('/api/enquiries')).toMatchObject({total:0});
  endDemo();expect(demoActive()).toBe(false);
});
test('expiry denies access without falling through to the server',async()=>{
  vi.useFakeTimers();vi.stubGlobal('fetch',vi.fn());startDemo('dealer',seed);
  vi.advanceTimersByTime(30*60*1000);
  await expect(request('/api/vehicles')).rejects.toThrow('expired');
  expect(fetch).not.toHaveBeenCalled();
});
test('record quota bounds memory and photo uploads are unavailable',async()=>{
  startDemo('dealer',seed);
  for(let i=0;i<50;i++)await request('/api/enquiries','POST',{vehicle_id:1,customer:'Sample',message:'Hello'});
  await expect(request('/api/enquiries','POST',{})).rejects.toThrow('limit');
  await expect(request('/api/vehicles/1/photos','POST',{})).rejects.toThrow('staff account');
});

test('demo copies all current public listings and reset discards edits without mutating the source',async()=>{
 const catalogue=Array.from({length:10},(_,i)=>({...seed[0],id:i+3,model:`Current model ${i}`,price_pence:2700000+i}));
 startDemo('dealer',catalogue);
 const result=await request<{items:{id:number;model:string;year:number;price_pence:number}[];total:number}>('/api/vehicles');
 expect(result.total).toBe(10);expect(result.items[9]).toMatchObject({id:12,model:'Current model 9',year:2026,price_pence:2700009});
 await request('/api/vehicles/3','PATCH',{revision:1,price_pence:100});
 expect(catalogue[0].price_pence).toBe(2700000);
 startDemo('dealer',catalogue);expect(await request('/api/vehicles/3')).toMatchObject({price_pence:2700000});
 endDemo();expect(()=>startDemo('dealer',[])).toThrow('no public vehicles');expect(demoActive()).toBe(false);
});
test('demo reads credited public photo metadata from memory and uses the public image endpoint',async()=>{
 const photo={id:42,vehicle_id:1,caption:'Reference photo',credit:'Photographer',source_url:'https://example.com/photo',license:'CC BY-SA 4.0',license_url:'https://creativecommons.org/licenses/by-sa/4.0/',illustrative:true,is_cover:true,width:800,height:600,created_at:'2026-10-25'};
 startDemo('dealer',[{...seed[0],photos:[photo]}]);vi.stubGlobal('fetch',vi.fn());
 expect(await request('/api/vehicles/1/photos')).toEqual([photo]);
 expect(photoUrl(42,true)).toBe('/api/catalogue/photos/42?thumbnail=true');expect(fetch).not.toHaveBeenCalled();
 endDemo();expect(photoUrl(42)).toBe('/api/photos/42/image');
});
