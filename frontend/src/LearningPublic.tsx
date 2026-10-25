import {useEffect} from 'react';
import type {ReactNode} from 'react';
import overview from '../../docs/media/dealer-overview.png';
import workflow from '../../docs/media/enquiry-workflow.png';
import mobile from '../../docs/media/mobile-navigation.jpg';
import conflict from '../../docs/evidence/two-session-conflict.png';
import telemetry from '../../docs/evidence/operations-correlation.png';

const sources=import.meta.glob<string>('../../docs/articles/[0-9][0-9]-*.md',{query:'?raw',import:'default',eager:true});
export const articles=Object.entries(sources).sort(([a],[b])=>a.localeCompare(b)).map(([path,markdown])=>{
 const file=path.split('/').pop()!;
 const paragraphs=markdown.trim().split(/\r?\n\s*\r?\n/);
 return {file,slug:file.replace(/^\d+-/,'').replace(/\.md$/,''),title:paragraphs[0].replace(/^# /,''),summary:paragraphs[2].replace(/`/g,''),markdown};
});
const pictures:Record<string,string>={'../media/dealer-overview.png':overview,'../media/enquiry-workflow.png':workflow,'../media/mobile-navigation.jpg':mobile,'../evidence/two-session-conflict.png':conflict,'../evidence/operations-correlation.png':telemetry};
export function reference(href:string):string|undefined{
 if(/^https?:\/\//.test(href))return href;
 if(/^[a-z][a-z0-9+.-]*:/i.test(href)||href.startsWith('//'))return undefined;
 const file=href.split('/').pop();
 const article=articles.find(a=>a.file===file);
 if(article)return `#/learning/${article.slug}`;
 return new URL(href,'https://github.com/mohanoor-ai/dealer-desk/blob/main/docs/articles/').href;
}
function inline(text:string):ReactNode[]{
 return text.split(/(\[[^\]]+\]\([^)]+\)|`[^`]+`)/g).map((part,i)=>{
  const link=part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
  if(link){const href=reference(link[2]);return href?<a href={href} key={i}>{link[1]}</a>:<span key={i}>{link[1]}</span>;}
  return part.startsWith('`')&&part.endsWith('`')?<code key={i}>{part.slice(1,-1)}</code>:part;
 });
}
function Content({markdown}:{markdown:string}){
 return <>{markdown.trim().split(/\r?\n\s*\r?\n/).map((block,i)=>{
  const image=block.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
  if(image)return <figure key={i}>{pictures[image[2]]?<a href={pictures[image[2]]}><img src={pictures[image[2]]} alt={image[1]} loading="lazy"/></a>:null}<figcaption>{image[1]}</figcaption></figure>;
  if(block.startsWith('# '))return <h1 key={i}>{inline(block.slice(2))}</h1>;
  if(block.startsWith('## '))return <h2 key={i}>{inline(block.slice(3))}</h2>;
  if(block.startsWith('#aidevtools'))return <p className="article-tags" aria-label="Article hashtags" key={i}>{block.split(/\s+/).map(tag=><span key={tag}>{tag}</span>)}</p>;
  return <p key={i}>{inline(block)}</p>;
 })}</>;
}
export default function LearningPublic({slug}:{slug:string}){
 const article=articles.find(a=>a.slug===slug);
 useEffect(()=>{document.title=article?`${article.title} | Dealer Desk`:'Learning in public | Dealer Desk';return()=>{document.title='Dealer Desk';};},[article]);
 if(!slug)return <section className="learning-index"><p className="eyebrow">PROJECT JOURNAL</p><h1>Learning in public</h1><p className="learning-intro">Fourteen articles by Mohammed Sheikh-Noor about building, testing and operating Dealer Desk during AI Dev Tools Zoomcamp. Examples and checks come from this project.</p><div className="article-grid">{articles.map((a,i)=><article className="panel article-card" key={a.slug}><span className="eyebrow">{String(i+1).padStart(2,'0')} / PROJECT ARTICLE</span><h2><a href={`#/learning/${a.slug}`}>{a.title}</a></h2><p>{a.summary.slice(0,190)}{a.summary.length>190?'…':''}</p><small>Mohammed Sheikh-Noor · 25 October 2026</small><a className="article-read" href={`#/learning/${a.slug}`}>Read article →</a></article>)}</div><p className="article-tags"><span>#aidevtools</span><span>#DataTalksClub</span><span>#BuildInPublic</span></p></section>;
 if(!article)return <section className="public-copy panel"><h1>Article not found</h1><p>This article address does not match a published post.</p><a href="#/learning">Browse all fourteen articles</a></section>;
 const next=articles[(articles.indexOf(article)+1)%articles.length];
 return <section className="learning-detail"><nav aria-label="Article navigation"><a href="#/learning">← All articles</a></nav><article className="article-content"><Content markdown={article.markdown}/></article><aside className="article-next"><p>Next article</p><a href={`#/learning/${next.slug}`}>{next.title} →</a></aside></section>;
}
