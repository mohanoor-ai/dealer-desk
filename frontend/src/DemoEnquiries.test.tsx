import {afterEach,expect,test,vi} from 'vitest';
import {render,screen,fireEvent,cleanup,within} from '@testing-library/react';
const {startDemo,endDemo,switchDemoRole}=await import('./demo');
const {request}=await import('./api');
const {default:DemoEnquiries,DemoEnquiryForm,emailDraftUrl}=await import('./DemoEnquiries');
const {default:App}=await import('./App');
const seed=[{id:1,make:'Ford',model:'Puma',year:2026,price_pence:2714500,status:'available' as const}];
afterEach(()=>{cleanup();endDemo();vi.unstubAllGlobals();});
const input={vehicle_id:1,source:'Phone',customer:'Alex Morgan',email:'alex@example.com',phone:'',message:'Can I view the Puma on Saturday?'};

test('website source is automatic, role switching preserves records and no business writes reach server',async()=>{
 vi.stubGlobal('fetch',vi.fn());startDemo('customer',seed);
 const e=await request<any>('/api/enquiries','POST',input);
 expect(e).toMatchObject({source:'Website',status:'new',email:'alex@example.com'});
 await expect(request(`/api/enquiries/${e.id}/reply`,'POST',{revision:1,subject:'Viewing',body:'Let me check',confirmed:true})).rejects.toThrow('Staff');
 switchDemoRole('dealer');
 await expect(request(`/api/enquiries/${e.id}/reply`,'POST',{revision:1,subject:'Viewing',body:'Let me check',confirmed:false})).rejects.toThrow('confirm');
 const draft=emailDraftUrl(e.email,'Viewing & availability','Hello Alex,\nI will check Saturday.');
 expect(draft).toContain('subject=Viewing%20%26%20availability');expect(draft).toContain('%0A');
 expect(await request(`/api/enquiries/${e.id}`)).toMatchObject({status:'new',revision:1});
 const contacted=await request<any>(`/api/enquiries/${e.id}/reply`,'POST',{revision:1,subject:'Viewing',body:'I will check Saturday.',confirmed:true});
 expect(contacted.status).toBe('contacted');expect(contacted.activity[1]).toMatchObject({kind:'Email marked as sent',actor:'Staff demo',body:'I will check Saturday.'});
 const task=await request<any>('/api/tasks','POST',{enquiry_id:e.id,due_date:'2026-10-30',note:'Confirm Saturday viewing'});
 await expect(request(`/api/enquiries/${e.id}/close`,'POST',{revision:2,outcome:'Viewing confirmed'})).rejects.toThrow('pending follow-ups');
 await request(`/api/tasks/${task.id}`,'PATCH',{revision:1,completed:true});
 const closed=await request<any>(`/api/enquiries/${e.id}/close`,'POST',{revision:2,outcome:'Viewing confirmed; no further action'});
 expect(closed).toMatchObject({status:'closed',closure_reason:'Viewing confirmed; no further action'});
 expect(fetch).not.toHaveBeenCalled();startDemo('dealer',seed);expect(await request('/api/enquiries')).toMatchObject({total:0});
});

test('invalid contact/source, empty fields, stale replies and header injection are rejected',async()=>{
 startDemo('dealer',seed);
 for(const fields of [{source:''},{source:'Unknown'},{customer:' '},{message:' '},{email:'bad'},{email:'a@example.com\r\nBcc:b@example.com'},{vehicle_id:999}]){
   await expect(request('/api/enquiries','POST',{...input,...fields})).rejects.toThrow();
 }
 const e=await request<any>('/api/enquiries','POST',input);expect(e.source).toBe('Phone');
 await expect(request(`/api/enquiries/${e.id}/reply`,'POST',{revision:99,confirmed:true,subject:'Hello',body:'Reply'})).rejects.toThrow('changed');
 expect(emailDraftUrl('a@example.com?bcc=b@example.com','Hello','Reply')).toBe('');
 expect(emailDraftUrl('a@example.com','Hello\r\nBcc: b@example.com','Reply')).toBe('');
 await expect(request(`/api/enquiries/${e.id}`,'PATCH',{revision:1,status:'closed'})).rejects.toThrow('reply or close');
});

test('manual form exposes source selection and website form fixes source',()=>{
 startDemo('dealer',seed);
 const snapshot={vehicles:[],enquiries:[],tasks:[]};
 const {unmount}=render(<DemoEnquiryForm snapshot={snapshot} onSaved={async()=>{}}/>);
 expect(screen.getByLabelText('Enquiry source')).toBeRequired();unmount();
 render(<DemoEnquiryForm snapshot={snapshot} website onSaved={async()=>{}}/>);
 expect(screen.queryByLabelText('Enquiry source')).not.toBeInTheDocument();expect(screen.getByLabelText('Email address')).toBeRequired();
});

test('customer to staff UI keeps enquiry, and email opening alone leaves it New',async()=>{
 window.location.hash='/login';
 vi.stubGlobal('fetch',vi.fn(async(input)=>({ok:String(input)==='/api/catalogue',status:String(input)==='/api/catalogue'?200:401,json:async()=>String(input)==='/api/catalogue'?{items:seed}:{error:{message:'Please sign in.'}}})));
 render(<App/>);fireEvent.click(await screen.findByRole('button',{name:'Try staff demo'}));
 fireEvent.click(await screen.findByRole('button',{name:'Switch to customer website view'}));
 fireEvent.click(await screen.findByRole('link',{name:'View Ford Puma'}));
 fireEvent.click(await screen.findByRole('button',{name:'Send an enquiry'}));
 fireEvent.change(await screen.findByLabelText('Customer name'),{target:{value:input.customer}});
 fireEvent.change(screen.getByLabelText('Email address'),{target:{value:input.email}});
 fireEvent.change(screen.getByLabelText('Message'),{target:{value:input.message}});
 fireEvent.click(screen.getByRole('button',{name:'Submit website enquiry'}));
 expect(await screen.findByText(/Enquiry #1 received/)).toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Close enquiry form'}));
 fireEvent.click(screen.getByRole('button',{name:'Switch to staff view'}));
 expect(await screen.findByRole('heading',{name:'Dealership overview'})).toBeInTheDocument();
 fireEvent.click(screen.getByRole('link',{name:'Enquiries'}));
 expect(await screen.findByText(/Source: Website/)).toBeInTheDocument();
 const response=within(screen.getByRole('region',{name:'Response for enquiry 1'}));
 fireEvent.change(response.getByLabelText('Action for enquiry #1'),{target:{value:'email'}});
 fireEvent.change(response.getByLabelText('Reply message'),{target:{value:'I will check the viewing time.'}});
 const mailLink=response.getByRole('link',{name:'Open in email app'});
 // Prevent the external handler in the test; retain the real React click behaviour.
 mailLink.addEventListener('click',event=>event.preventDefault());fireEvent.click(mailLink);
 expect(await request('/api/enquiries/1')).toMatchObject({status:'new'});
 fireEvent.click(response.getByLabelText('I sent this email'));fireEvent.click(response.getByRole('button',{name:'Record sent email'}));
 fireEvent.click(screen.getByText('View conversation / history'));
 expect(await screen.findByText('Email marked as sent')).toBeInTheDocument();
 expect(await request('/api/enquiries/1')).toMatchObject({status:'contacted'});
 expect(vi.mocked(fetch).mock.calls.every(([url])=>String(url).includes('/auth/me')||String(url)==='/api/catalogue')).toBe(true);
});

test('vehicle popup starts closed, fixes the car, and exposes change/general only explicitly',async()=>{
 const {EnquiryDialog}=await import('./DemoEnquiries');
 const snapshot={vehicles:[{...seed[0],archived:false,approved_facts:[],revision:1,created_at:'',updated_at:''}],enquiries:[],tasks:[]};
 render(<EnquiryDialog snapshot={snapshot} vehicleId={1}/>);
 expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
 expect(screen.queryByLabelText('Message')).not.toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Send an enquiry'}));
 expect(await screen.findByRole('dialog')).toBeInTheDocument();
 expect(screen.queryByLabelText('Vehicle',{exact:true})).not.toBeInTheDocument();
 fireEvent.change(screen.getByLabelText('Request type'),{target:{value:'Request a callback'}});
 expect(screen.getByLabelText('Phone number')).toBeRequired();
 fireEvent.click(screen.getByLabelText('Enquire about a different vehicle or make a general enquiry'));
 fireEvent.change(screen.getByLabelText('Vehicle',{exact:true}),{target:{value:''}});
 expect(screen.getByLabelText('Vehicle',{exact:true})).toHaveValue('');
 fireEvent.click(screen.getByRole('button',{name:'Close enquiry form'}));
 expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
 expect(screen.getByRole('button',{name:'Send an enquiry'})).toHaveFocus();
});

test('normal staff enquiry uses saved API with source and optional next action in one request',async()=>{
 const {dealershipDate}=await import('./workflow');
 vi.stubGlobal('fetch',vi.fn(async()=>({ok:true,status:201,json:async()=>({id:7})})));
 render(<DemoEnquiryForm snapshot={{vehicles:[],enquiries:[],tasks:[]}} onSaved={async()=>{}}/>);
 fireEvent.change(screen.getByLabelText('Enquiry source'),{target:{value:'Phone'}});
 fireEvent.change(screen.getByLabelText('Customer name'),{target:{value:'Alex'}});
 fireEvent.change(screen.getByLabelText('Message'),{target:{value:'Please call tomorrow'}});
 fireEvent.change(screen.getByLabelText('Request type'),{target:{value:'Request a callback'}});
 fireEvent.change(screen.getByLabelText('Phone number'),{target:{value:'020 0000 0000'}});
 expect(screen.queryByLabelText('Follow-up due date')).not.toBeInTheDocument();
 fireEvent.click(screen.getByLabelText('Add follow-up'));
 expect(screen.getByLabelText('Follow-up action')).toHaveValue('Call the customer using the supplied number');
 fireEvent.change(screen.getByLabelText('Follow-up due date'),{target:{value:dealershipDate()}});
 fireEvent.click(screen.getByRole('button',{name:'Save enquiry'}));
 expect(await screen.findByText('Enquiry #7 received')).toBeInTheDocument();
 expect(fetch).toHaveBeenCalledTimes(1);
 const args=vi.mocked(fetch).mock.calls[0];
 expect(args[0]).toBe('/api/enquiries');
 expect(JSON.parse(String(args[1]?.body))).toMatchObject({source:'Phone',vehicle_id:null,request_type:'Request a callback',follow_up:{due_date:dealershipDate(),note:'Call the customer using the supplied number'}});
});

test('viewer sees request/activity without response or recording controls',()=>{
 render(<DemoEnquiries snapshot={{vehicles:[],tasks:[],enquiries:[{id:1,vehicle_id:null,customer:'Alex',message:'Hello',status:'new',revision:1,created_at:'',updated_at:'',source:'Website',request_type:'Other'}]}} canWrite={false} onSaved={async()=>{}}/>);
 expect(screen.getByText('General enquiry')).toBeInTheDocument();
 expect(screen.queryByRole('button',{name:'Close enquiry'})).not.toBeInTheDocument();
 expect(screen.queryByRole('heading',{name:'Record enquiry'})).not.toBeInTheDocument();
 expect(screen.queryByLabelText('Reply message')).not.toBeInTheDocument();
});
