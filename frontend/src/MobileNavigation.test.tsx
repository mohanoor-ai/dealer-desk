import {afterEach,beforeEach,expect,test,vi} from 'vitest';
import {render,screen,fireEvent,cleanup,within} from '@testing-library/react';
import MobileNavigation from './MobileNavigation';
const proto=HTMLDialogElement.prototype;
const originalShow=Object.getOwnPropertyDescriptor(proto,'showModal'),originalClose=Object.getOwnPropertyDescriptor(proto,'close');
beforeEach(()=>{
 Object.defineProperty(proto,'showModal',{configurable:true,value:function(this:HTMLDialogElement){this.setAttribute('open','');}});
 Object.defineProperty(proto,'close',{configurable:true,value:function(this:HTMLDialogElement){this.removeAttribute('open');this.dispatchEvent(new Event('close'));}});
});
afterEach(()=>{cleanup();for(const [name,value] of [['showModal',originalShow],['close',originalClose]] as const){if(value)Object.defineProperty(proto,name,value);else delete (proto as unknown as Record<string,unknown>)[name];}});
const items=[{label:'Home',href:'#/home'},{label:'Vehicles',href:'#/catalogue',current:true},{label:'Staff sign in',href:'#/login'}];
test('top and bottom controls open one vertical menu and restore focus on close',()=>{
 render(<MobileNavigation items={items} routeKey="#/catalogue" staff={false}/>);
 const top=screen.getByRole('button',{name:'Open navigation'}),bottom=screen.getByRole('button',{name:'Open bottom navigation'});
 expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
 top.focus();fireEvent.click(top);
 let menu=screen.getByRole('dialog',{name:'Menu'});
 expect(top).toHaveAttribute('aria-expanded','true');expect(bottom).toHaveAttribute('aria-expanded','true');
 expect(within(menu).getByRole('link',{name:'Vehicles'})).toHaveAttribute('aria-current','page');
 fireEvent.click(within(menu).getByRole('button',{name:'Close navigation'}));
 expect(top).toHaveFocus();expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
 bottom.focus();fireEvent.click(bottom);menu=screen.getByRole('dialog');expect(menu).toHaveAttribute('data-origin','bottom');
 fireEvent(menu,new Event('cancel',{bubbles:false,cancelable:true}));
 expect(bottom).toHaveFocus();expect(bottom).toHaveAttribute('aria-expanded','false');
});
test('menu closes for link selection, external route changes and staff sign-out',()=>{
 const logout=vi.fn().mockResolvedValue(undefined);
 const {rerender}=render(<MobileNavigation items={[{label:'Enquiries',href:'#/enquiries'}]} routeKey="#/overview" staff onLogout={logout}/>);
 fireEvent.click(screen.getByRole('button',{name:'Open navigation'}));
 let menu=screen.getByRole('dialog',{name:'Staff navigation'});expect(within(menu).queryByRole('link',{name:'Staff sign in'})).not.toBeInTheDocument();
 fireEvent.click(within(menu).getByRole('link',{name:'Enquiries'}));expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Open bottom navigation'}));
 rerender(<MobileNavigation items={items} routeKey="#/enquiries" staff onLogout={logout}/>);expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Open navigation'}));menu=screen.getByRole('dialog');
 fireEvent.click(within(menu).getByRole('button',{name:'Sign out'}));expect(logout).toHaveBeenCalledTimes(1);expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
});
