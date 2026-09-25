import {useState} from 'react';

type Item={id:number,sku:string,name:string,category:string,quantity:number,reorder_level:number,location?:string};
type Ticket={id:number,title:string,priority:string,status:string,requester_id:number,assignee_id?:number};

const demoItems:Item[]=[
 {id:1,sku:'LT-001',name:'Dell Latitude Laptop',category:'IT Equipment',quantity:14,reorder_level:5,location:'Berlin Office'},
 {id:2,sku:'HD-014',name:'USB-C Dock',category:'IT Equipment',quantity:3,reorder_level:6,location:'Berlin Office'},
 {id:3,sku:'HS-021',name:'Jabra Headset',category:'Accessories',quantity:8,reorder_level:4,location:'Storage A'}
];
const demoTickets:Ticket[]=[
 {id:1042,title:'VPN access not working',priority:'high',status:'in_progress',requester_id:3,assignee_id:2},
 {id:1043,title:'Replacement laptop required',priority:'medium',status:'open',requester_id:3},
 {id:1044,title:'Payment terminal issue',priority:'critical',status:'open',requester_id:3,assignee_id:2}
];

export default function App(){
 const[tab,setTab]=useState<'inventory'|'tickets'>('inventory');
 return <div className="shell">
   <header><div><div className="eyebrow">INTERNAL COMPANY TOOL</div><h1>Operations Portal</h1><p>Inventory and employee helpdesk management.</p></div><div className="user">Arpit Admin · Admin</div></header>
   <div className="grid stats"><div className="card"><span>Inventory items</span><b>3</b></div><div className="card"><span>Low stock</span><b>1</b></div><div className="card"><span>Open tickets</span><b>3</b></div><div className="card"><span>Critical tickets</span><b>1</b></div></div>
   <nav><button className={tab==='inventory'?'active':''} onClick={()=>setTab('inventory')}>Inventory</button><button className={tab==='tickets'?'active':''} onClick={()=>setTab('tickets')}>Helpdesk Tickets</button></nav>
   {tab==='inventory'?<section className="card"><div className="sectionTitle"><h2>Inventory Management</h2><button>+ Add item</button></div><table><thead><tr><th>SKU</th><th>Item</th><th>Category</th><th>Qty</th><th>Reorder</th><th>Location</th></tr></thead><tbody>{demoItems.map(x=><tr key={x.id}><td>{x.sku}</td><td>{x.name}</td><td>{x.category}</td><td><span className={x.quantity<=x.reorder_level?'badge danger':'badge'}>{x.quantity}</span></td><td>{x.reorder_level}</td><td>{x.location}</td></tr>)}</tbody></table></section>:<section className="card"><div className="sectionTitle"><h2>Helpdesk / Tickets</h2><button>+ New ticket</button></div><table><thead><tr><th>ID</th><th>Title</th><th>Priority</th><th>Status</th><th>Assignee</th></tr></thead><tbody>{demoTickets.map(x=><tr key={x.id}><td>#{x.id}</td><td>{x.title}</td><td><span className={'badge '+(x.priority==='critical'?'danger':'')}>{x.priority}</span></td><td>{x.status.replace('_',' ')}</td><td>{x.assignee_id?'Mia Support':'Unassigned'}</td></tr>)}</tbody></table></section>}
 </div>
}
