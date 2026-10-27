import {afterEach,expect,test,vi} from 'vitest';
import {render,screen,fireEvent,cleanup,within} from '@testing-library/react';
import Enquiries from './DemoEnquiries';
import {startDemo,endDemo} from './demo';
import {request,loadSnapshot} from './api';
import {dealershipDate} from './workflow';

const seed=[{id:1,make:'Ford',model:'Puma',year:2026,price_pence:2714500,status:'available' as const}];
afterEach(()=>{cleanup();endDemo();vi.unstubAllGlobals()});
async function setup(){
 startDemo('dealer',seed);
 await request('/api/enquiries','POST',{vehicle_id:1,customer:'Alex',email:'alex@example.com',phone:'',message:'Can I view it?',source:'Website',request_type:'Arrange a viewing'});
 return loadSnapshot();
}

test('one action selector replaces simultaneous forms and history is collapsed',async()=>{
 render(<Enquiries snapshot={await setup()} onSaved={async()=>{}}/>);
 expect(screen.getByLabelText('Action for enquiry #1')).toHaveValue('');
 expect(screen.queryByLabelText('Reply message')).not.toBeInTheDocument();
 expect(screen.queryByLabelText('Contact outcome')).not.toBeInTheDocument();
 expect(screen.queryByLabelText('Closing outcome')).not.toBeInTheDocument();
 expect(screen.queryByRole('heading',{name:'Activity'})).not.toBeInTheDocument();
 fireEvent.change(screen.getByLabelText('Action for enquiry #1'),{target:{value:'email'}});
 expect(screen.getByLabelText('Reply message')).toBeInTheDocument();
 expect(screen.queryByLabelText('Contact outcome')).not.toBeInTheDocument();
 fireEvent.change(screen.getByLabelText('Action for enquiry #1'),{target:{value:'contact'}});
 expect(screen.getByLabelText('Contact outcome')).toBeInTheDocument();
 expect(screen.queryByLabelText('Reply message')).not.toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Cancel'}));
 expect(screen.getByLabelText('Action for enquiry #1')).toHaveValue('');
 fireEvent.click(screen.getByText('View conversation / history'));
 expect(await screen.findByRole('heading',{name:'Activity'})).toBeInTheDocument();
});

test('schedule action saves the suggested editable task then closes the form',async()=>{
 const saved=vi.fn().mockResolvedValue(undefined);
 render(<Enquiries snapshot={await setup()} onSaved={saved}/>);
 fireEvent.change(screen.getByLabelText('Action for enquiry #1'),{target:{value:'schedule'}});
 expect(screen.getByLabelText('Follow-up action')).toHaveValue('Agree a viewing date and confirm the appointment');
 fireEvent.change(screen.getByLabelText('Follow-up due date'),{target:{value:dealershipDate()}});
 fireEvent.click(screen.getByRole('button',{name:'Save follow-up'}));
 await vi.waitFor(()=>expect(saved).toHaveBeenCalledTimes(1));
 expect(await request('/api/tasks')).toMatchObject({total:1,items:[{enquiry_id:1,note:'Agree a viewing date and confirm the appointment'}]});
 expect(screen.getByLabelText('Action for enquiry #1')).toHaveValue('');
});

test('account reply offers one optional follow-up and saves both without showing email fields',async()=>{
 const snapshot=await setup();snapshot.enquiries[0].customer_linked=true;
 const saved=vi.fn().mockResolvedValue(undefined);
 render(<Enquiries snapshot={snapshot} onSaved={saved}/>);
 fireEvent.change(screen.getByLabelText('Action for enquiry #1'),{target:{value:'account'}});
 const form=within(screen.getByRole('region',{name:'Conversation for enquiry 1'}));
 expect(screen.queryByLabelText('Reply subject')).not.toBeInTheDocument();
 fireEvent.change(form.getByLabelText('Reply in customer account'),{target:{value:'We will confirm Saturday.'}});
 fireEvent.click(form.getByLabelText('Add follow-up'));
 fireEvent.change(form.getByLabelText('Follow-up due date'),{target:{value:dealershipDate()}});
 fireEvent.click(form.getByRole('button',{name:'Send message'}));
 await vi.waitFor(()=>expect(saved).toHaveBeenCalledTimes(1));
 expect(await request('/api/tasks')).toMatchObject({total:1});
 expect(await request('/api/enquiries/1/messages')).toMatchObject({items:[{body:'We will confirm Saturday.'}]});
});
