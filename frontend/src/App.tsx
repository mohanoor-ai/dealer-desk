import {useEffect, useState} from 'react';
import type {FormEvent} from 'react';
import type {Snapshot, Vehicle} from './types';
import {ApiError, loadSnapshot, request, money, poundsToPence} from './api';
import './style.css';

type User = {id:number; username:string; role:'viewer'|'sales'|'manager'};
const empty:Snapshot = {vehicles:[], enquiries:[], tasks:[]};

export default function App() {
  const [user,setUser]=useState<User|null>(null);
  const [checking,setChecking]=useState(true);
  const [snapshot,setSnapshot]=useState(empty);
  const [loading,setLoading]=useState(false);
  const [saving,setSaving]=useState(false);
  const [error,setError]=useState('');
  const [notice,setNotice]=useState('');
  const [query,setQuery]=useState('');
  const [status,setStatus]=useState('all');
  const [editing,setEditing]=useState<Vehicle|null>(null);

  function showError(error:unknown) {
    setError(error instanceof Error?error.message:'Something went wrong. Please try again.');
    if(error instanceof ApiError&&error.status===401){setUser(null);setSnapshot(empty);setEditing(null);}
  }
  async function refresh() {
    setLoading(true);
    try{setSnapshot(await loadSnapshot());setError('');}
    catch(error){showError(error);}finally{setLoading(false);}
  }
  useEffect(()=>{
    let active=true;
    request<User>('/api/auth/me').then(value=>{if(active)setUser(value);})
      .catch(error=>{if(active&&!(error instanceof ApiError&&error.status===401))showError(error);})
      .finally(()=>{if(active)setChecking(false);});
    return ()=>{active=false;};
  },[]);
  useEffect(()=>{
    if(!user)return;
    let active=true;let busy=false;
    async function sync(){
      if(busy)return;busy=true;
      try{const next=await loadSnapshot();if(active)setSnapshot(next);}
      catch(error){if(active)showError(error);}finally{busy=false;if(active)setLoading(false);}
    }
    setLoading(true);sync();const timer=setInterval(sync,3000);
    return ()=>{active=false;clearInterval(timer);};
  },[user]);
  async function login(event:FormEvent<HTMLFormElement>){
    event.preventDefault();const data=new FormData(event.currentTarget);setSaving(true);setError('');
    try{setUser(await request<User>('/api/auth/login','POST',{username:String(data.get('username')),password:String(data.get('password'))}));setNotice('');}
    catch(error){showError(error);}finally{setSaving(false);}
  }
  async function logout(){
    try{await request('/api/auth/logout','POST');setUser(null);setSnapshot(empty);setEditing(null);setNotice('');}
    catch(error){showError(error);}
  }
  async function change(path:string,method:string,data:unknown){
    setSaving(true);setError('');setNotice('');
    try{await request(path,method,data);await refresh();setNotice('Saved successfully.');return true;}
    catch(error){showError(error);return false;}finally{setSaving(false);}
  }
  async function saveVehicle(event:FormEvent<HTMLFormElement>){
    event.preventDefault();const form=event.currentTarget;const data=new FormData(form);
    try{
      const fields={make:String(data.get('make')).trim(),model:String(data.get('model')).trim(),year:Number(data.get('year')),price_pence:poundsToPence(String(data.get('price')))};
      if(await change(editing?`/api/vehicles/${editing.id}`:'/api/vehicles',editing?'PATCH':'POST',editing?{...fields,revision:editing.revision}:fields)){setEditing(null);form.reset();}
    }catch(error){showError(error);}
  }
  async function saveEnquiry(event:FormEvent<HTMLFormElement>){
    event.preventDefault();const form=event.currentTarget;const data=new FormData(form);
    if(await change('/api/enquiries','POST',{vehicle_id:Number(data.get('vehicle_id')),customer:String(data.get('customer')),message:String(data.get('message'))}))form.reset();
  }
  async function saveTask(event:FormEvent<HTMLFormElement>){
    event.preventDefault();const form=event.currentTarget;const data=new FormData(form);
    if(await change('/api/tasks','POST',{enquiry_id:Number(data.get('enquiry_id')),due_date:String(data.get('due_date')),note:String(data.get('note'))}))form.reset();
  }
  const canWrite=user?.role!=='viewer';
  const visible=snapshot.vehicles.filter(v=>`${v.make} ${v.model}`.toLowerCase().includes(query.toLowerCase())&&(status==='all'||v.status===status));
  const openEnquiries=snapshot.enquiries.filter(e=>e.status!=='closed');
  const openTasks=snapshot.tasks.filter(t=>!t.completed&&openEnquiries.some(e=>e.id===t.enquiry_id));
  const value=snapshot.vehicles.filter(v=>v.status!=='sold').reduce((sum,v)=>sum+v.price_pence,0);
  return <>
    <a className="skip" href="#main">Skip to content</a>
    <header><div className="brand"><span className="brand-mark" aria-hidden="true">D</span><span>Dealer Desk<small>YOUR NEXT MOVE, IN VIEW</small></span></div>{user&&<div className="account"><span>{user.username} · {user.role}</span><button className="secondary" onClick={logout}>Sign out</button></div>}</header>
    <main id="main">
      {error&&<div role="alert" className="error">{error} {user&&<button className="secondary" onClick={refresh}>Refresh records</button>}</div>}
      {checking?<p role="status">Checking your session…</p>:!user?
      <section className="login"><div><p className="eyebrow">A CLEARER WORKING DAY</p><h1>Know your stock.<br/>Keep your promises.</h1><p>Stock, enquiries and the next follow-up.<br/>Together in one place.</p><div className="login-note">Educational demonstration · use fictional information only.</div></div>
        <form className="panel login-form" onSubmit={login}><h2>Welcome back</h2><p>Sign in with your individual account.</p><label>Username<input name="username" autoComplete="username" required maxLength={80}/></label><label>Password<input name="password" type="password" autoComplete="current-password" required maxLength={128}/></label><button disabled={saving}>{saving?'Signing in…':'Sign in'}</button><small>Ask your dealership administrator for an account.</small></form>
      </section>:<>
        <div className="page-heading"><div><p className="eyebrow">WORKSPACE / OVERVIEW</p><h1>A clear view of today.</h1><p>Keep stock moving and every conversation on track.</p></div><span className="live-label">● Shared workspace</span></div>
        <p role="status" className="notice">{notice}</p>{user.role==='viewer'&&<p className="banner">You have read-only access. Contact a manager to request changes.</p>}
        <section className="metrics" aria-label="Business overview"><article><small>Active stock</small><strong>{snapshot.vehicles.length}</strong><span>vehicles on your desk</span></article><article><small>Unsold stock value</small><strong>{money(value)}</strong><span>available and reserved</span></article><article><small>Open enquiries</small><strong>{openEnquiries.length}</strong><span>conversations to progress</span></article><article><small>Open follow-ups</small><strong>{openTasks.length}</strong><span>actions to complete</span></article></section>
        <section className="panel" id="stock"><div className="section-heading"><div><p className="eyebrow">YOUR INVENTORY</p><h2>Vehicle stock</h2></div><button className="secondary" onClick={refresh}>Refresh</button></div>
          <div className="filters"><label>Search stock<input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search make or model…"/></label><label>Stock status<select value={status} onChange={e=>setStatus(e.target.value)}><option value="all">All statuses</option>{['available','reserved','sold'].map(s=><option key={s} value={s}>{s}</option>)}</select></label></div>
          {loading&&!snapshot.vehicles.length?<p role="status">Loading stock…</p>:!visible.length?<div className="empty"><h3>{query||status!=='all'?'No matching vehicles':'Your stock starts here'}</h3><p>{query||status!=='all'?'Try another make, model or status.':'Add your first vehicle using the form below.'}</p></div>:<div className="stock">{visible.map(v=><article key={v.id}><div className="vehicle-top"><span className={`badge ${v.status}`}>{v.status}</span><small>STOCK #{v.id}</small></div><div className="vehicle-icon" aria-hidden="true"><svg viewBox="0 0 240 100"><path d="M36 64 55 34h105l37 30 18 7v16H24V71z"/><path d="m66 42-12 22h111l-23-22z"/><circle cx="64" cy="84" r="12"/><circle cx="180" cy="84" r="12"/></svg></div><small>{v.year}</small><h3>{v.make} {v.model}</h3><strong className="price">{money(v.price_pence)}</strong>
            <label>Status<select aria-label={`Status for ${v.make} ${v.model}`} value={v.status} disabled={saving||!canWrite} onChange={e=>change(`/api/vehicles/${v.id}`,'PATCH',{status:e.target.value,revision:v.revision})}>{['available','reserved','sold'].map(s=><option key={s}>{s}</option>)}</select></label>{canWrite&&<button className="secondary" onClick={()=>{setEditing({...v});document.getElementById('vehicle-form')?.scrollIntoView({behavior:'smooth'});}}>Edit vehicle</button>}</article>)}</div>}
        </section>
        {canWrite&&<div className="grid forms">
          <section className="panel" id="vehicle-form"><p className="eyebrow">01 / STOCK</p><h2>{editing?'Edit vehicle':'Add vehicle'}</h2>{editing&&<p className="hint">Editing stock #{editing.id}. A changed record must be refreshed before saving.</p>}<form key={editing?.id||'new'} onSubmit={saveVehicle}><label>Make<input name="make" defaultValue={editing?.make} required maxLength={60}/></label><label>Model<input name="model" defaultValue={editing?.model} required maxLength={80}/></label><div className="form-row"><label>Year<input name="year" type="number" min={1900} max={2100} defaultValue={editing?.year||2020} required/></label><label>Price (£)<input name="price" type="number" step="0.01" min="0" max="1000000" defaultValue={editing?(editing.price_pence/100).toFixed(2):''} required/></label></div><button disabled={saving}>Save vehicle</button>{editing&&<button className="secondary" type="button" onClick={()=>setEditing(null)}>Cancel edit</button>}</form></section>
          <section className="panel"><p className="eyebrow">02 / CONVERSATION</p><h2>Record enquiry</h2><form onSubmit={saveEnquiry}><label>Vehicle<select name="vehicle_id" required>{snapshot.vehicles.map(v=><option key={v.id} value={v.id}>{v.make} {v.model}</option>)}</select></label><label>Customer name<input name="customer" required maxLength={80}/></label><label>Message<textarea name="message" required maxLength={1000}/></label><button disabled={saving||!snapshot.vehicles.length}>Save enquiry</button></form></section>
          <section className="panel"><p className="eyebrow">03 / NEXT ACTION</p><h2>Schedule follow-up</h2><form onSubmit={saveTask}><label>Enquiry<select name="enquiry_id" required>{openEnquiries.map(e=><option key={e.id} value={e.id}>#{e.id} · {e.customer}</option>)}</select></label><label>Due date<input name="due_date" type="date" required/></label><label>Task note<textarea name="note" maxLength={300}/></label><button disabled={saving||!openEnquiries.length}>Save follow-up</button></form></section>
        </div>}
        <div className="grid queues"><section className="panel"><p className="eyebrow">CONVERSATIONS</p><h2>Enquiry queue</h2>{!snapshot.enquiries.length&&<div className="empty"><h3>No enquiries yet</h3><p>Record a conversation to keep its next action visible.</p></div>}{snapshot.enquiries.map(e=><article className="queue-item" key={e.id}><strong>{e.customer} · stock #{e.vehicle_id}</strong><p>{e.message}</p><label>Enquiry status<select aria-label={`Status for enquiry ${e.id}`} value={e.status} disabled={saving||!canWrite} onChange={event=>change(`/api/enquiries/${e.id}`,'PATCH',{status:event.target.value,revision:e.revision})}>{['new','contacted','closed'].map(s=><option key={s}>{s}</option>)}</select></label></article>)}</section>
          <section className="panel"><p className="eyebrow">NEXT ACTIONS</p><h2>Follow-up tasks</h2>{!snapshot.tasks.length&&<div className="empty"><h3>Nothing scheduled</h3><p>Give each conversation a clear next step.</p></div>}{snapshot.tasks.map(t=><article className="queue-item" key={t.id}><span className={`badge ${t.completed?'completed':'reserved'}`}>{t.completed?'Completed':'Open'}</span><p>Enquiry #{t.enquiry_id} · {t.due_date}</p><strong>{t.note||'Customer follow-up'}</strong><br/>{canWrite&&<button className="secondary" disabled={saving} onClick={()=>change(`/api/tasks/${t.id}`,'PATCH',{completed:!t.completed,revision:t.revision})}>{t.completed?'Reopen task':'Complete task'}</button>}</article>)}</section></div>
        <footer>Dealer Desk · Educational demonstration. Use fictional customer and stock information only.</footer>
      </>}
    </main>
  </>;
}
