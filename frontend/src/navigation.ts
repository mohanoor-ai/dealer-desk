import {useEffect,useState} from 'react';

export function routeFromHash(hash:string) {
  const [pathname,query='']=hash.replace(/^#\/?/,'').split('?');
  const path=pathname.split('/'),params=new URLSearchParams(query);
  const value=params.get('enquiry')||'';
  const enquiryId=/^[1-9]\d*$/.test(value)&&Number.isSafeInteger(Number(value))?Number(value):0;
  const extra={articleSlug:path[0]==='learning'?(path[1]||''):'',enquiryId,filter:params.get('status')==='open'?'open':'all'};
  if(path[0]==='car'&&/^\d+$/.test(path[1]||''))return {...extra,page:'catalogue-detail',id:Number(path[1])};
  if(path[0]==='vehicles'&&/^\d+$/.test(path[1]||''))return {...extra,page:'vehicle',id:Number(path[1])};
  if(path[0]==='vehicles'&&path[1]==='new')return {...extra,page:'new',id:0};
  return {...extra,page:['learning','home','login','catalogue','contact','privacy','cookies','terms','account','compare','viewed','promotions','leads','overview','enquiries','follow-ups','stock'].includes(path[0])?path[0]:(path[0]?'stock':'home'),id:0};
}

export function useRoute() {
  const [route,setRoute]=useState(()=>routeFromHash(window.location.hash));
  useEffect(()=>{
    const changed=()=>{setRoute(routeFromHash(window.location.hash));window.scrollTo(0,0);};
    window.addEventListener('hashchange',changed);
    return ()=>window.removeEventListener('hashchange',changed);
  },[]);
  return route;
}

export function vehicleName(make:string,model:string) {
  return `${make} ${model.replace(/\s*\(sample\)$/,'')}`;
}
