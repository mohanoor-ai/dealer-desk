import {useEffect,useState} from 'react';
import type {FormEvent} from 'react';
import type {Snapshot,Vehicle} from './types';
import {vehicleName} from './navigation';

export type Change = (path:string,method:string,data:unknown)=>Promise<boolean>;

export function VehicleForm({vehicle,saving,onSave,onCancel}:{vehicle:Vehicle|null;saving:boolean;onSave:(event:FormEvent<HTMLFormElement>)=>void;onCancel:()=>void}) {
  return <form key={vehicle?.id||'new'} onSubmit={onSave} className="vehicle-form">
    <label>Make<input name="make" defaultValue={vehicle?.make} required maxLength={60} placeholder="e.g. Ford"/></label>
    <label>Model<input name="model" defaultValue={vehicle?.model} required maxLength={80} placeholder="e.g. Puma Titanium"/></label>
    <div className="form-row"><label>Year<input name="year" type="number" min={1900} max={2100} defaultValue={vehicle?.year||2026} required/></label><label>Price (£)<input name="price" type="number" step="0.01" min="0" max="1000000" defaultValue={vehicle?(vehicle.price_pence/100).toFixed(2):''} placeholder="0.00" required/></label></div>
    {vehicle&&<p className="hint">Changes are checked against the version you opened. If another person saves first, refresh and review before trying again.</p>}
    <div className="dialog-actions"><button className="secondary" type="button" disabled={saving} onClick={onCancel}>Cancel</button><button disabled={saving}>{saving?'Saving…':'Save vehicle'}</button></div>
  </form>;
}

export function EnquiryForm({snapshot,change,saving,preferredVehicle=0}:{snapshot:Snapshot;change:Change;saving:boolean;preferredVehicle?:number}) {
  async function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault();const form=event.currentTarget;const data=new FormData(form);
    if(await change('/api/enquiries','POST',{vehicle_id:Number(data.get('vehicle_id')),customer:String(data.get('customer')),message:String(data.get('message'))}))form.reset();
  }
  return <form onSubmit={submit} key={preferredVehicle}>
    <label>Vehicle<select name="vehicle_id" defaultValue={preferredVehicle||snapshot.vehicles[0]?.id} required>{snapshot.vehicles.map(vehicle=><option key={vehicle.id} value={vehicle.id}>{vehicleName(vehicle.make,vehicle.model)} · #{vehicle.id}</option>)}</select></label>
    <label>Customer name<input name="customer" required maxLength={80} placeholder="e.g. Alex Morgan"/></label>
    <label>Message<textarea name="message" required maxLength={1000} placeholder="What would they like to know?"/></label>
    <button disabled={saving||!snapshot.vehicles.length}>{saving?'Saving…':'Save enquiry'}</button>
  </form>;
}

export function FollowUpForm({snapshot,change,saving,preferredEnquiry=0}:{snapshot:Snapshot;change:Change;saving:boolean;preferredEnquiry?:number}) {
  const open=snapshot.enquiries.filter(enquiry=>enquiry.status!=='closed');
  const [selected,setSelected]=useState(preferredEnquiry||open[0]?.id||0);
  useEffect(()=>setSelected(preferredEnquiry||open[0]?.id||0),[preferredEnquiry]);
  useEffect(()=>{if(!open.some(e=>e.id===selected)&&open.length)setSelected(open.some(e=>e.id===preferredEnquiry)?preferredEnquiry:open[0].id);},[snapshot.enquiries,selected,preferredEnquiry]);
  async function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault();const form=event.currentTarget;const data=new FormData(form);
    if(await change('/api/tasks','POST',{enquiry_id:Number(data.get('enquiry_id')),due_date:String(data.get('due_date')),note:String(data.get('note'))}))form.reset();
  }
  return <form onSubmit={submit} key={preferredEnquiry}>
    <label>Enquiry<select name="enquiry_id" value={selected} onChange={event=>setSelected(Number(event.target.value))} required>{open.map(enquiry=><option key={enquiry.id} value={enquiry.id}>#{enquiry.id} · {enquiry.customer}</option>)}</select></label>
    <label>Due date<input name="due_date" type="date" required/></label>
    <label>Task note<textarea name="note" maxLength={300} placeholder="The next action to take"/></label>
    <button disabled={saving||!open.length}>{saving?'Saving…':'Save follow-up'}</button>
  </form>;
}
