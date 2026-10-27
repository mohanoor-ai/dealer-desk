import type {Snapshot,Vehicle} from './types';
import {StockPage} from './Pages';
import type {Change} from './WorkForms';
import {money} from './api';
import CustomerAccount from './CustomerAccount';
import {PromotionsPreferences} from './Leads';
import {CompareButton,ReviewStars,BrowsingPage,rememberVehicle} from './BrowsingTools';
import {useEffect} from 'react';
import {EnquiryDialog} from './DemoEnquiries';
import PhotoGallery from './PhotoGallery';
import {vehicleName} from './navigation';

export default function CustomerDemo({snapshot,vehicle,loading,refresh}:{snapshot:Snapshot;vehicle?:Vehicle;loading:boolean;saving:boolean;change:Change;refresh:()=>Promise<void>}){
  useEffect(()=>{if(vehicle)rememberVehicle(vehicle.id)},[vehicle?.id]);
  const page=window.location.hash.split('?')[0];
  if(page==='#/promotions')return <PromotionsPreferences/>;
  if(page==='#/account')return <CustomerAccount/>;
  if(page==='#/compare'||page==='#/viewed')return <BrowsingPage cars={snapshot.vehicles} page={page==='#/compare'?'compare':'viewed'}/>;
  return <><p><a href="#/account">My enquiries</a> · <a href="#/compare">Compare vehicles</a> · <a href="#/viewed">Recently viewed</a></p>
    {vehicle?<section className="panel"><a href="#/stock">← Back to vehicles</a><p className="eyebrow">VEHICLE DETAILS</p><h1>{vehicleName(vehicle.make,vehicle.model)}</h1><p>{vehicle.year} · {vehicle.status}</p><ReviewStars make={vehicle.make} model={vehicle.model} year={vehicle.year}/><CompareButton id={vehicle.id}/><strong className="detail-price">{money(vehicle.price_pence)}</strong>{vehicle.approved_facts.map((fact,i)=><p key={i}>{fact}</p>)}<PhotoGallery vehicle={vehicle} canWrite={false} refresh={async()=>{}}/></section>:<StockPage snapshot={snapshot} loading={loading} canWrite={false} onAdd={()=>{}}/>}
    {vehicle&&<section className="panel"><EnquiryDialog snapshot={snapshot} vehicleId={vehicle.id} onSaved={refresh}/></section>}

  </>;
}
