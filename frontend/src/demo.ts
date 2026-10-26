import type {Snapshot,Vehicle,Photo} from './types';
export type DemoVehicleSeed=Pick<Vehicle,'id'|'make'|'model'|'year'|'price_pence'|'status'>&{photos?:Photo[]};
let pictures=new Map<number,Photo[]>();

export type DemoRole='customer'|'dealer';
let state:Snapshot|null=null;
let role:DemoRole='customer';
let expires=0;
export class DemoError extends Error {}
export const enquiryPrototypeEnabled=import.meta.env.VITE_ENQUIRY_DEMO==='true'&&['127.0.0.1','localhost'].includes(window.location.hostname);
export const enquirySources=['Website','Phone','Email','WhatsApp','SMS','Walk-in','Other'] as const;
export type DemoActivity={kind:string;at:string;actor:string;subject?:string;body?:string;outcome?:string};
export type PipelineEnquiry=import('./types').Enquiry&{source?:string;email?:string;phone?:string;activity?:DemoActivity[];closure_reason?:string};
export function switchDemoRole(next:DemoRole){
  if(!state||Date.now()>=expires)throw new DemoError('Start a new demo.');
  role=next;
}
export function demoActive(){return state!==null;}
export function endDemo(){state=null;expires=0;pictures.clear();}
export function startDemo(next:DemoRole,seed:DemoVehicleSeed[]){
  if(!seed.length)throw new DemoError('There are no public vehicles available for the demo. Please try again later.');
  role=next;expires=Date.now()+30*60*1000;
  const stamp=new Date().toISOString();
  pictures=new Map(seed.slice(0,100).map(car=>[car.id,structuredClone((car.photos||[]).filter(p=>p.illustrative))]));
  state={vehicles:seed.slice(0,100).map(car=>{
    const photos=pictures.get(car.id)||[],cover=photos.find(p=>p.is_cover)||photos[0];
    return {id:car.id,make:car.make,model:car.model,year:car.year,price_pence:car.price_pence,status:car.status,archived:false,approved_facts:['Reference vehicle. Price is illustrative.'],revision:1,created_at:stamp,updated_at:stamp,photo_count:photos.length,cover_photo_id:cover?.id||null,cover_photo:cover||null};
  }),enquiries:[],tasks:[]};
  return expires;
}
// Deliberately has no fetch, browser storage, cookies or access to private dealership records.
export function demoRequest(path:string,method:string,data?:unknown):unknown {
  if(!state)throw new DemoError('Start a new demo.');
  if(Date.now()>=expires)throw new DemoError('Your demo has expired. End it and start a new demo.');
  if(path==='/api/demo/enquiries'&&method==='POST'&&enquiryPrototypeEnabled){
    const f=data as Record<string,unknown>;
    const text=(key:string,max:number)=>{const v=f[key];if(typeof v!=='string'||v.length>max)throw new DemoError('Check the enquiry details.');return v.trim();};
    const customer=text('customer',80),message=text('message',1000),email=text('email',254),phone=text('phone',40);
    const source=role==='customer'?'Website':text('source',20);
    if(!customer||!message||!enquirySources.includes(source as typeof enquirySources[number]))throw new DemoError('Enter a name, message and enquiry source.');
    if((role==='customer'||email)&&(!/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(email)||/[\r\n]/.test(email)))throw new DemoError('Enter a valid email address.');
    if(!state.vehicles.some(v=>v.id===f.vehicle_id&&!v.archived))throw new DemoError('Choose an existing vehicle.');
    if(state.enquiries.length>=50)throw new DemoError('Demo limit reached. Reset the demo to continue.');
    const at=new Date().toISOString();
    const row:PipelineEnquiry={id:Math.max(0,...state.enquiries.map(e=>e.id))+1,vehicle_id:Number(f.vehicle_id),customer,message,email,phone,source,status:'new',revision:1,created_at:at,updated_at:at,activity:[{kind:'Enquiry received',at,actor:role==='customer'?'Customer website':'Staff demo'}]};
    state.enquiries.push(row);return structuredClone(row);
  }
  const action=/^\/api\/demo\/enquiries\/(\d+)\/(reply|close)$/.exec(path);
  if(action&&method==='POST'&&enquiryPrototypeEnabled){
    if(role!=='dealer')throw new DemoError('Staff access required.');
    const row=state.enquiries.find(e=>e.id===Number(action[1])) as PipelineEnquiry|undefined;
    if(!row)throw new DemoError('Record not found.');
    const f=data as Record<string,unknown>;
    if(f.revision!==row.revision)throw new DemoError('Record changed. Refresh and try again.');
    if(row.status==='closed')throw new DemoError('This enquiry is closed.');
    if((row.activity?.length||0)>=100)throw new DemoError('Activity limit reached. Reset the demo.');
    const at=new Date().toISOString();
    if(action[2]==='reply'){
      if(f.confirmed!==true||!row.email||typeof f.subject!=='string'||!f.subject.trim()||f.subject.length>160||/[\r\n]/.test(f.subject)||typeof f.body!=='string'||!f.body.trim()||f.body.length>2000)throw new DemoError('Enter a subject and reply, then confirm you sent the email.');
      row.activity=[...(row.activity||[]),{kind:'Email marked as sent',actor:'Staff demo',at,subject:f.subject,body:f.body}];row.status='contacted';
    }else{
      if(typeof f.outcome!=='string'||!f.outcome.trim()||f.outcome.length>300)throw new DemoError('Record the outcome before closing.');
      if(state.tasks.some(t=>t.enquiry_id===row.id&&!t.completed))throw new DemoError('Complete pending follow-ups before closing this enquiry.');
      row.closure_reason=f.outcome.trim();row.status='closed';row.activity=[...(row.activity||[]),{kind:'Enquiry closed',actor:'Staff demo',at,outcome:row.closure_reason}];
    }
    row.revision++;row.updated_at=at;return structuredClone(row);
  }
  const match=/^\/api\/(vehicles|enquiries|tasks)(?:\/(\d+))?(\/photos)?(?:\?.*)?$/.exec(path);
  if(!match)throw new DemoError('This operation is unavailable in the browser demo.');
  const collection=match[1] as keyof Snapshot,id=Number(match[2]);
  const rows=state[collection] as unknown as Record<string,unknown>[];
  if(match[3]){if(method==='GET')return structuredClone(pictures.get(id)||[]);throw new DemoError('Photo uploads require a staff account.');}
  const row=rows.find(item=>item.id===id);
  if(method==='GET'){
    if(id){if(!row)throw new DemoError('Record not found.');return structuredClone(row);}
    const query=new URLSearchParams(path.split('?')[1]);
    const offset=Math.max(0,Number(query.get('offset'))||0),limit=Math.min(100,Math.max(1,Number(query.get('limit'))||100));
    return structuredClone({items:rows.slice(offset,offset+limit),total:rows.length,offset,limit});
  }
  if(role==='customer'&&(collection!=='enquiries'||method!=='POST'))throw new DemoError('Customers can send enquiries only.');
  const fields={...(data as Record<string,unknown>)};
  if(JSON.stringify(fields).length>4000)throw new DemoError('Please use shorter demo details.');
  if(method==='POST'){
    if(rows.length>=50)throw new DemoError('Demo limit reached. Reset the demo to continue.');
    if(collection==='enquiries'&&!state.vehicles.some(v=>v.id===fields.vehicle_id))throw new DemoError('Choose an existing vehicle.');
    if(collection==='tasks'&&!state.enquiries.some(e=>e.id===fields.enquiry_id))throw new DemoError('Choose an existing enquiry.');
    const stamp=new Date().toISOString();
    const defaults=collection==='vehicles'?{status:'available',archived:false,approved_facts:[],photo_count:0}:collection==='enquiries'?{status:'new'}:{completed:false};
    const created={...defaults,...fields,id:Math.max(0,...rows.map(item=>Number(item.id)))+1,revision:1,created_at:stamp,updated_at:stamp};
    rows.push(created);return structuredClone(created);
  }
  if(method!=='PATCH'||!row)throw new DemoError('Record not found.');
  if(enquiryPrototypeEnabled&&collection==='enquiries'&&row.source)throw new DemoError('Use the reply or close actions for this enquiry.');
  if(fields.revision!==row.revision)throw new DemoError('Record changed. Refresh and try again.');
  delete fields.id;delete fields.created_at;
  Object.assign(row,fields,{revision:Number(row.revision)+1,updated_at:new Date().toISOString()});
  return structuredClone(row);
}
