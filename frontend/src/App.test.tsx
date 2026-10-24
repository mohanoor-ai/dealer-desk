import {afterEach,beforeEach,expect,test,vi} from 'vitest';
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import App from './App';
import {poundsToPence,request} from './api';
import {endDemo} from './demo';

beforeEach(()=>vi.stubGlobal('fetch',vi.fn()));
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
  vi.mocked(fetch).mockResolvedValue(reply({error:{message:'Please sign in.'}},401) as Response);
  render(<App/>);
  fireEvent.click(await screen.findByRole('button',{name:'Customer demo'}));
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
  expect(fetch).toHaveBeenCalledTimes(1);
  fireEvent.click(screen.getByRole('button',{name:'End demo'}));
  expect(await screen.findByLabelText('Password')).toBeInTheDocument();
});
