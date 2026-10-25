import {useEffect,useRef,useState} from 'react';
type Item={label:string;href:string;current?:boolean};
type Props={items:Item[];routeKey:string;staff:boolean;onLogout?:()=>Promise<void>;onTryDemo?:()=>void};
function Bars(){return <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>}
export default function MobileNavigation({items,routeKey,staff,onLogout,onTryDemo}:Props){
 const dialog=useRef<HTMLDialogElement>(null),trigger=useRef<HTMLButtonElement|null>(null);
 const [open,setOpen]=useState(false),[origin,setOrigin]=useState<'top'|'bottom'>('top');
 function close(){if(dialog.current?.open)dialog.current.close();setOpen(false);trigger.current?.focus();}
 function show(where:'top'|'bottom',button:HTMLButtonElement){trigger.current=button;setOrigin(where);dialog.current?.showModal();setOpen(true);}
 useEffect(()=>{if(dialog.current?.open)dialog.current.close();setOpen(false);},[routeKey]);
 useEffect(()=>{const media=window.matchMedia?.('(min-width: 761px)');if(!media)return;const resize=()=>{if(media.matches&&dialog.current?.open){dialog.current.close();setOpen(false);}};media.addEventListener('change',resize);return()=>media.removeEventListener('change',resize);},[]);
 return <>
  <button className="mobile-menu-trigger secondary" aria-label="Open navigation" aria-controls="mobile-navigation-dialog" aria-haspopup="dialog" aria-expanded={open} onClick={e=>show('top',e.currentTarget)}><Bars/><span>Menu</span></button>
  <div className="mobile-bottom-bar" aria-label="Mobile shortcuts"><a href={staff?'#/overview':'#/home'}>{staff?'Overview':'Home'}</a><button className="secondary" aria-label="Open bottom navigation" aria-controls="mobile-navigation-dialog" aria-haspopup="dialog" aria-expanded={open} onClick={e=>show('bottom',e.currentTarget)}><Bars/><span>Menu</span></button></div>
  <dialog ref={dialog} id="mobile-navigation-dialog" className="mobile-navigation-dialog" data-origin={origin} aria-labelledby="mobile-navigation-title" onCancel={e=>{e.preventDefault();close();}} onClose={()=>setOpen(false)} onClick={e=>{if(e.target===e.currentTarget){const box=e.currentTarget.getBoundingClientRect();if(e.clientX<box.left||e.clientX>box.right||e.clientY<box.top||e.clientY>box.bottom)close();}}}>
   <div className="mobile-menu-heading"><h2 id="mobile-navigation-title">{staff?'Staff navigation':'Menu'}</h2><button className="secondary" aria-label="Close navigation" onClick={close}>Close ×</button></div>
   <nav aria-label="Mobile navigation">{items.map(item=><a key={item.href} href={item.href} aria-current={item.current?'page':undefined} onClick={close}>{item.label}<span aria-hidden="true">→</span></a>)}</nav>
   {onTryDemo&&<button className="secondary mobile-menu-action" onClick={()=>{close();onTryDemo();}}>Try demo</button>}
   {onLogout&&<button className="secondary mobile-menu-action" onClick={()=>{close();void onLogout();}}>Sign out</button>}
  </dialog>
 </>;
}
