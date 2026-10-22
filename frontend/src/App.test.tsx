import {afterEach,beforeEach,expect,test,vi} from 'vitest';
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import App from './App';
import {poundsToPence,request} from './api';

beforeEach(()=>vi.stubGlobal('fetch',vi.fn()));
afterEach(()=>{cleanup();vi.unstubAllGlobals();});
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
