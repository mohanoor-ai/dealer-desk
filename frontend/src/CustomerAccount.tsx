import {useEffect,useState} from 'react';
import type {ReactNode} from 'react';
import {request,ApiError} from './api';
import {demoActive,endDemo} from './demo';

type Account={name:string;email:string};
type CustomerEnquiry={id:number;vehicle_id:number|null;message:string;status:string;request_type:string};
export type ConversationMessage={id:number;author_role:string;body:string;created_at:string};

export function Conversation({id,staff=false,canWrite=true,onSaved=async()=>{},showHistory=true,followUpFields}:{id:number;staff?:boolean;canWrite?:boolean;onSaved?:()=>Promise<void>;showHistory?:boolean;followUpFields?:ReactNode}){
 const [items,setItems]=useState<ConversationMessage[]>([]),[text,setText]=useState(''),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 const path=staff?`/api/enquiries/${id}/messages`:`/api/customer/enquiries/${id}/messages`;
 async function load(){try{setItems((await request<{items:ConversationMessage[]}>(path)).items);}catch(e){setError(e instanceof Error?e.message:'Could not load messages.');}}
 useEffect(()=>{load();const timer=setInterval(load,3000);return()=>clearInterval(timer)},[path]);
 return <section className="conversation" aria-label={`Conversation for enquiry ${id}`}><h3>{showHistory?'Customer conversation':'Reply in account'}</h3>{error&&<p role="alert">{error}</p>}
 {showHistory&&(items.length?<ol>{items.map(m=><li key={m.id}><strong>{m.author_role==='staff'?'Dealership':'Customer'}</strong> · <time>{new Date(m.created_at).toLocaleString('en-GB')}</time><p style={{whiteSpace:'pre-wrap'}}>{m.body}</p></li>)}</ol>:<p>No follow-up messages yet.</p>)}
 {canWrite&&<form onSubmit={async e=>{e.preventDefault();if(busy)return;setBusy(true);setError('');try{const form=new FormData(e.currentTarget);await request(path,'POST',{body:text,...(staff&&form.get('schedule_follow_up')?{follow_up:{note:String(form.get('follow_up_note')),due_date:String(form.get('follow_up_date'))}}:{})});setText('');await load();await onSaved();}catch(e){setError(e instanceof Error?e.message:'Message could not be saved.')}finally{setBusy(false)}}}>
 <label>{staff?'Reply in customer account':'Follow up this enquiry'}<textarea value={text} maxLength={2000} required onChange={e=>setText(e.target.value)}/></label>{followUpFields}<button disabled={busy||!text.trim()}>{busy?'Saving…':'Send message'}</button></form>}
 </section>;
}

export default function CustomerAccount(){
 const [account,setAccount]=useState<Account|null>(null),[items,setItems]=useState<CustomerEnquiry[]>([]),[mode,setMode]=useState<'login'|'register'|'recovery'>('login');
 const [registrationEnabled,setRegistrationEnabled]=useState(!demoActive()&&['localhost','127.0.0.1'].includes(window.location.hostname));
 const [error,setError]=useState(''),[notice,setNotice]=useState(''),[preview,setPreview]=useState(''),[busy,setBusy]=useState(false);
 const query=new URLSearchParams(window.location.hash.split('?')[1]||'');const token=query.get('token'),purpose=query.get('purpose');
 async function load(){try{setAccount(await request<Account>('/api/customer/me'));setItems((await request<{items:CustomerEnquiry[]}>('/api/customer/enquiries')).items)}catch(e){if(e instanceof ApiError&&e.status===401)setAccount(null);else setError(e instanceof Error?e.message:'Account could not load.')}}
 useEffect(()=>{load();if(!demoActive())request<{customer_registration:boolean}>('/api/catalogue/capabilities').then(c=>setRegistrationEnabled(c.customer_registration)).catch(()=>setRegistrationEnabled(false))},[]);
 useEffect(()=>{if(!account)return;const timer=setInterval(load,3000);return()=>clearInterval(timer)},[account?.email]);
 async function action(path:string,body:unknown){setBusy(true);setError('');try{const result=await request<{message?:string;local_email_url?:string}>(path,'POST',body);setNotice(result?.message||'Saved successfully.');setPreview(result?.local_email_url||'');await load();return true}catch(e){setError(e instanceof Error?e.message:'Please try again.');return false}finally{setBusy(false)}}
 return <section className="public-copy panel"><h1>My enquiries</h1>{error&&<p role="alert">{error}</p>}{notice&&<p role="status">{notice}</p>}
 {preview&&<aside className="banner"><strong>Local email preview — no email was sent.</strong><p>This testing link is available only in the local app. It does not prove ownership of a real inbox.</p><a href={preview}>Open local verification / recovery email</a></aside>}
 {token?<form onSubmit={async e=>{e.preventDefault();const data=new FormData(e.currentTarget);if(await action(purpose==='reset'?'/api/customer/reset':'/api/customer/verify',purpose==='reset'?{token,password:String(data.get('password')),purpose:'reset'}:{token,purpose:'verify'})){window.location.hash='/account';window.location.reload()}}}>
 <p>{purpose==='reset'?'Choose a new password.':'Confirm this local account verification link.'}</p>{purpose==='reset'&&<label>New password<input name="password" type="password" minLength={12} maxLength={128} required autoComplete="new-password"/></label>}<button disabled={busy}>{purpose==='reset'?'Change password':'Verify account'}</button></form>:
 account?<><p>Signed in as {account.name} · {account.email}</p><button className="secondary" onClick={async()=>{if(demoActive()){endDemo();window.location.hash='/login';window.location.reload();return}await action('/api/customer/logout',{});setAccount(null);setItems([])}}>Customer sign out</button><h2>Your enquiries</h2>{!items.length&&<p>No enquiries are linked to this verified account yet. <a href="#/catalogue">Browse vehicles</a>.</p>}{items.map(e=><article className="enquiry-card" key={e.id}><h2>Enquiry #{e.id} · {e.request_type}</h2><span className="badge">{e.status}</span><p>{e.message}</p>{e.vehicle_id&&<a href={`#/car/${e.vehicle_id}`}>View vehicle</a>}<Conversation id={e.id}/></article>)}</>:
 <><p>Sign in to follow up an existing enquiry and read dealership replies. Browsing does not require an account.</p><div className="dialog-actions"><button className="secondary" onClick={()=>setMode('login')}>Customer sign in</button>{registrationEnabled&&<><button className="secondary" onClick={()=>setMode('register')}>Register</button><button className="secondary" onClick={()=>setMode('recovery')}>Forgot password</button></>}</div>
 {!registrationEnabled&&<p>New customer accounts and password recovery are not available yet. You can still browse vehicles and send an enquiry. Staff will respond using the contact details provided.</p>}
 <form key={mode} onSubmit={e=>{e.preventDefault();const data=new FormData(e.currentTarget);action(`/api/customer/${mode}`,{email:String(data.get('email')),...(mode!=='recovery'?{password:String(data.get('password'))}:{}),...(mode==='register'?{name:String(data.get('name'))}:{})})}}>
 {mode==='register'&&<label>Your name<input name="name" required maxLength={80}/></label>}<label>Email<input name="email" type="email" required maxLength={254} autoComplete="email"/></label>{mode!=='recovery'&&<label>Password<input name="password" type="password" minLength={12} maxLength={128} required autoComplete={mode==='register'?'new-password':'current-password'}/></label>}<button disabled={busy}>{busy?'Please wait…':mode==='register'?'Create customer account':mode==='recovery'?'Request recovery':'Sign in to my enquiries'}</button></form>
 <p>Registration requires verification before enquiry access. Guest enquiries are linked only after that step. <a href="#/privacy">Privacy</a> · <a href="#/terms">Terms</a></p></>}
 </section>;
}
