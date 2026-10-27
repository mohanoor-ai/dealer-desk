export type Status = 'available' | 'reserved' | 'sold';
export type Photo = {id:number;vehicle_id:number;caption:string;credit:string;source_url:string;license:string;license_url:string;illustrative:boolean;is_cover:boolean;width:number;height:number;created_at:string};
export type Vehicle = {id:number;make:string;model:string;year:number;price_pence:number;approved_facts:string[];status:Status;archived:boolean;revision:number;created_at:string;updated_at:string;cover_photo_id?:number|null;photo_count?:number;cover_photo?:Photo|null};
export type Enquiry = {id:number;vehicle_id:number|null;customer_linked?:boolean;source?:string;request_type?:string;email?:string;phone?:string;activity?:{kind:string;at:string;actor:string;subject?:string;body?:string;outcome?:string}[];closure_reason?:string;customer:string;message:string;status:'new'|'contacted'|'closed';revision:number;created_at:string;updated_at:string};
export type Task = {id:number;enquiry_id:number;due_date:string;note:string;completed:boolean;revision:number;created_at:string;updated_at:string};
export type Page<T> = {items:T[];total:number;offset:number;limit:number};
export type Snapshot = {vehicles:Vehicle[];enquiries:Enquiry[];tasks:Task[]};
