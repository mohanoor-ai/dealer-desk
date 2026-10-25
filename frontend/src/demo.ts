import type {Snapshot,Vehicle,Photo} from './types';
export type DemoVehicleSeed=Pick<Vehicle,'id'|'make'|'model'|'year'|'price_pence'|'status'>&{photos?:Photo[]};
let pictures=new Map<number,Photo[]>();

export type DemoRole='customer'|'dealer';
let state:Snapshot|null=null;
let role:DemoRole='customer';
let expires=0;
export class DemoError extends Error {}
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
  if(fields.revision!==row.revision)throw new DemoError('Record changed. Refresh and try again.');
  delete fields.id;delete fields.created_at;
  Object.assign(row,fields,{revision:Number(row.revision)+1,updated_at:new Date().toISOString()});
  return structuredClone(row);
}
