import type {Snapshot,Task} from './types';
export function dealershipDate(){
 const parts=new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/London',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
 const get=(type:string)=>parts.find(p=>p.type===type)?.value;
 return `${get('year')}-${get('month')}-${get('day')}`;
}
export function taskTiming(task:Task,today=dealershipDate()){
 return task.due_date<today?'Overdue':task.due_date===today?'Due today':'Upcoming';
}
export function pendingTasks(snapshot:Snapshot,enquiryId:number){
 return snapshot.tasks.filter(t=>t.enquiry_id===enquiryId&&!t.completed).sort((a,b)=>a.due_date.localeCompare(b.due_date)||a.id-b.id);
}
export function attentionEnquiries(snapshot:Snapshot,today=dealershipDate()){
 const priority=(id:number)=>{const next=pendingTasks(snapshot,id)[0];return !next?1:next.due_date<today?0:next.due_date===today?2:3;};
 return snapshot.enquiries.filter(e=>e.status!=='closed').sort((a,b)=>priority(a.id)-priority(b.id)||a.id-b.id);
}
