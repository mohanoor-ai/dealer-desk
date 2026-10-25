import {useEffect,useState} from 'react';

export function routeFromHash(hash:string) {
  const path=hash.replace(/^#\/?/,'').split('/');
  if(path[0]==='car'&&/^\d+$/.test(path[1]||''))return {page:'catalogue-detail',id:Number(path[1])};
  if(path[0]==='vehicles'&&/^\d+$/.test(path[1]||''))return {page:'vehicle',id:Number(path[1])};
  if(path[0]==='vehicles'&&path[1]==='new')return {page:'new',id:0};
  return {page:['home','login','catalogue','contact','privacy','overview','enquiries','follow-ups','stock'].includes(path[0])?path[0]:(path[0]?'stock':'home'),id:0};
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
