import {afterEach,beforeEach,expect,test,vi} from 'vitest';
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import App from './App';
import {poundsToPence,request,modelForSave} from './api';
import {endDemo} from './demo';

beforeEach(()=>{window.location.hash='/stock';vi.stubGlobal('fetch',vi.fn());});
afterEach(()=>{cleanup();endDemo();vi.unstubAllGlobals();});
function reply(data:unknown,status=200){return {ok:status>=200&&status<300,status,json:async()=>data};}

test('money uses exact pennies and rejects malformed amounts',()=>{
  expect(poundsToPence('12.30')).toBe(1230);
  for(const bad of ['-1','1.005','abc'])expect(()=>poundsToPence(bad)).toThrow();
});
test('API sends same-origin session and mutation header, handles logout and conflict',async()=>{
  vi.mocked(fetch).mockResolvedValueOnce(reply(undefined,204) as Response);
  await expect(request('/api/auth/logout','POST')).resolves.toBeUndefined();
  expect(fetch).toHaveBeenCalledWith('/api/auth/logout',expect.objectContaining({credentials:'same-origin',headers:expect.objectContaining({'X-Requested-With':'DealerDesk'})}));
  vi.mocked(fetch).mockResolvedValueOnce(reply({error:{message:'Record changed'}},409) as Response);
  await expect(request('/api/vehicles/1','PATCH',{revision:1})).rejects.toThrow('Record changed');
});
test('sign in uses individual credentials and displays backend errors',async()=>{
  vi.mocked(fetch).mockResolvedValue(reply({error:{message:'Please sign in.'}},401) as Response);
  render(<App/>);
  const username=await screen.findByLabelText('Username');
  fireEvent.change(username,{target:{value:'sales'}});
  fireEvent.change(screen.getByLabelText('Password'),{target:{value:'incorrect'}});
  vi.mocked(fetch).mockResolvedValue(reply({error:{message:'Username or password is incorrect.'}},401) as Response);
  fireEvent.click(screen.getByRole('button',{name:'Sign in'}));
  expect(await screen.findByRole('alert')).toHaveTextContent('Username or password is incorrect.');
});
test('viewer gets useful empty state without write controls',async()=>{
  vi.mocked(fetch).mockImplementation(async(input)=>String(input).includes('/auth/me')?
    reply({id:3,username:'viewer',role:'viewer'}) as Response:reply({items:[],total:0}) as Response);
  render(<App/>);
  expect(await screen.findByText('You have read-only access. Contact a manager to request changes.')).toBeInTheDocument();
  expect(await screen.findByText('Your stock starts here')).toBeInTheDocument();
  expect(screen.queryByRole('button',{name:'Save vehicle'})).not.toBeInTheDocument();
});

test('customer demo starts without login and ends back at staff sign-in',async()=>{
  vi.mocked(fetch).mockImplementation(async(input)=>String(input)==='/api/catalogue'?reply({items:[{id:1,make:'Ford',model:'Puma',year:2026,price_pence:2714500,status:'available'},{id:2,make:'Nissan',model:'Qashqai',year:2026,price_pence:3063500,status:'available'}]}) as Response:reply({error:{message:'Please sign in.'}},401) as Response);
  render(<App/>);
  fireEvent.click(await screen.findByRole('button',{name:'Try demo'}));
  fireEvent.click(screen.getByRole('button',{name:'Explore customer demo'}));
  expect(await screen.findByRole('heading',{name:'Try a vehicle enquiry'})).toBeInTheDocument();
  expect((await screen.findAllByText(/Ford Puma/)).length).toBeGreaterThan(0);
  fireEvent.click(screen.getByRole('link',{name:'View Nissan Qashqai'}));
  expect(await screen.findByRole('heading',{name:'Nissan Qashqai',level:1})).toBeInTheDocument();
  expect(screen.getByLabelText('Vehicle')).toHaveValue('2');
  expect(screen.queryByRole('link',{name:'Follow-ups'})).not.toBeInTheDocument();
  expect(screen.queryByRole('button',{name:'Save vehicle'})).not.toBeInTheDocument();
  fireEvent.change(screen.getByLabelText('Customer name'),{target:{value:'Fictional buyer'}});
  fireEvent.change(screen.getByLabelText('Message'),{target:{value:'Sample test drive'}});
  fireEvent.click(screen.getByRole('button',{name:'Save enquiry'}));
  expect(await screen.findByText('Saved successfully.')).toBeInTheDocument();
  expect(vi.mocked(fetch).mock.calls.every(([url])=>String(url).includes('/auth/me')||String(url)==='/api/catalogue')).toBe(true);
  fireEvent.click(screen.getByRole('button',{name:'End demo'}));
  expect(await screen.findByLabelText('Password')).toBeInTheDocument();
});

 test('home separates catalogue and staff entry from optional demo choices',async()=>{
 window.location.hash='/home';
 vi.mocked(fetch).mockImplementation(async(input)=>String(input).includes('/catalogue')?reply({items:[]}) as Response:reply({error:{message:'Please sign in.'}},401) as Response);
 render(<App/>);
 expect(await screen.findByRole('heading',{name:'Find your next car.'})).toBeInTheDocument();
 expect(screen.queryByLabelText('Password')).not.toBeInTheDocument();
 expect(screen.queryByRole('button',{name:'Explore customer demo'})).not.toBeInTheDocument();
 expect(screen.getAllByRole('link',{name:/Staff sign in/}).every(a=>a.getAttribute('href')==='#/login')).toBe(true);
 });

 test('vehicle edits preserve the internal catalogue marker without duplicating it',()=>{
 expect(modelForSave('Puma Titanium','Puma (sample)')).toBe('Puma Titanium (sample)');
 expect(modelForSave('Puma (sample)','Puma (sample)')).toBe('Puma (sample)');
 expect(modelForSave(' Golf Life ','Golf')).toBe('Golf Life');
 expect(()=>modelForSave('   ','Puma (sample)')).toThrow('Enter a model name.');
 });

test('failed public catalogue loading leaves demo inactive with a recoverable error',async()=>{
 vi.mocked(fetch).mockImplementation(async(input)=>String(input)==='/api/catalogue'?reply({error:{message:'Listings unavailable'}},503) as Response:reply({error:{message:'Please sign in.'}},401) as Response);
 render(<App/>);fireEvent.click(await screen.findByRole('button',{name:'Try demo'}));fireEvent.click(screen.getByRole('button',{name:'Explore staff demo'}));
 expect(await screen.findByRole('alert')).toHaveTextContent('Listings unavailable');
 expect(screen.queryByRole('button',{name:'End demo'})).not.toBeInTheDocument();expect(screen.getByRole('button',{name:'Explore staff demo'})).toBeEnabled();
});
