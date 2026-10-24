import type {Snapshot} from './types';

export type DemoRole='customer'|'dealer';
let state:Snapshot|null=null;
let role:DemoRole='customer';
let expires=0;
export class DemoError extends Error {}
export function demoActive(){return state!==null;}
export function endDemo(){state=null;expires=0;}
export function startDemo(next:DemoRole){
  role=next;expires=Date.now()+30*60*1000;
  const stamp=new Date().toISOString();
  state={vehicles:[['Ford','Puma',2499500],['Nissan','Qashqai',2799500],['Volkswagen','Golf',2299500]].map(([make,model,price],i)=>({id:i+1,make:String(make),model:String(model),year:2024,price_pence:Number(price),status:'available',archived:false,approved_facts:['Fictional demonstration vehicle. Price is illustrative.'],revision:1,created_at:stamp,updated_at:stamp,photo_count:0})),enquiries:[],tasks:[]};
  return expires;
}
// Deliberately has no fetch, browser storage, cookies or access to dealership data.
export function demoRequest(path:string,method:string,data?:unknown):unknown {
  if(!state)throw new DemoError('Start a new demo.');
  if(Date.now()>=expires)throw new DemoError('Your demo has expired. End it and start a new demo.');
  const match=/^\/api\/(vehicles|enquiries|tasks)(?:\/(\d+))?(\/photos)?(?:\?.*)?$/.exec(path);
  if(!match)throw new DemoError('This operation is unavailable in the browser demo.');
  const collection=match[1] as keyof Snapshot,id=Number(match[2]);
  const rows=state[collection] as unknown as Record<string,unknown>[];
  if(match[3]){if(method==='GET')return [];throw new DemoError('Photo uploads require a staff account.');}
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
  if(fields.revision!==row.revision)throw new DemoError('Record changed. Refresh and try again.');
  delete fields.id;delete fields.created_at;
  Object.assign(row,fields,{revision:Number(row.revision)+1,updated_at:new Date().toISOString()});
  return structuredClone(row);
}
