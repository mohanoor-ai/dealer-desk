import {afterEach,expect,test,vi} from 'vitest';
import {request} from './api';
import {startDemo,endDemo,demoActive} from './demo';
afterEach(()=>{endDemo();vi.useRealTimers();vi.unstubAllGlobals();});
test('demo journeys never send business requests to the server',async()=>{
  vi.stubGlobal('fetch',vi.fn());startDemo('dealer');
  const enquiry=await request<{id:number}>('/api/enquiries','POST',{vehicle_id:1,customer:'Sample buyer',message:'Test drive'});
  await request('/api/tasks','POST',{enquiry_id:enquiry.id,due_date:'2026-10-25',note:'Sample follow-up'});
  await request('/api/vehicles/1','PATCH',{revision:1,status:'reserved'});
  await expect(request('/api/vehicles/1','PATCH',{revision:1,status:'sold'})).rejects.toThrow('Record changed');
  await expect(request('/api/auth/login','POST',{})).rejects.toThrow('unavailable');
  expect(fetch).not.toHaveBeenCalled();
});
test('customer cannot modify stock; reset isolates data and ending discards it',async()=>{
  startDemo('customer');
  await expect(request('/api/vehicles/1','PATCH',{revision:1,status:'sold'})).rejects.toThrow('Customers');
  await request('/api/enquiries','POST',{vehicle_id:1,customer:'Fictional',message:'Hello'});
  startDemo('dealer');
  expect(await request('/api/enquiries')).toMatchObject({total:0});
  endDemo();expect(demoActive()).toBe(false);
});
test('expiry denies access without falling through to the server',async()=>{
  vi.useFakeTimers();vi.stubGlobal('fetch',vi.fn());startDemo('dealer');
  vi.advanceTimersByTime(30*60*1000);
  await expect(request('/api/vehicles')).rejects.toThrow('expired');
  expect(fetch).not.toHaveBeenCalled();
});
test('record quota bounds memory and photo uploads are unavailable',async()=>{
  startDemo('dealer');
  for(let i=0;i<50;i++)await request('/api/enquiries','POST',{vehicle_id:1,customer:'Sample',message:'Hello'});
  await expect(request('/api/enquiries','POST',{})).rejects.toThrow('limit');
  await expect(request('/api/vehicles/1/photos','POST',{})).rejects.toThrow('staff account');
});
