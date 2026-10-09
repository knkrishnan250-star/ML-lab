import React,{useState} from 'react'
import {createRoot} from 'react-dom/client'
import {BarChart,Bar,XAxis,YAxis,Tooltip,ResponsiveContainer} from 'recharts'
import './style.css'
const API='http://127.0.0.1:8000'
function App(){
 const [token,setToken]=useState(localStorage.getItem('token')), [login,setLogin]=useState(true)
 const [username,setUsername]=useState(''),[password,setPassword]=useState(''),[file,setFile]=useState(null)
 const [target,setTarget]=useState(''),[task,setTask]=useState('classification'),[result,setResult]=useState(null),[history,setHistory]=useState([]),[error,setError]=useState('')
 async function auth(register=false){
  const fd=new FormData();fd.append('username',username);fd.append('password',password)
  const r=await fetch(API+'/api/auth/'+(register?'register':'login'),{method:'POST',body:fd});const j=await r.json()
  if(!r.ok)return setError(j.detail||'Authentication failed')
  if(!register){localStorage.setItem('token',j.access_token);setToken(j.access_token)}else setError('Registered. Now login.')
 }
 async function run(){
  const fd=new FormData();fd.append('file',file);fd.append('target',target);fd.append('task',task)
  const r=await fetch(API+'/api/experiment',{method:'POST',headers:{Authorization:'Bearer '+token},body:fd});const j=await r.json()
  if(!r.ok)return setError(j.detail||'Experiment failed');setResult(j);load()
 }
 async function load(){const r=await fetch(API+'/api/history',{headers:{Authorization:'Bearer '+token}});if(r.ok)setHistory(await r.json())}
 if(!token)return <main><div className="auth card"><span className="eyebrow">ML EXPERIMENT LAB V5</span><h1>Research-grade ML workspace.</h1><input placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)}/><input type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)}/><button onClick={()=>auth()}>LOGIN</button><button className="ghost" onClick={()=>auth(true)}>CREATE ACCOUNT</button><p>{error}</p></div></main>
 return <main><header><div><span className="eyebrow">ML PLATFORM / V5</span><h1>ML Experiment Lab</h1><p>Experiments, explainability, registry and tracking.</p></div><button className="ghost" onClick={()=>{localStorage.clear();setToken(null)}}>LOG OUT</button></header>
 <section className="grid"><div className="card"><h2>New experiment</h2><input type="file" accept=".csv" onChange={e=>setFile(e.target.files[0])}/><input placeholder="Target column" value={target} onChange={e=>setTarget(e.target.value)}/><select value={task} onChange={e=>setTask(e.target.value)}><option>classification</option><option>regression</option></select><button onClick={run}>RUN EXPERIMENT</button><p>{error}</p></div>
 <div className="card"><h2>Result</h2>{result?<><div className="score">{result.score.toFixed(4)}</div><b>{result.metric} · {result.model}</b><p>Registry: {result.registry_stage}</p><a href={API+'/api/models/'+result.model_file+'?token='+token}>Model artifact</a></>:<p className="muted">No experiment yet.</p>}</div></section>
 {result&&<section className="card"><h2>Explainability</h2><ResponsiveContainer width="100%" height={300}><BarChart data={result.importance}><XAxis dataKey="feature"/><YAxis/><Tooltip/><Bar dataKey="importance"/></BarChart></ResponsiveContainer></section>}
 <section className="card"><h2>Experiment history</h2><button className="ghost" onClick={load}>REFRESH</button><table><thead><tr><th>ID</th><th>Model</th><th>Task</th><th>Metric</th><th>Score</th></tr></thead><tbody>{history.map(x=><tr key={x.id}><td>{x.id}</td><td>{x.model}</td><td>{x.task}</td><td>{x.metric}</td><td>{x.score?.toFixed(4)}</td></tr>)}</tbody></table></section></main>
}
createRoot(document.getElementById('root')).render(<App/>)
