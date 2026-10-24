import {useEffect,useRef,useState} from 'react';
import type {FormEvent} from 'react';
import type {Photo,Vehicle} from './types';
import {photoUrl,readPhoto,request} from './api';
import {vehicleName} from './navigation';
import {demoActive} from './demo';

export function PhotoCredit({photo}:{photo:Photo}) {
  return <span className="photo-credit">{photo.credit&&<>Photo: {photo.credit} · </>}{photo.source_url&&<><a href={photo.source_url} target="_blank" rel="noreferrer">Source</a> · </>}{photo.license_url?<a href={photo.license_url} target="_blank" rel="noreferrer">{photo.license}</a>:photo.license}{photo.credit&&' · Optimized and resized'}</span>;
}

export default function PhotoGallery({vehicle,canWrite,refresh}:{vehicle:Vehicle;canWrite:boolean;refresh:()=>Promise<void>}) {
  canWrite=canWrite&&!demoActive();
  const [photos,setPhotos]=useState<Photo[]>([]);
  const [selected,setSelected]=useState(0);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState('');
  const [uploading,setUploading]=useState(false);
  const [showUpload,setShowUpload]=useState(false);
  const [files,setFiles]=useState<File[]>([]);
  const [caption,setCaption]=useState(`${vehicleName(vehicle.make,vehicle.model)} photo`);
  const [illustrative,setIllustrative]=useState(vehicle.model.includes('(sample)'));
  const [rights,setRights]=useState(false);
  const [credit,setCredit]=useState('');
  const [sourceUrl,setSourceUrl]=useState('');
  const [license,setLicense]=useState('');
  const [licenseUrl,setLicenseUrl]=useState('');
  const [notice,setNotice]=useState('');
  const dialog=useRef<HTMLDialogElement>(null);
  const active=photos.find(photo=>photo.id===selected)||photos.find(photo=>photo.is_cover)||photos[0];

  useEffect(()=>{
    let current=true;
    request<Photo[]>(`/api/vehicles/${vehicle.id}/photos`).then(rows=>{if(current){setPhotos(rows);setError('');}})
      .catch(error=>{if(current)setError(error.message);}).finally(()=>{if(current)setLoading(false);});
    return ()=>{current=false;};
  },[vehicle.id,vehicle.revision]);
  useEffect(()=>{if(showUpload)dialog.current?.showModal();},[showUpload]);

  async function setCover() {
    if(!active)return;
    setUploading(true);setError('');
    try{await request(`/api/vehicles/${vehicle.id}/photos/${active.id}/cover`,'PATCH',{revision:vehicle.revision});await refresh();setNotice('Cover photo updated.');}
    catch(error){setError((error as Error).message);await refresh();}
    finally{setUploading(false);}
  }
  async function upload(event:FormEvent) {
    event.preventDefault();setError('');setUploading(true);
    let revision=vehicle.revision,added=0;
    try{
      if(!files.length)throw new Error('Choose at least one image.');
      if(!rights)throw new Error('Confirm that you have permission to use these photos.');
      if(photos.length+files.length>12)throw new Error('Choose fewer images. Each vehicle can have up to 12 photos.');
      // Validate every file before saving the first, then upload sequentially without retries.
      const images=await Promise.all(files.map(readPhoto));
      for(const data_url of images){
        const result=await request<{photo:Photo;vehicle_revision:number}>(`/api/vehicles/${vehicle.id}/photos`,'POST',{
          data_url,revision,caption:caption.trim(),rights_confirmed:true,illustrative,
          credit,source_url:sourceUrl,license,license_url:licenseUrl
        });
        revision=result.vehicle_revision;added++;setSelected(result.photo.id);
      }
      setNotice(`${added} ${added===1?'photo':'photos'} added.`);setFiles([]);setRights(false);setShowUpload(false);
    }catch(error){
      setFiles(current=>current.slice(added));
      setError(`${added?`${added} saved. `:''}${(error as Error).message}`);
    }finally{await refresh();setUploading(false);}
  }
  function closeUpload(){if(!uploading){setShowUpload(false);setError('');}}
  return <section className="gallery" aria-label="Vehicle photo gallery">
    <div className="gallery-stage">
      {active?<img src={photoUrl(active.id)} alt={active.caption}/>:<div className="photo-empty"><span aria-hidden="true">▧</span><h2>{loading?'Loading photos…':'Give this vehicle a great first impression'}</h2><p>Add exterior, interior and detail photos.</p></div>}
      {active?.illustrative&&<span className="image-label">Stock illustration · not the actual vehicle</span>}
      {active&&<span className="image-counter">{photos.indexOf(active)+1} / {photos.length}</span>}
      {photos.length>1&&<><button className="gallery-arrow previous" aria-label="Previous photo" onClick={()=>setSelected(photos[(photos.indexOf(active)-1+photos.length)%photos.length].id)}>‹</button><button className="gallery-arrow next" aria-label="Next photo" onClick={()=>setSelected(photos[(photos.indexOf(active)+1)%photos.length].id)}>›</button></>}
    </div>
    {!!photos.length&&<div className="thumbnails">{photos.map(photo=><button key={photo.id} className={active?.id===photo.id?'selected':''} aria-label={`View photo ${photos.indexOf(photo)+1}`} aria-pressed={active?.id===photo.id} onClick={()=>setSelected(photo.id)}><img src={photoUrl(photo.id,true)} alt={photo.caption}/>{photo.is_cover&&<span>Cover</span>}</button>)}</div>}
    {active&&<div className="gallery-caption"><p>{active.caption}</p><PhotoCredit photo={active}/></div>}
    <div className="gallery-actions"><span>{photos.length} of 12 photos</span>{canWrite&&<><button className="secondary" onClick={()=>{setError('');setShowUpload(true);}} disabled={photos.length>=12}>＋ Add photos</button>{active&&!active.is_cover&&<button className="secondary" disabled={uploading} onClick={setCover}>Make cover photo</button>}</>}</div>
    <p role="status" className="notice">{notice}</p>{error&&!showUpload&&<p role="alert" className="error">{error}</p>}
    {showUpload&&<dialog ref={dialog} className="upload-dialog" onCancel={event=>{if(uploading)event.preventDefault();else closeUpload();}} onClose={closeUpload}>
      <form onSubmit={upload}><div className="section-heading"><h2>Add vehicle photos</h2><button className="icon-button" type="button" aria-label="Close photo upload" disabled={uploading} onClick={closeUpload}>×</button></div>
        <p>Choose exterior, interior or detail shots. JPEG, PNG or WebP · 2 MB each · up to 12 per vehicle.</p>
        <label className="file-drop">Choose images<input type="file" multiple accept="image/jpeg,image/png,image/webp" onChange={event=>{setFiles(Array.from(event.target.files||[]));setError('');}} disabled={uploading}/><span>You can select more than one image.</span></label>
        {!!files.length&&<ul className="file-list">{files.map((file,index)=><li key={`${index}-${file.name}`}>{file.name}<span>{(file.size/1024).toFixed(0)} KB</span></li>)}</ul>}
        <label>Photo description<input value={caption} onChange={event=>setCaption(event.target.value)} maxLength={160} required disabled={uploading}/></label>
        <details className="credit-fields"><summary>Photo credit and source (optional)</summary>
          <label>Photographer / credit<input value={credit} onChange={event=>setCredit(event.target.value)} maxLength={200} disabled={uploading}/></label>
          <label>Source link<input type="url" value={sourceUrl} onChange={event=>setSourceUrl(event.target.value)} maxLength={1000} placeholder="https://…" disabled={uploading}/></label>
          <div className="form-row"><label>Photo licence<input value={license} onChange={event=>setLicense(event.target.value)} maxLength={100} placeholder="e.g. CC BY-SA 4.0" disabled={uploading}/></label><label>Licence link<input type="url" value={licenseUrl} onChange={event=>setLicenseUrl(event.target.value)} maxLength={1000} placeholder="https://…" disabled={uploading}/></label></div>
        </details>
        <label className="check-label"><input type="checkbox" checked={illustrative} onChange={event=>setIllustrative(event.target.checked)} disabled={uploading}/>These photos are illustrations, not this exact stock vehicle.</label>
        <label className="check-label"><input type="checkbox" checked={rights} onChange={event=>setRights(event.target.checked)} required disabled={uploading}/>I own these photos or have permission to use them.</label>
        {error&&<p role="alert" className="error">{error}</p>}
        <div className="dialog-actions"><button type="button" className="secondary" onClick={closeUpload} disabled={uploading}>Cancel</button><button disabled={uploading||!files.length||!rights}>{uploading?'Uploading…':`Upload ${files.length||''} ${files.length===1?'photo':'photos'}`}</button></div>
        <small>Location and camera metadata are removed before photos are stored.</small>
      </form></dialog>}
  </section>;
}
