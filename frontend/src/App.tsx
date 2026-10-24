import {useEffect,useRef,useState} from 'react';
import type {FormEvent} from 'react';
import type {Snapshot,Vehicle} from './types';
import {ApiError,loadSnapshot,request,poundsToPence} from './api';
import {useRoute} from './navigation';
import {StockPage,OverviewPage,VehiclePage,EnquiriesPage,FollowUpsPage,Heading} from './Pages';
import {VehicleForm} from './WorkForms';
import './style.css';
import './pages.css';

type User={id:number;username:string;role:'viewer'|'sales'|'manager'};
const empty:Snapshot={vehicles:[],enquiries:[],tasks:[]};
const navigation=[['overview','Overview','◈'],['stock','Vehicle stock','◇'],['enquiries','Enquiries','↗'],['follow-ups','Follow-ups','◷']];

export default function App(){
  const route=useRoute();
  const [user,setUser]=useState<User|null>(null);
  const [checking,setChecking]=useState(true);
  const [snapshot,setSnapshot]=useState(empty);
  const [loading,setLoading]=useState(false);
  const [saving,setSaving]=useState(false);
  const [error,setError]=useState('');
  const [notice,setNotice]=useState('');
  const [editing,setEditing]=useState<Vehicle|null>(null);
  const [preferredVehicle,setPreferredVehicle]=useState(0);
  const editDialog=useRef<HTMLDialogElement>(null);
  const canWrite=!!user&&user.role!=='viewer';

  function showError(error:unknown){
    setError(error instanceof Error?error.message:'Something went wrong. Please try again.');
    if(error instanceof ApiError&&error.status===401){setUser(null);setSnapshot(empty);setEditing(null);}
  }
  async function refresh(){
    try{setSnapshot(await loadSnapshot());}
    catch(error){showError(error);}
    finally{setLoading(false);}
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
    let active=true,busy=false;
    async function sync(){
      if(busy)return;busy=true;
      try{const next=await loadSnapshot();if(active)setSnapshot(next);}
      catch(error){if(active)showError(error);}
      finally{busy=false;if(active)setLoading(false);}
    }
    setLoading(true);sync();const timer=setInterval(sync,3000);
    return ()=>{active=false;clearInterval(timer);};
  },[user]);
  useEffect(()=>{if(editing)editDialog.current?.showModal();},[editing]);
  useEffect(()=>{setError('');setNotice('');setEditing(null);},[route.page,route.id]);

  async function login(event:FormEvent<HTMLFormElement>){
    event.preventDefault();const data=new FormData(event.currentTarget);setSaving(true);setError('');
    try{setUser(await request<User>('/api/auth/login','POST',{username:String(data.get('username')),password:String(data.get('password'))}));}
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
    event.preventDefault();const data=new FormData(event.currentTarget);setSaving(true);setError('');
    try{
      const fields={make:String(data.get('make')).trim(),model:String(data.get('model')).trim(),year:Number(data.get('year')),price_pence:poundsToPence(String(data.get('price')))};
      const saved=await request<Vehicle>(editing?`/api/vehicles/${editing.id}`:'/api/vehicles',editing?'PATCH':'POST',editing?{...fields,revision:editing.revision}:fields);
      setEditing(null);await refresh();window.location.hash=`/vehicles/${saved.id}`;setNotice('Vehicle saved.');
    }catch(error){showError(error);}finally{setSaving(false);}
  }
  const vehicle=snapshot.vehicles.find(vehicle=>vehicle.id===route.id);
  const onAdd=()=>{window.location.hash='/vehicles/new';};

  return <>
    <a className="skip" href="#main">Skip to content</a>
    <header><a className="brand" href="#/overview"><span className="brand-mark" aria-hidden="true">D</span><span>Dealer Desk<small>YOUR NEXT MOVE, IN VIEW</small></span></a>
      {user&&<><nav aria-label="Main navigation">{navigation.map(([page,label,icon])=><a key={page} href={`#/${page}`} className={(route.page===page||(page==='stock'&&['vehicle','new'].includes(route.page)))?'active':''} aria-current={(route.page===page||(page==='stock'&&route.page==='vehicle'))?'page':undefined}><span aria-hidden="true">{icon}</span>{label}</a>)}</nav><div className="account"><span className="avatar">{user.username[0].toUpperCase()}</span><span>{user.username}<small>{user.role}</small></span><button className="secondary" onClick={logout}>Sign out</button></div></>}
    </header>
    <main id="main">
      {error&&!editing&&<div role="alert" className="error">{error} {user&&<button className="secondary" onClick={()=>{setError('');refresh();}}>Refresh records</button>}</div>}
      {checking?<p role="status">Checking your session…</p>:!user?
        <section className="login"><div><p className="eyebrow">A CLEARER WORKING DAY</p><h1>Know your stock.<br/>Keep your promises.</h1><p>Stock, enquiries and the next follow-up.<br/>Together in one place.</p><div className="login-note">Your dealership workspace.</div></div><form className="panel login-form" onSubmit={login}><h2>Welcome back</h2><p>Sign in with your individual account.</p><label>Username<input name="username" autoComplete="username" required maxLength={80}/></label><label>Password<input name="password" type="password" autoComplete="current-password" required maxLength={128}/></label><button disabled={saving}>{saving?'Signing in…':'Sign in'}</button><small>Ask your dealership administrator for an account.</small></form></section>:
        <><div role="status" className={`global-notice ${notice?'has-notice':''}`}>{notice}</div>{user.role==='viewer'&&<p className="banner">You have read-only access. Contact a manager to request changes.</p>}
          {route.page==='stock'&&<StockPage snapshot={snapshot} loading={loading} canWrite={canWrite} onAdd={onAdd}/>}
          {route.page==='overview'&&<OverviewPage snapshot={snapshot} canWrite={canWrite} onAdd={onAdd}/>}
          {route.page==='enquiries'&&<EnquiriesPage snapshot={snapshot} canWrite={canWrite} saving={saving} change={change} preferredVehicle={preferredVehicle}/>}
          {route.page==='follow-ups'&&<FollowUpsPage snapshot={snapshot} canWrite={canWrite} saving={saving} change={change}/>}
          {route.page==='vehicle'&&(vehicle?<VehiclePage vehicle={vehicle} snapshot={snapshot} canWrite={canWrite} saving={saving} change={change} refresh={refresh} onEdit={()=>{setError('');setEditing({...vehicle});}} onEnquire={()=>{setPreferredVehicle(vehicle.id);window.location.hash='/enquiries';}}/>:<div className="empty"><h1>{loading?'Loading vehicle…':'Vehicle not found'}</h1><p>It may have been archived or removed from active stock.</p><a href="#/stock">Return to stock</a></div>)}
          {route.page==='new'&&(canWrite?<><Heading eyebrow="YOUR INVENTORY / NEW VEHICLE" title="Add to your stock." description="Start with the essentials. You can add photos on the vehicle page."/><section className="panel new-vehicle-panel"><VehicleForm vehicle={null} saving={saving} onSave={saveVehicle} onCancel={()=>{window.location.hash='/stock';}}/></section></>:<div className="empty">Your account has read-only access.</div>)}
          <footer><span>Dealer Desk</span>Vehicle stock, enquiries and follow-ups.</footer>
        </>}
      {editing&&<dialog ref={editDialog} className="upload-dialog" onCancel={event=>{if(saving)event.preventDefault();else setEditing(null);}} onClose={()=>setEditing(null)}><div className="section-heading"><h2>Edit vehicle</h2><button className="icon-button" disabled={saving} aria-label="Close vehicle editor" onClick={()=>setEditing(null)}>×</button></div>{error&&<p role="alert" className="error">{error}</p>}<VehicleForm vehicle={editing} saving={saving} onSave={saveVehicle} onCancel={()=>setEditing(null)}/></dialog>}
    </main>
  </>;
}
