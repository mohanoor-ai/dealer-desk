import {afterEach,expect,test,vi} from 'vitest';
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import {request} from './api';
import {startDemo,endDemo,switchDemoRole,restoreDemo,clearSavedDemo,demoActive} from './demo';
import {EnquiryDialog} from './DemoEnquiries';
import {CookieChoices,rememberVehicle,CompareButton,ReviewStars,PolicyPage} from './BrowsingTools';

const seed=[{id:1,make:'Ford',model:'Puma',year:2026,price_pence:2714500,status:'available' as const}];
afterEach(()=>{cleanup();endDemo();vi.unstubAllGlobals();vi.useRealTimers()});
const fields={vehicle_id:1,customer:'Alex',email:'alex@example.com',phone:'',message:'Saturday viewing?',request_type:'Arrange a viewing',source:'Website',submission_key:'00000000-0000-0000-0000-000000000001'};

test('blocked browser storage leaves a failed persistent demo inactive',()=>{
 const blocked=vi.spyOn(Storage.prototype,'setItem').mockImplementation(()=>{throw new Error('blocked')});
 try{expect(()=>startDemo('dealer',seed,true)).toThrow('storage');expect(demoActive()).toBe(false)}finally{blocked.mockRestore()}
});

test('persistent demo survives end/resume, shares customer/staff messages, and remains off the server',async()=>{
 vi.stubGlobal('fetch',vi.fn());startDemo('customer',seed,true);
 const receipt=await request<{reference:number}>('/api/catalogue/enquiries','POST',fields);
 await request(`/api/customer/enquiries/${receipt.reference}/messages`,'POST',{body:'Is the morning possible?'});
 switchDemoRole('dealer');
 await request(`/api/enquiries/${receipt.reference}/messages`,'POST',{body:'We will confirm the viewing time.'});
 // Ending removes only active role; the saved dataset is deliberately retained.
 endDemo();expect(restoreDemo()).toBeNull();startDemo('customer',seed,true);
 expect(await request('/api/customer/enquiries')).toMatchObject({items:[{id:receipt.reference,status:'contacted'}]});
 expect(await request(`/api/customer/enquiries/${receipt.reference}/messages`)).toMatchObject({items:[{author_role:'customer'},{author_role:'staff'}]});
 // Simulate reload by restoring the active session from saved browser state.
 expect(restoreDemo()?.role).toBe('customer');
 expect(fetch).not.toHaveBeenCalled();
 clearSavedDemo();startDemo('dealer',seed,true);
 expect(await request('/api/enquiries')).toMatchObject({total:0});
});

test('expiry retains shared records but denies active operations until demo is resumed',async()=>{
 vi.useFakeTimers();startDemo('customer',seed,true);
 await request('/api/catalogue/enquiries','POST',fields);
 vi.advanceTimersByTime(31*60000);
 await expect(request('/api/customer/enquiries')).rejects.toThrow('expired');
 expect(restoreDemo()).toBeNull();endDemo();startDemo('dealer',seed,true);
 expect(await request('/api/enquiries')).toMatchObject({total:1});
});

test('receipt returns to car, offers browsing, and reopening does not create a new request',async()=>{
 startDemo('customer',seed);
 const snapshot={vehicles:[{...seed[0],archived:false,approved_facts:[],revision:1,created_at:'',updated_at:''}],enquiries:[],tasks:[]};
 render(<EnquiryDialog snapshot={snapshot} vehicleId={1}/>);
 fireEvent.click(screen.getByRole('button',{name:'Send an enquiry'}));
 fireEvent.change(screen.getByLabelText('Customer name'),{target:{value:'Alex'}});
 fireEvent.change(screen.getByLabelText('Email address'),{target:{value:'alex@example.com'}});
 fireEvent.change(screen.getByLabelText('Message'),{target:{value:'Viewing request'}});
 fireEvent.click(screen.getByRole('button',{name:'Submit website enquiry'}));
 expect(await screen.findByText('Enquiry #1 received')).toBeInTheDocument();
 expect(screen.queryByRole('button',{name:'Start another enquiry'})).not.toBeInTheDocument();
 expect(screen.getByRole('link',{name:'Recently viewed cars'})).toHaveAttribute('href','#/viewed');
 fireEvent.click(screen.getByRole('button',{name:'Back to vehicle'}));
 expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Send an enquiry'}));
 expect(screen.getByText('Enquiry #1 received')).toBeInTheDocument();
 expect(screen.queryByLabelText('Message')).not.toBeInTheDocument();
});

test('recently viewed storage waits for choice and revocation removes it',async()=>{
 render(<CookieChoices/>);rememberVehicle(1);
 expect(localStorage.getItem('dealer-desk-viewed-v1')).toBeNull();
 fireEvent.click(screen.getByRole('button',{name:'Remember viewed cars'}));rememberVehicle(2);
 expect(JSON.parse(localStorage.getItem('dealer-desk-viewed-v1')||'[]')).toContain(2);
 fireEvent(window,new Event('open-cookie-choices'));
 fireEvent.click(await screen.findByRole('button',{name:'Essential only'}));
 expect(localStorage.getItem('dealer-desk-viewed-v1')).toBeNull();
});

test('comparison refuses a fourth vehicle and verified stars link to the publisher',()=>{
 render(<>{[21,22,23,24].map(id=><CompareButton key={id} id={id}/>)}<ReviewStars make="Ford" model="Puma" year={2026}/><ReviewStars make="Unknown" model="Unknown" year={2026}/></>);
 const buttons=screen.getAllByRole('button',{name:/^Compare$/});
 buttons.forEach(button=>fireEvent.click(button));
 expect(screen.getAllByRole('button',{name:'Remove from comparison'})).toHaveLength(3);
 expect(screen.getByRole('status')).toHaveTextContent('Compare up to three');
 expect(screen.getByRole('link',{name:/Auto Express expert model-range review/})).toHaveAttribute('href','https://www.autoexpress.co.uk/ford/puma');
 expect(screen.getAllByRole('link')).toHaveLength(1);
});

test('policy pages describe the actual local handling without claiming delivered verification email',()=>{
 const {rerender}=render(<PolicyPage page="privacy"/>);
 expect(screen.getByRole('heading',{name:'Privacy'})).toBeInTheDocument();
 expect(screen.getByText(/do not prove ownership/)).toBeInTheDocument();
 rerender(<PolicyPage page="cookies"/>);expect(screen.getByRole('heading',{name:'Cookies and browser storage'})).toBeInTheDocument();
 rerender(<PolicyPage page="terms"/>);expect(screen.getByRole('heading',{name:'Terms of use'})).toBeInTheDocument();
});


test('hosted capability hides registration and recovery while retaining customer sign in',async()=>{
 const {default:Account}=await import('./CustomerAccount');
 window.location.hash='/account';
 vi.stubGlobal('fetch',vi.fn(async(input)=>({ok:String(input)==='/api/catalogue/capabilities',status:String(input)==='/api/catalogue/capabilities'?200:401,json:async()=>String(input)==='/api/catalogue/capabilities'?{enquiries:true,customer_registration:false}:{error:{message:'Sign in'}}})));
 render(<Account/>);
 expect(await screen.findByText(/New customer accounts and password recovery are not available yet/)).toBeInTheDocument();
 expect(screen.queryByRole('button',{name:'Register'})).not.toBeInTheDocument();
 expect(screen.queryByRole('button',{name:'Forgot password'})).not.toBeInTheDocument();
 expect(screen.getByRole('button',{name:'Sign in to my enquiries'})).toBeInTheDocument();
});
