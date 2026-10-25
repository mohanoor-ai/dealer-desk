import type {Snapshot,Vehicle} from './types';
import {StockPage} from './Pages';
import {EnquiryForm,type Change} from './WorkForms';
import {money} from './api';

export default function CustomerDemo({snapshot,vehicle,loading,saving,change}:{snapshot:Snapshot;vehicle?:Vehicle;loading:boolean;saving:boolean;change:Change}){
  return <>
    {vehicle?<section className="panel"><a href="#/stock">← Back to vehicles</a><p className="eyebrow">VEHICLE DETAILS</p><h1>{vehicle.make} {vehicle.model}</h1><p>{vehicle.year} · {vehicle.status}</p><strong className="detail-price">{money(vehicle.price_pence)}</strong>{vehicle.approved_facts.map((fact,i)=><p key={i}>{fact}</p>)}</section>:<StockPage snapshot={snapshot} loading={loading} canWrite={false} onAdd={()=>{}}/>}
    <section className="panel"><h2>Try a vehicle enquiry</h2><p>This demonstrates the form only. No enquiry is sent to the dealership. Use demonstration details.</p><EnquiryForm snapshot={snapshot} change={change} saving={saving} preferredVehicle={vehicle?.id||0}/></section>
  </>;
}
