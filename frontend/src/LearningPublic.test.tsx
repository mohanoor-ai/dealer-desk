import {afterEach,expect,test,vi} from 'vitest';
import {cleanup,render,screen} from '@testing-library/react';
import LearningPublic,{articles,reference} from './LearningPublic';
import {routeFromHash} from './navigation';
import App from './App';
afterEach(()=>{cleanup();vi.unstubAllGlobals();window.location.hash='';});
test('all fourteen direct article routes render their authored text and bundled images',()=>{
 expect(articles).toHaveLength(14);expect(new Set(articles.map(a=>a.slug)).size).toBe(14);
 for(const article of articles){
  const route=routeFromHash(`#/learning/${article.slug}`);
  expect(route.page).toBe('learning');expect(route.articleSlug).toBe(article.slug);
  const {container}=render(<LearningPublic slug={route.articleSlug}/>);
  expect(screen.getByRole('heading',{level:1,name:article.title})).toBeInTheDocument();
  expect(screen.getByLabelText('Article hashtags')).toHaveTextContent('#aidevtools');
  expect(screen.getByRole('link',{name:'DataTalks.Club'})).toHaveAttribute('href','https://datatalks.club/');
  for(const image of container.querySelectorAll('img'))expect(image.src).not.toContain('github.com');
  cleanup();
 }
});
test('index links stay on the current origin and unknown posts have a recovery path',()=>{
 render(<LearningPublic slug=""/>);
 for(const article of articles)expect(screen.getByRole('link',{name:article.title})).toHaveAttribute('href',`#/learning/${article.slug}`);
 cleanup();render(<LearningPublic slug="not-a-post"/>);
 expect(screen.getByRole('heading',{name:'Article not found'})).toBeInTheDocument();
 expect(screen.getByRole('link',{name:'Browse all fourteen articles'})).toHaveAttribute('href','#/learning');
 expect(reference('javascript:alert(1)')).toBeUndefined();expect(reference('//untrusted.test')).toBeUndefined();
 expect(reference('01-building-dealer-desk.md')).toBe('#/learning/building-dealer-desk');
});
test('article deep links render without a staff session and never request GitHub content',async()=>{
 window.location.hash='#/learning/mobile-navigation';
 const fetcher=vi.fn().mockResolvedValue({ok:false,status:401,json:async()=>({error:{message:'Please sign in.'}})});
 vi.stubGlobal('fetch',fetcher);render(<App/>);
 expect(await screen.findByRole('heading',{level:1,name:'Replacing scrolling menus on a phone'})).toBeInTheDocument();
 expect(screen.queryByRole('button',{name:'Sign in'})).not.toBeInTheDocument();
 expect(fetcher.mock.calls.every(([url])=>String(url)==='/api/auth/me')).toBe(true);
 expect(screen.getByRole('navigation',{name:'Article navigation'})).toBeInTheDocument();
});
