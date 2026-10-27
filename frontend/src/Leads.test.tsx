import {afterEach,expect,test,vi} from 'vitest';
import {cleanup,render,screen,fireEvent} from '@testing-library/react';
import {DemoEnquiryForm} from './DemoEnquiries';
import {startDemo,endDemo,switchDemoRole} from './demo';
import {request,loadSnapshot} from './api';
import Leads from './Leads';
const seed=[{id:1,make:'Ford',model:'Puma',year:2026,price_pence:2714500,status:'available' as const}];
afterEach(()=>{cleanup();endDemo();vi.unstubAllGlobals()});
const fields={vehicle_id:1,customer:'Alex',email:'alex@example.com',phone:'',message:'Looking for a car',request_type:'Other',source:'Website'};

test('required contact fields and callback phone are separate from optional unticked promotions',async()=>{
 startDemo('customer',seed);
 render(<DemoEnquiryForm snapshot={await loadSnapshot()} website preferredVehicle={1} onSaved={async()=>{}}/>);
 expect(screen.getByLabelText('Customer name')).toBeRequired();
 expect(screen.getByLabelText('Email address')).toBeRequired();
 expect(screen.getByLabelText('Message')).toBeRequired();
 expect(screen.getByLabelText('Request type')).toBeRequired();
 const consent=screen.getByRole('checkbox',{name:/Email me Dealer Desk/});
 expect(consent).not.toBeChecked();expect(consent).not.toBeRequired();
 fireEvent.change(screen.getByLabelText('Request type'),{target:{value:'Request a callback'}});
 expect(screen.getByLabelText('Phone number')).toBeRequired();
});

test('saved demo leads track explicit opt-in and withdrawal without business fetches',async()=>{
 vi.stubGlobal('fetch',vi.fn());startDemo('customer',seed,true);
 await request('/api/catalogue/enquiries','POST',{...fields,promotions_opt_in:true});
 await expect(request('/api/leads')).rejects.toThrow('Staff');
 switchDemoRole('dealer');
 render(<Leads snapshot={await loadSnapshot()} canWrite onSaved={async()=>{}}/>);
 expect(await screen.findByText('Alex')).toBeInTheDocument();
 expect(screen.getByText('Email updates: opted in')).toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Record withdrawal of email consent'}));
 expect(await screen.findByText('Email updates: not subscribed')).toBeInTheDocument();
 expect(fetch).not.toHaveBeenCalled();
});
