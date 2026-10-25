import type {Vehicle, Enquiry, Task, Snapshot, Page} from './types';
import {demoActive,demoRequest} from './demo';
export class ApiError extends Error {
  constructor(public status:number, message:string) {super(message);}
}
// This is the only place that calls fetch. Do not automatically retry writes.
export async function request<T>(path:string, method='GET', data?:unknown):Promise<T> {
  if(demoActive())return demoRequest(path,method,data) as T;
  const controller = new AbortController();
  const timeout=setTimeout(()=>controller.abort(),10000);
  try {
    const response=await fetch(path,{method,credentials:'same-origin',signal:controller.signal,headers:{'Content-Type':'application/json','X-Requested-With':'DealerDesk'},body:data===undefined?undefined:JSON.stringify(data)});
    const result=response.status===204?undefined:await response.json();
    if(!response.ok) throw new ApiError(response.status,result.error?.message || `Request failed (${response.status})`);
    return result;
  }catch(error){
    if(error instanceof DOMException && error.name==='AbortError')throw new Error('The request timed out. Refresh records before trying to save again.');
    throw error;
  }finally{clearTimeout(timeout);}
}
async function allPages<T>(path:string):Promise<T[]> {
  const result:T[]=[];
  let offset=0;
  while(true){const page=await request<Page<T>>(`${path}?offset=${offset}&limit=100`);result.push(...page.items);offset+=page.items.length;if(offset>=page.total || page.items.length===0)return result;}
}
export async function loadSnapshot():Promise<Snapshot> {
  const [vehicles,enquiries,tasks]=await Promise.all([allPages<Vehicle>('/api/vehicles'),allPages<Enquiry>('/api/enquiries'),allPages<Task>('/api/tasks')]);
  return {vehicles,enquiries,tasks};
}
export function poundsToPence(value:string):number {
  if(!/^\d+(\.\d{1,2})?$/.test(value))throw Error('Use pounds with up to two decimal places.');
  const [whole,decimal='']=value.split('.');const pence=Number(whole)*100+Number(decimal.padEnd(2,'0'));
  if(!Number.isSafeInteger(pence)||pence>100000000)throw Error('Price is too large.');return pence;
}
export function money(value:number){return new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP'}).format(value/100);}

export function photoUrl(id:number, thumbnail=false) {
  return `/api/photos/${id}/image${thumbnail?'?thumbnail=true':''}`;
}

export function readPhoto(file:File):Promise<string> {
  if(file.size>2*1024*1024)return Promise.reject(new Error(`${file.name}: choose an image of 2 MB or smaller.`));
  if(!['image/jpeg','image/png','image/webp'].includes(file.type))return Promise.reject(new Error(`${file.name}: use JPEG, PNG or WebP.`));
  return new Promise((resolve,reject)=>{
    const reader=new FileReader();
    reader.onload=()=>resolve(String(reader.result));
    reader.onerror=()=>reject(new Error(`Could not read ${file.name}.`));
    reader.readAsDataURL(file);
  });
}

// Keep the internal showcase marker out of staff-facing form values.
export function modelForSave(value:string,original?:string){
  const clean=value.trim().replace(/\s*\(sample\)$/i,'').trim();
  if(!clean)throw new Error('Enter a model name.');
  return original?.endsWith(' (sample)')?`${clean} (sample)`:value.trim();
}
