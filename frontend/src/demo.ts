import type {Snapshot,Vehicle,Photo} from './types';
export type DemoVehicleSeed=Pick<Vehicle,'id'|'make'|'model'|'year'|'price_pence'|'status'>&{photos?:Photo[]};
let pictures=new Map<number,Photo[]>();

export type DemoRole='customer'|'dealer';
let state:Snapshot|null=null;
let role:DemoRole='customer';
let expires=0;
let persistent=false;
let initialSeed:DemoVehicleSeed[]=[];
let messages:Record<string,{id:number;author_role:string;body:string;created_at:string}[]>={};
const SHARED='dealer-desk-demo-v2',ACTIVE='dealer-desk-demo-active-v2';
function savedDemo(){try{const raw=localStorage.getItem(SHARED);if(!raw||raw.length>2000000)return null;const value=JSON.parse(raw);if(value.version!==2||!Array.isArray(value.state?.vehicles)||!Array.isArray(value.state?.enquiries)||!Array.isArray(value.state?.tasks)||value.state.vehicles.length>100||value.state.enquiries.length>50||value.state.tasks.length>50||!Array.isArray(value.seed)||!Array.isArray(value.pictures))return null;return value}catch{return null}}
export function persistDemo(){if(!persistent||!state)return;try{const payload=JSON.stringify({version:2,state,pictures:[...pictures],seed:initialSeed,messages});if(payload.length>2000000)throw new Error('limit');localStorage.setItem(SHARED,payload);try{sessionStorage.setItem(ACTIVE,JSON.stringify({role,expires}));}catch{}}catch{throw new DemoError('Browser storage is full or unavailable. Clear the saved demo or enable storage.')}}
export function syncDemo(){if(!persistent)return;const saved=savedDemo();if(saved){state=saved.state;pictures=new Map(saved.pictures);messages=saved.messages||{};initialSeed=saved.seed;}}
export function restoreDemo():{role:DemoRole;expires:number;seed:DemoVehicleSeed[]}|null{try{const active=JSON.parse(sessionStorage.getItem(ACTIVE)||'null');if(!active||!['customer','dealer'].includes(active.role)||active.expires<=Date.now())return null;const saved=savedDemo();if(!saved)return null;persistent=true;role=active.role;expires=active.expires;syncDemo();return {role,expires,seed:initialSeed}}catch{return null}}
export function clearSavedDemo(){localStorage.removeItem(SHARED);sessionStorage.removeItem(ACTIVE);for(const key of Object.keys(sessionStorage))if(key.startsWith('dealer-receipt-demo-'))sessionStorage.removeItem(key);messages={};persistent=false;}

export class DemoError extends Error {}
export const enquirySources=['Website','Phone','Email','WhatsApp','SMS','Walk-in','Other'] as const;
export type DemoActivity={kind:string;at:string;actor:string;subject?:string;body?:string;outcome?:string};
export type PipelineEnquiry=import('./types').Enquiry;
export function switchDemoRole(next:DemoRole){
  if(!state||Date.now()>=expires)throw new DemoError('Start a new demo.');
  role=next;persistDemo();
}
function validatePlan(value:unknown):{note:string;due_date:string}|null{
  if(value==null)return null;
  const p=value as Record<string,unknown>;
  const parts=new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/London',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
  const part=(key:string)=>parts.find(p=>p.type===key)?.value;const today=`${part('year')}-${part('month')}-${part('day')}`;
  if(typeof p.note!=='string'||!p.note.trim()||p.note.length>300||typeof p.due_date!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(p.due_date)||Number.isNaN(Date.parse(p.due_date))||p.due_date<today)throw new DemoError('Enter an action and today or a future date.');
  if((state?.tasks.length||0)>=50)throw new DemoError('Demo limit reached.');
  return {note:p.note,due_date:p.due_date};
}
function addPlannedTask(enquiry_id:number,plan:{note:string;due_date:string}|null){
  if(!state||!plan)return;
  const stamp=new Date().toISOString();state.tasks.push({id:Math.max(0,...state.tasks.map(t=>t.id))+1,enquiry_id,...plan,completed:false,revision:1,created_at:stamp,updated_at:stamp});
}
export function demoActive(){return state!==null;}
export function endDemo(){state=null;expires=0;pictures.clear();persistent=false;messages={};try{sessionStorage.removeItem(ACTIVE);}catch{}}
export function startDemo(next:DemoRole,seed:DemoVehicleSeed[],save=false){
  persistent=save;initialSeed=structuredClone(seed);
  if(save&&savedDemo()){role=next;expires=Date.now()+30*60*1000;syncDemo();try{persistDemo()}catch(e){endDemo();throw e}return expires;}
  messages={};
  if(!seed.length)throw new DemoError('There are no public vehicles available for the demo. Please try again later.');
  role=next;expires=Date.now()+30*60*1000;
  const stamp=new Date().toISOString();
  pictures=new Map(seed.slice(0,100).map(car=>[car.id,structuredClone((car.photos||[]).filter(p=>p.illustrative))]));
  state={vehicles:seed.slice(0,100).map(car=>{
    const photos=pictures.get(car.id)||[],cover=photos.find(p=>p.is_cover)||photos[0];
    return {id:car.id,make:car.make,model:car.model,year:car.year,price_pence:car.price_pence,status:car.status,archived:false,approved_facts:['Reference vehicle. Price is illustrative.'],revision:1,created_at:stamp,updated_at:stamp,photo_count:photos.length,cover_photo_id:cover?.id||null,cover_photo:cover||null};
  }),enquiries:[],tasks:[]};
  try{persistDemo()}catch(e){endDemo();throw e}return expires;
}
// Only explicitly persistent demo snapshots use browser storage. Never access private dealership records.
export function demoRequest(path:string,method:string,data?:unknown):unknown {
  if(!state)throw new DemoError('Start a new demo.');
  syncDemo();
  if(Date.now()>=expires)throw new DemoError('Your demo has expired. End it and start a new demo.');
  if(path==='/api/customer/me'&&method==='GET'){
    if(role!=='customer')throw new DemoError('Switch to customer view.');const profile=state.enquiries.find(e=>e.source==='Website');return {name:profile?profile.customer+' (customer demo)':'Customer demo',email:profile?.email||'customer@example.com'};
  }
  if(path==='/api/customer/enquiries'&&method==='GET'){
    if(role!=='customer')throw new DemoError('Customer access required.');return {items:structuredClone(state.enquiries.filter(e=>e.source==='Website'))};
  }
  const conversation=/^\/api\/(customer\/)?enquiries\/(\d+)\/messages$/.exec(path);
  if(conversation){
    const customer=!!conversation[1];
    if((customer&&role!=='customer')||(!customer&&role!=='dealer'))throw new DemoError('Switch to the correct view.');
    const enquiry=state.enquiries.find(e=>e.id===Number(conversation[2]));
    if(!enquiry||(customer&&enquiry.source!=='Website'))throw new DemoError('Enquiry not found.');
    const thread=messages[String(enquiry.id)]||[];
    if(method==='POST'){
      const body=(data as {body?:unknown}).body;
      if(typeof body!=='string'||!body.trim()||body.length>2000)throw new DemoError('Enter a message of up to 2000 characters.');
      if(thread.length>=100)throw new DemoError('Conversation limit reached.');
      const plan=validatePlan((data as {follow_up?:unknown}).follow_up);
      if(customer&&plan)throw new DemoError('Only staff can schedule follow-ups.');
      addPlannedTask(enquiry.id,plan);
      thread.push({id:thread.length+1,author_role:customer?'customer':'staff',body:body.trim(),created_at:new Date().toISOString()});messages[String(enquiry.id)]=thread;
      enquiry.status=customer?'new':'contacted';enquiry.closure_reason='';enquiry.revision++;enquiry.updated_at=new Date().toISOString();
    }else if(method!=='GET')throw new DemoError('Operation unavailable.');
    return {items:structuredClone(thread)};
  }
  const publicSubmission=path==='/api/catalogue/enquiries';
  const pipelineCreate=publicSubmission||(path==='/api/enquiries'&&Object.prototype.hasOwnProperty.call(data||{},'source'));
  if(pipelineCreate&&method==='POST'){
    const f=data as Record<string,unknown>;
    const text=(key:string,max:number)=>{const v=f[key];if(typeof v!=='string'||v.length>max)throw new DemoError('Check the enquiry details.');return v.trim();};
    const customer=text('customer',80),message=text('message',1000),email=text('email',254),phone=text('phone',40);
    const source=publicSubmission||role==='customer'?'Website':text('source',20);
    const requestType=typeof f.request_type==='string'?f.request_type:'Other';
    if(!['Check availability','Arrange a viewing','Book a test drive','Vehicle details','Request a callback','Other'].includes(requestType))throw new DemoError('Choose a request type.');
    if(requestType==='Request a callback'&&!phone)throw new DemoError('Enter a phone number for a callback.');
    const plan=validatePlan(f.follow_up);
    if(publicSubmission&&plan)throw new DemoError('Only staff can schedule follow-ups.');
    if(!customer||!message||!enquirySources.includes(source as typeof enquirySources[number]))throw new DemoError('Enter a name, message and enquiry source.');
    if((role==='customer'||email)&&(!/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(email)||/[\r\n]/.test(email)))throw new DemoError('Enter a valid email address.');
    if(f.vehicle_id!==null&&!state.vehicles.some(v=>v.id===f.vehicle_id&&!v.archived))throw new DemoError('Choose an existing vehicle.');
    if(state.enquiries.length>=50)throw new DemoError('Demo limit reached. Reset the demo to continue.');
    const at=new Date().toISOString();
    const row:PipelineEnquiry={id:Math.max(0,...state.enquiries.map(e=>e.id))+1,vehicle_id:f.vehicle_id===null?null:Number(f.vehicle_id),customer,message,email,phone,source,request_type:requestType,customer_linked:publicSubmission,status:'new',revision:1,created_at:at,updated_at:at,activity:[{kind:'Enquiry received',at,actor:role==='customer'?'Customer website':'Staff demo'}]};
    state.enquiries.push(row);addPlannedTask(row.id,plan);return publicSubmission?{reference:row.id}:structuredClone(row);
  }
  const action=/^\/api\/enquiries\/(\d+)\/(reply|close|contact)$/.exec(path);
  if(action&&method==='POST'){
    if(role!=='dealer')throw new DemoError('Staff access required.');
    const row=state.enquiries.find(e=>e.id===Number(action[1])) as PipelineEnquiry|undefined;
    if(!row)throw new DemoError('Record not found.');
    const f=data as Record<string,unknown>;
    if(f.revision!==row.revision)throw new DemoError('Record changed. Refresh and try again.');
    if(row.status==='closed')throw new DemoError('This enquiry is closed.');
    if((row.activity?.length||0)>=100)throw new DemoError('Activity limit reached. Reset the demo.');
    const plan=validatePlan(f.follow_up);
    const at=new Date().toISOString();
    if(action[2]==='reply'){
      if(f.confirmed!==true||!row.email||typeof f.subject!=='string'||!f.subject.trim()||f.subject.length>160||/[\r\n]/.test(f.subject)||typeof f.body!=='string'||!f.body.trim()||f.body.length>2000)throw new DemoError('Enter a subject and reply, then confirm you sent the email.');
      row.activity=[...(row.activity||[]),{kind:'Email marked as sent',actor:'Staff demo',at,subject:f.subject,body:f.body}];row.status='contacted';
    }else if(action[2]==='contact'){
      if(typeof f.outcome!=='string'||!f.outcome.trim()||f.outcome.length>300)throw new DemoError('Record the contact outcome.');
      row.activity=[...(row.activity||[]),{kind:'Contact recorded',actor:'Staff demo',at,outcome:f.outcome}];row.status='contacted';
    }else{
      if(plan)throw new DemoError('A closed enquiry cannot have a new follow-up.');
      if(typeof f.outcome!=='string'||!f.outcome.trim()||f.outcome.length>300)throw new DemoError('Record the outcome before closing.');
      if(state.tasks.some(t=>t.enquiry_id===row.id&&!t.completed))throw new DemoError('Complete pending follow-ups before closing this enquiry.');
      row.closure_reason=f.outcome.trim();row.status='closed';row.activity=[...(row.activity||[]),{kind:'Enquiry closed',actor:'Staff demo',at,outcome:row.closure_reason}];
    }
    addPlannedTask(row.id,plan);row.revision++;row.updated_at=at;return structuredClone(row);
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
  if(collection==='enquiries'&&row.source)throw new DemoError('Use the reply or close actions for this enquiry.');
  if(fields.revision!==row.revision)throw new DemoError('Record changed. Refresh and try again.');
  delete fields.id;delete fields.created_at;
  Object.assign(row,fields,{revision:Number(row.revision)+1,updated_at:new Date().toISOString()});
  return structuredClone(row);
}
