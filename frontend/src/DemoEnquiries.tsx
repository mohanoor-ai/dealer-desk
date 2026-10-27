import {useState,useEffect,useRef} from 'react';
import type {FormEvent} from 'react';
import type {Snapshot} from './types';
import {request} from './api';
import {Conversation} from './CustomerAccount';
import {demoActive,enquirySources,type PipelineEnquiry} from './demo';
import {vehicleName} from './navigation';
import {requestTypes,suggestions} from './enquiryWorkflow';
import {dealershipDate} from './workflow';

export function emailDraftUrl(email:string,subject:string,body:string){
  if(!/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(email)||/[\r\n]/.test(email+subject))return '';
  return `mailto:${encodeURIComponent(email)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}

export function FollowUpFields({suggestion}:{suggestion:string}){
  const [checked,setChecked]=useState(false);
  return <fieldset className="follow-up-fields"><label className="check-label"><input name="schedule_follow_up" type="checkbox" checked={checked} onChange={e=>setChecked(e.target.checked)}/> Schedule a follow-up</label>{checked&&<><label>Follow-up action<textarea key={suggestion} name="follow_up_note" required maxLength={300} defaultValue={suggestion}/></label><label>Follow-up due date<input name="follow_up_date" type="date" min={dealershipDate()} required/></label></>}</fieldset>;
}
function followUpFrom(form:FormData){return form.get('schedule_follow_up')?{note:String(form.get('follow_up_note')),due_date:String(form.get('follow_up_date'))}:null;}

export function DemoEnquiryForm({snapshot,website=false,preferredVehicle=0,onSaved,onReturn}:{snapshot:Snapshot;website?:boolean;preferredVehicle?:number;onSaved:()=>Promise<void>;onReturn?:()=>void}){
  const receiptKey=`dealer-receipt-${demoActive()?'demo':'saved'}-${preferredVehicle}`;
  const [busy,setBusy]=useState(false),[error,setError]=useState(''),[receipt,setReceipt]=useState(()=>{if(!website)return 0;try{return Number(sessionStorage.getItem(receiptKey))||0}catch{return 0}});
  const [different,setDifferent]=useState(false),[category,setCategory]=useState<string>('Check availability');
  const submissionKey=useRef(crypto.randomUUID());
  const selected=snapshot.vehicles.find(v=>v.id===preferredVehicle);
  async function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault();if(busy||receipt)return;const form=event.currentTarget,data=new FormData(form);setBusy(true);setError('');
    try{
      const value=data.get('vehicle_id');
      const fields={vehicle_id:value?Number(value):null,customer:String(data.get('customer')),email:String(data.get('email')),phone:String(data.get('phone')),request_type:category,message:String(data.get('message')),source:website?'Website':String(data.get('source'))};
      const row=await request<{id?:number;reference?:number}>(website?'/api/catalogue/enquiries':'/api/enquiries','POST',website?{...fields,submission_key:submissionKey.current}:{...fields,follow_up:followUpFrom(data)});
      const ref=row.reference||row.id||0;setReceipt(ref);if(website){try{sessionStorage.setItem(receiptKey,String(ref))}catch{}}await onSaved();
    }catch(e){setError(e instanceof Error?e.message:'Could not save the enquiry.');}finally{setBusy(false);}
  }
  if(receipt)return <div role="status"><h3>Enquiry #{receipt} received</h3><p>{website?(demoActive()?'Your request is saved in the shared demo staff queue.':'Your request has been saved for the dealership to review.'):'The enquiry and any selected follow-up have been saved.'}</p>{website?<><button type="button" onClick={onReturn}>Back to vehicle</button><p><a href="#/account" onClick={onReturn}>View or follow up this enquiry</a></p><p><a href="#/viewed" onClick={onReturn}>Recently viewed cars</a> · <a href="#/catalogue" onClick={onReturn}>Browse more vehicles</a></p></>:<button type="button" className="secondary" onClick={()=>{setReceipt(0);submissionKey.current=crypto.randomUUID();}}>Record another conversation</button>}</div>;

  return <form onSubmit={submit} className="pipeline-form">
    {demoActive()&&<p>Saved demo. Use test contact details; records stay on this browser until reset.</p>}
    {error&&<p role="alert">{error}</p>}
    {website&&selected&&!different?<><p>Vehicle: <strong>{vehicleName(selected.make,selected.model)}</strong></p><input name="vehicle_id" type="hidden" value={selected.id}/></>:<label>Vehicle<select name="vehicle_id" defaultValue={preferredVehicle||''}><option value="">General enquiry</option>{snapshot.vehicles.map(v=><option key={v.id} value={v.id}>{vehicleName(v.make,v.model)}</option>)}</select></label>}
    {website&&selected&&<label className="check-label"><input type="checkbox" checked={different} onChange={e=>setDifferent(e.target.checked)}/> Enquire about a different vehicle or make a general enquiry</label>}
    {website?<p>Enquiry source: <strong>Website</strong></p>:<label>Enquiry source<select name="source" required defaultValue=""><option value="" disabled>Select source</option>{enquirySources.map(source=><option key={source}>{source}</option>)}</select></label>}
    <label>Request type<select name="request_type" value={category} onChange={e=>setCategory(e.target.value)}>{requestTypes.map(type=><option key={type}>{type}</option>)}</select></label>
    <label>Customer name<input name="customer" required maxLength={80}/></label>
    <label>Email address<input name="email" type="email" required={website} maxLength={254} placeholder="alex@example.com"/></label>
    <label>Phone number<input name="phone" type="tel" required={category==='Request a callback'} maxLength={40}/></label>
    <label>Message<textarea name="message" required maxLength={1000}/></label>
    {!website&&<FollowUpFields suggestion={suggestions[category]}/>}
    <button disabled={busy}>{busy?'Saving…':website?'Submit website enquiry':'Save enquiry'}</button>
  </form>;
}

export function EnquiryDialog({snapshot,vehicleId,onSaved=async()=>{}}:{snapshot:Snapshot;vehicleId:number;onSaved?:()=>Promise<void>}){
  const [open,setOpen]=useState(false);const dialog=useRef<HTMLDialogElement>(null),trigger=useRef<HTMLButtonElement>(null);
  useEffect(()=>{if(open){if(dialog.current?.showModal)dialog.current.showModal();else dialog.current?.setAttribute('open','');}},[open]);
  function close(){setOpen(false);trigger.current?.focus();}
  useEffect(()=>{setOpen(false)},[vehicleId]);
  return <><button ref={trigger} onClick={()=>setOpen(true)}>Send an enquiry</button>{open&&<dialog ref={dialog} className="upload-dialog enquiry-dialog" aria-labelledby="enquiry-popup-title" onCancel={close} onClose={close}><div className="section-heading"><h2 id="enquiry-popup-title">Send an enquiry</h2><button type="button" className="icon-button" aria-label="Close enquiry form" onClick={close}>×</button></div><DemoEnquiryForm snapshot={snapshot} website preferredVehicle={vehicleId} onSaved={onSaved} onReturn={close}/></dialog>}</>;
}

function ResponseActions({enquiry,onSaved,canWrite=true}:{enquiry:PipelineEnquiry;onSaved:()=>Promise<void>;canWrite?:boolean}){
  const [subject,setSubject]=useState(`Your vehicle enquiry #${enquiry.id}`),[body,setBody]=useState('');
  const [confirmed,setConfirmed]=useState(false),[opened,setOpened]=useState(false),[outcome,setOutcome]=useState(''),[contactOutcome,setContactOutcome]=useState('');
  const [busy,setBusy]=useState(false),[error,setError]=useState('');
  const draft=emailDraftUrl(enquiry.email||'',subject,body);
  async function save(action:'reply'|'close'|'contact',plan:ReturnType<typeof followUpFrom>=null){
    if(busy)return;setBusy(true);setError('');
    try{
      await request(`/api/enquiries/${enquiry.id}/${action}`,'POST',{revision:enquiry.revision,follow_up:plan,...(action==='reply'?{subject,body,confirmed}:{outcome:action==='contact'?contactOutcome:outcome})});
      await onSaved();setConfirmed(false);setOpened(false);setBody('');setOutcome('');setContactOutcome('');
    }catch(e){setError(e instanceof Error?e.message:'Could not record the action.');}finally{setBusy(false);}
  }
  return <section aria-label={`Response for enquiry ${enquiry.id}`}>
    {error&&<p role="alert">{error}</p>}
    {canWrite&&enquiry.status!=='closed'&&<>
      <h4>Reply by email</h4>
      {enquiry.email?<><p>To: {enquiry.email}</p>
        <label>Reply subject<input value={subject} maxLength={160} onChange={e=>{setSubject(e.target.value);setOpened(false);setConfirmed(false);}}/></label>
        <label>Reply message<textarea value={body} maxLength={2000} onChange={e=>{setBody(e.target.value);setOpened(false);setConfirmed(false);}}/></label>
        {draft&&subject.trim()&&body.trim()?<a className="button-link secondary" href={draft} onClick={()=>setOpened(true)}>Open in email app</a>:<p>Enter a subject and reply to open your email app.</p>}
        <p>The app cannot verify sending or delivery. Opening your email app does not change the enquiry.</p>
        <label><input type="checkbox" checked={confirmed} disabled={!opened||busy} onChange={e=>setConfirmed(e.target.checked)}/> I sent this email</label>
        <form onSubmit={e=>{e.preventDefault();save('reply',followUpFrom(new FormData(e.currentTarget)));}}><FollowUpFields suggestion={suggestions[enquiry.request_type||'Other']||suggestions.Other}/><button disabled={!opened||!confirmed||busy}>Record sent email</button></form>
      </>:<p>No email address recorded. Contact the customer using the supplied details, then record the outcome.</p>}
      <p><a className="button-link secondary" href={`#/follow-ups?enquiry=${enquiry.id}`}>Schedule follow-up</a></p><form onSubmit={e=>{e.preventDefault();save('contact',followUpFrom(new FormData(e.currentTarget)));}}><label>Contact outcome<textarea value={contactOutcome} required maxLength={300} onChange={e=>setContactOutcome(e.target.value)} placeholder="Record a call or conversation"/></label><FollowUpFields suggestion={suggestions[enquiry.request_type||'Other']||suggestions.Other}/><button disabled={busy||!contactOutcome.trim()}>Record contact</button></form>
      <label>Closing outcome<textarea maxLength={300} value={outcome} onChange={e=>setOutcome(e.target.value)} placeholder="What happened and why is no further action needed?"/></label>
      <button className="secondary" disabled={!outcome.trim()||busy} onClick={()=>save('close')}>Close enquiry</button>
    </>}
    <h4>Activity</h4>
    <ol>{(enquiry.activity||[]).map((event,i)=><li key={i}><strong>{event.kind}</strong> · {event.actor} · <time dateTime={event.at}>{new Date(event.at).toLocaleString('en-GB')}</time>{event.subject&&<p>{event.subject}</p>}{event.body&&<p style={{whiteSpace:'pre-wrap'}}>{event.body}</p>}{event.outcome&&<p>{event.outcome}</p>}</li>)}</ol>
  </section>;
}

export default function DemoEnquiries({snapshot,selectedEnquiry=0,onSaved,canWrite=true,initialFilter='all',preferredVehicle=0}:{snapshot:Snapshot;selectedEnquiry?:number;onSaved:()=>Promise<void>;canWrite?:boolean;initialFilter?:string;preferredVehicle?:number}){
  const [source,setSource]=useState('All sources'),[status,setStatus]=useState(initialFilter);
  useEffect(()=>setStatus(initialFilter),[initialFilter,selectedEnquiry]);
  const records=(snapshot.enquiries as PipelineEnquiry[]).filter(e=>(!selectedEnquiry||e.id===selectedEnquiry)&&(source==='All sources'||source===e.source)&&(status!=='open'||e.status!=='closed'));
  return <><h1>Enquiries</h1><p>Review the request, record your response and choose the next action.</p>
    {selectedEnquiry>0&&<p><a href="#/enquiries">View all enquiries</a></p>}
    <div className="work-grid"><section className="panel"><h2>Staff queue</h2><label>Enquiry status<select value={status} onChange={e=>setStatus(e.target.value)}><option value="all">All enquiries</option><option value="open">Open enquiries</option></select></label>
      <label>Filter by source<select value={source} onChange={e=>setSource(e.target.value)}><option>All sources</option>{enquirySources.map(s=><option key={s}>{s}</option>)}</select></label>
      {!records.length&&<p>No enquiries match this view. Website enquiries appear here after submission; staff can also record a conversation.</p>}
      {records.map(e=><article className="enquiry-card" key={e.id}><div className="section-heading"><h3>Enquiry #{e.id} · {e.customer}</h3><span className={`badge ${e.status}`}>{e.status}</span></div>
        <p><strong>Source: {e.source||'Not recorded'}</strong></p>
        {e.vehicle_id?<a href={`#/vehicles/${e.vehicle_id}`}>{snapshot.vehicles.filter(v=>v.id===e.vehicle_id).map(v=>vehicleName(v.make,v.model))}</a>:<p>General enquiry</p>}<p>Request: <strong>{e.request_type||'Other'}</strong></p>{e.status!=='closed'&&<p>Suggested next action: {suggestions[e.request_type||'Other']||suggestions.Other}</p>}
        <p>{e.message}</p>{e.email&&<p>Email: {e.email}</p>}{e.phone&&<p>Phone: {e.phone}</p>}
        <h4>Next action</h4>
        {snapshot.tasks.some(t=>t.enquiry_id===e.id&&!t.completed)?snapshot.tasks.filter(t=>t.enquiry_id===e.id&&!t.completed).map(t=><p key={t.id}>{t.note} · Due {t.due_date} · <a href={`#/follow-ups?enquiry=${e.id}`}>View follow-up</a></p>):<p>{e.status==='closed'?'Enquiry closed':'No next action scheduled'}</p>}
        {e.customer_linked&&<Conversation id={e.id} staff canWrite={canWrite} onSaved={onSaved}/>}<ResponseActions enquiry={e} onSaved={onSaved} canWrite={canWrite}/>
      </article>)}
    </section>{canWrite&&<section className="panel"><h2>Record enquiry</h2><DemoEnquiryForm snapshot={snapshot} preferredVehicle={preferredVehicle} onSaved={onSaved}/></section>}</div>
  </>;
}
