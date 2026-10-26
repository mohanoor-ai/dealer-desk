import type {Snapshot,Vehicle} from './types';
import {StockPage} from './Pages';
import type {Change} from './WorkForms';
import {money} from './api';
import {EnquiryDialog} from './DemoEnquiries';
import PhotoGallery from './PhotoGallery';
import {vehicleName} from './navigation';

export default function CustomerDemo({snapshot,vehicle,loading,refresh}:{snapshot:Snapshot;vehicle?:Vehicle;loading:boolean;saving:boolean;change:Change;refresh:()=>Promise<void>}){
  return <>
    {vehicle?<section className="panel"><a href="#/stock">← Back to vehicles</a><p className="eyebrow">VEHICLE DETAILS</p><h1>{vehicleName(vehicle.make,vehicle.model)}</h1><p>{vehicle.year} · {vehicle.status}</p><strong className="detail-price">{money(vehicle.price_pence)}</strong>{vehicle.approved_facts.map((fact,i)=><p key={i}>{fact}</p>)}<PhotoGallery vehicle={vehicle} canWrite={false} refresh={async()=>{}}/></section>:<StockPage snapshot={snapshot} loading={loading} canWrite={false} onAdd={()=>{}}/>}
    {vehicle&&<section className="panel"><EnquiryDialog snapshot={snapshot} vehicleId={vehicle.id} onSaved={refresh}/></section>}

  </>;
}
