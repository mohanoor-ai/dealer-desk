import {useState} from 'react';
import type {FormEvent} from 'react';
import type {Snapshot} from './types';
import {request} from './api';
import {demoActive,enquirySources,type PipelineEnquiry} from './demo';
import {vehicleName} from './navigation';

export function emailDraftUrl(email:string,subject:string,body:string){
  if(!/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(email)||/[\r\n]/.test(email+subject))return '';
  return `mailto:${encodeURIComponent(email)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}

export function DemoEnquiryForm({snapshot,website=false,preferredVehicle=0,onSaved}:{snapshot:Snapshot;website?:boolean;preferredVehicle?:number;onSaved:()=>Promise<void>}){
  const [busy,setBusy]=useState(false),[error,setError]=useState(''),[receipt,setReceipt]=useState(0);
  async function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault();if(busy)return;const form=event.currentTarget,data=new FormData(form);setBusy(true);setError('');setReceipt(0);
    try{
      if(!demoActive())throw new Error('Start a new demo.');
      const row=await request<PipelineEnquiry>('/api/demo/enquiries','POST',{vehicle_id:Number(data.get('vehicle_id')),customer:String(data.get('customer')),email:String(data.get('email')),phone:String(data.get('phone')),message:String(data.get('message')),source:website?'Website':String(data.get('source'))});
      await onSaved();setReceipt(row.id);form.reset();
    }catch(e){setError(e instanceof Error?e.message:'Could not save the enquiry.');}finally{setBusy(false);}
  }
  return <form onSubmit={submit} className="pipeline-form">
    <p>Local workflow preview. Use test contact details. Records stay in this tab.</p>
    {receipt>0&&<p role="status">Enquiry #{receipt} received. {website?'Switch to staff view to respond.':'Open it in the staff queue.'}</p>}
    {error&&<p role="alert">{error}</p>}
    <label>Vehicle<select name="vehicle_id" defaultValue={preferredVehicle||snapshot.vehicles[0]?.id} required>{snapshot.vehicles.map(v=><option key={v.id} value={v.id}>{vehicleName(v.make,v.model)}</option>)}</select></label>
    {website?<p>Enquiry source: <strong>Website</strong></p>:<label>Enquiry source<select name="source" required defaultValue=""><option value="" disabled>Select source</option>{enquirySources.map(source=><option key={source}>{source}</option>)}</select></label>}
    <label>Customer name<input name="customer" required maxLength={80}/></label>
    <label>Email address<input name="email" type="email" required={website} maxLength={254} placeholder="alex@example.com"/></label>
    <label>Phone number<input name="phone" type="tel" maxLength={40}/></label>
    <label>Message<textarea name="message" required maxLength={1000}/></label>
    <button disabled={busy||!snapshot.vehicles.length}>{busy?'Saving…':website?'Submit website enquiry':'Save enquiry'}</button>
  </form>;
}

function ResponseActions({enquiry,onSaved}:{enquiry:PipelineEnquiry;onSaved:()=>Promise<void>}){
  const [subject,setSubject]=useState(`Your vehicle enquiry #${enquiry.id}`),[body,setBody]=useState('');
  const [confirmed,setConfirmed]=useState(false),[opened,setOpened]=useState(false),[outcome,setOutcome]=useState('');
  const [busy,setBusy]=useState(false),[error,setError]=useState('');
  const draft=emailDraftUrl(enquiry.email||'',subject,body);
  async function save(action:'reply'|'close'){
    if(busy)return;setBusy(true);setError('');
    try{
      if(!demoActive())throw new Error('Start a new demo.');
      await request(`/api/demo/enquiries/${enquiry.id}/${action}`,'POST',{revision:enquiry.revision,...(action==='reply'?{subject,body,confirmed}:{outcome})});
      await onSaved();setConfirmed(false);setOpened(false);setBody('');setOutcome('');
    }catch(e){setError(e instanceof Error?e.message:'Could not record the action.');}finally{setBusy(false);}
  }
  return <section aria-label={`Response for enquiry ${enquiry.id}`}>
    {error&&<p role="alert">{error}</p>}
    {enquiry.status!=='closed'&&<>
      <h4>Reply by email</h4>
      {enquiry.email?<><p>To: {enquiry.email}</p>
        <label>Reply subject<input value={subject} maxLength={160} onChange={e=>{setSubject(e.target.value);setOpened(false);setConfirmed(false);}}/></label>
        <label>Reply message<textarea value={body} maxLength={2000} onChange={e=>{setBody(e.target.value);setOpened(false);setConfirmed(false);}}/></label>
        {draft&&subject.trim()&&body.trim()?<a className="button-link secondary" href={draft} onClick={()=>setOpened(true)}>Open in email app</a>:<p>Enter a subject and reply to open your email app.</p>}
        <p>The app cannot verify sending or delivery. Opening your email app does not change the enquiry.</p>
        <label><input type="checkbox" checked={confirmed} disabled={!opened||busy} onChange={e=>setConfirmed(e.target.checked)}/> I sent this email</label>
        <button disabled={!opened||!confirmed||busy} onClick={()=>save('reply')}>Record sent email</button>
      </>:<p>No email address recorded. Contact the customer using the supplied details, then record the outcome.</p>}
      <p><a className="button-link secondary" href={`#/follow-ups?enquiry=${enquiry.id}`}>Schedule follow-up</a></p>
      <label>Closing outcome<textarea maxLength={300} value={outcome} onChange={e=>setOutcome(e.target.value)} placeholder="What happened and why is no further action needed?"/></label>
      <button className="secondary" disabled={!outcome.trim()||busy} onClick={()=>save('close')}>Close enquiry</button>
    </>}
    <h4>Activity</h4>
    <ol>{(enquiry.activity||[]).map((event,i)=><li key={i}><strong>{event.kind}</strong> · {event.actor} · <time dateTime={event.at}>{new Date(event.at).toLocaleString('en-GB')}</time>{event.subject&&<p>{event.subject}</p>}{event.body&&<p style={{whiteSpace:'pre-wrap'}}>{event.body}</p>}{event.outcome&&<p>{event.outcome}</p>}</li>)}</ol>
  </section>;
}

export default function DemoEnquiries({snapshot,selectedEnquiry=0,onSaved}:{snapshot:Snapshot;selectedEnquiry?:number;onSaved:()=>Promise<void>}){
  const [source,setSource]=useState('All sources');
  const records=(snapshot.enquiries as PipelineEnquiry[]).filter(e=>(!selectedEnquiry||e.id===selectedEnquiry)&&(source==='All sources'||source===e.source));
  return <><h1>Enquiries</h1><p>Review the request, record your response and choose the next action.</p>
    {selectedEnquiry>0&&<p><a href="#/enquiries">View all enquiries</a></p>}
    <div className="work-grid"><section className="panel"><h2>Staff queue</h2>
      <label>Filter by source<select value={source} onChange={e=>setSource(e.target.value)}><option>All sources</option>{enquirySources.map(s=><option key={s}>{s}</option>)}</select></label>
      {!records.length&&<p>No enquiries here yet. Switch to customer website view to submit one, or record an enquiry.</p>}
      {records.map(e=><article className="enquiry-card" key={e.id}><div className="section-heading"><h3>Enquiry #{e.id} · {e.customer}</h3><span className={`badge ${e.status}`}>{e.status}</span></div>
        <p><strong>Source: {e.source||'Not recorded'}</strong></p>
        <a href={`#/vehicles/${e.vehicle_id}`}>{snapshot.vehicles.filter(v=>v.id===e.vehicle_id).map(v=>vehicleName(v.make,v.model))}</a>
        <p>{e.message}</p>{e.email&&<p>Email: {e.email}</p>}{e.phone&&<p>Phone: {e.phone}</p>}
        <h4>Next action</h4>
        {snapshot.tasks.some(t=>t.enquiry_id===e.id&&!t.completed)?snapshot.tasks.filter(t=>t.enquiry_id===e.id&&!t.completed).map(t=><p key={t.id}>{t.note} · Due {t.due_date} · <a href={`#/follow-ups?enquiry=${e.id}`}>View follow-up</a></p>):<p>{e.status==='closed'?'Enquiry closed':'No next action scheduled'}</p>}
        <ResponseActions enquiry={e} onSaved={onSaved}/>
      </article>)}
    </section><section className="panel"><h2>Record enquiry</h2><DemoEnquiryForm snapshot={snapshot} onSaved={onSaved}/></section></div>
  </>;
}
