import React,{useEffect,useMemo,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Activity,ArrowUpRight,BookOpen,BrainCircuit,CalendarCheck,ChevronRight,ClipboardCheck,CloudUpload,GraduationCap,LayoutDashboard,LogOut,Menu,MessageCircle,Moon,PanelLeft,Search,ShieldCheck,Sparkles,Sun,Target,TrendingUp,Upload,UserRound,Users, X, CheckCircle2, AlertCircle, Loader2} from 'lucide-react';
import {api,login,logout} from './services/api';
import './styles.css';

const fmt=(v,f='—')=>v===null||v===undefined||v===''?f:v;
const pct=(v)=>v===null||v===undefined||v===''?'—':Number.isFinite(Number(v))?`${Number(v).toFixed(1)}%`:'—';
const initials=(name='User')=>name.split(/\s+/).map(x=>x[0]).slice(0,2).join('').toUpperCase();

function Login({onLogin}){const [u,setU]=useState(''),[p,setP]=useState(''),[busy,setBusy]=useState(false),[err,setErr]=useState('');
 const submit=async e=>{e.preventDefault();setBusy(true);setErr('');try{const data=await login(u,p);localStorage.setItem('edunexus_token',data.access_token);localStorage.setItem('edunexus_user',JSON.stringify(data));onLogin(data)}catch(x){setErr(x.message)}finally{setBusy(false)}};
 return <div className="login-shell"><div className="login-orbit o1"/><div className="login-orbit o2"/><div className="login-card"><div className="brand-mark"><div className="brand-icon">E</div><div><b>EduNexus</b><span>Academic Intelligence</span></div></div><div className="login-copy"><span className="eyebrow"><Sparkles size={14}/> THE CAMPUS INTELLIGENCE LAYER</span><h1>Everything academic.<br/><em>One intelligent space.</em></h1><p>Connect learning, faculty operations, resources and student success in one calm, intelligent workspace.</p></div><form onSubmit={submit}><label>Username<input value={u} onChange={e=>setU(e.target.value)} autoComplete="username"/></label><label>Password<input type="password" value={p} onChange={e=>setP(e.target.value)} autoComplete="current-password"/></label>{err&&<div className="error"><AlertCircle size={15}/>{err}</div>}<button className="primary wide" disabled={busy}>{busy?<Loader2 className="spin" size={18}/>:<ArrowUpRight size={18}/>}Sign in to EduNexus</button></form><div className="login-hint"><ShieldCheck size={15}/> Secure role-based access • Student, Faculty & Admin</div></div><div className="login-mascot"><img src="/aadhi-3d.png"/><div className="mascot-caption"><b>Aadhi</b><span>Your campus companion</span></div></div></div>}

function Shell({user,tab,setTab,children,onLogout}){const [dark,setDark]=useState(true),[mobile,setMobile]=useState(false);const nav=user.role==='FACULTY'?[['home','Overview',LayoutDashboard],['attendance','Smart Attendance',CalendarCheck],['marks','Smart Marks',ClipboardCheck],['resources','Resources',CloudUpload],['insights','Class Intelligence',TrendingUp],['mentor','Mentor Requests',MessageCircle],['reviews','Achievement Reviews',Target],['notifications','Notifications',Activity]]:user.role==='ADMIN'?[['home','Admin Overview',LayoutDashboard],['students','Student Records',Users]]:[['home','Overview',LayoutDashboard],['academics','Academics',BookOpen],['attendance','Attendance',CalendarCheck],['resources','Resources',CloudUpload],['achievements','SkillFolio',Target],['mentor','Mentor Support',MessageCircle],['notifications','Notifications',Activity]];
 return <div className={dark?'app dark':'app'}><aside className={mobile?'sidebar open':'sidebar'}><div className="side-brand"><div className="brand-icon">E</div><div><b>EduNexus</b><small>Academic OS</small></div><button className="icon-btn mobile-close" onClick={()=>setMobile(false)}><X/></button></div><div className="role-pill"><span className="live-dot"/> {user.role==='FACULTY'?'Faculty workspace':user.role==='ADMIN'?'Admin workspace':'Student workspace'}</div><nav>{nav.map(([id,label,I])=><button key={id} className={tab===id?'nav active':'nav'} onClick={()=>{setTab(id);setMobile(false)}}><I size={18}/><span>{label}</span>{tab===id&&<ChevronRight size={15}/>}</button>)}</nav><div className="side-bottom"><button className="nav" onClick={()=>setDark(!dark)}>{dark?<Sun size={18}/>:<Moon size={18}/>}<span>{dark?'Light mode':'Dark mode'}</span></button><button className="nav logout" onClick={onLogout}><LogOut size={18}/><span>Sign out</span></button></div></aside><main className="main"><header className="topbar"><button className="icon-btn menu-btn" onClick={()=>setMobile(true)}><Menu/></button><div className="crumb"><span>EduNexus</span><ChevronRight size={14}/><b>{nav.find(x=>x[0]===tab)?.[1]}</b></div><div className="top-actions"><div className="search"><Search size={16}/><input placeholder="Search your campus..."/></div><div className="avatar">{initials(user.username)}</div></div></header><section className="content">{children}</section></main><Aadhi/></div>}

function Stat({label,value,sub,icon:Icon,tone=''}){return <div className="stat"><div className={`stat-icon ${tone}`}><Icon size={18}/></div><div><span>{label}</span><strong>{fmt(value)}</strong><small>{sub}</small></div></div>}
function Section({title,meta,children,action}){return <section className="panel"><div className="panel-head"><div><h3>{title}</h3>{meta&&<span>{meta}</span>}</div>{action}</div>{children}</section>}
function Empty({text}){return <div className="empty"><Sparkles size={20}/><span>{text}</span></div>}

function Student({tab}){const [data,setData]=useState(null),[marks,setMarks]=useState(null),[att,setAtt]=useState(null),[results,setResults]=useState(null),[resources,setResources]=useState(null),[ach,setAch]=useState(null),[err,setErr]=useState('');useEffect(()=>{(async()=>{try{const [d,m,a,r,rs,ac]=await Promise.all([api('/student/dashboard'),api('/student/marks'),api('/student/attendance'),api('/student/results'),api('/student/resources'),api('/student/achievements')]);setData(d);setMarks(m);setAtt(a);setResults(r);setResources(rs);setAch(ac)}catch(e){setErr(e.message)}})()},[]);
 const subjectRows=useMemo(()=>Array.isArray(marks)?marks:(marks?.marks||marks?.subjects||marks?.records||[]),[marks]);
 const attendanceRows=useMemo(()=>Array.isArray(att)?att:(att?.attendance||att?.subjects||att?.records||[]),[att]);
 const displayName=data?.student?.name||'Student'; const cgpa=data?.academic?.cgpa; const overall=data?.attendance?.percentage;
 if(err&&!data)return <ErrorState error={err}/>;
 return <><PageHero kicker="STUDENT INTELLIGENCE" title={`Good morning, ${displayName}.`} text="Your academic life, organized around what matters next." icon={GraduationCap}/><div className="stats"><Stat label="Overall attendance" value={pct(overall)} sub="Across recorded sessions" icon={CalendarCheck} tone="violet"/><Stat label="CGPA" value={fmt(cgpa)} sub="Latest available result" icon={GraduationCap} tone="gold"/><Stat label="Current Subjects" value={fmt(data?.statistics?.subject_count??data?.current_semester_subjects?.length??0)} sub="Current semester subjects" icon={BookOpen} tone="blue"/><Stat label="Achievements" value={fmt(data?.statistics?.achievements??(Array.isArray(ach)?ach.length:(ach?.achievements?.length??ach?.items?.length)))} sub="In your SkillFolio" icon={Target} tone="green"/></div>
 {tab==='home'&&<div className="grid-2"><Section title="Academic pulse" meta="Your latest academic signals"><Pulse data={data}/></Section><Section title="Ask Aadhi" meta="Your campus companion"><AadhiCard/></Section><Section title="Recent marks" meta="Latest records"><MarkTable rows={subjectRows.slice(0,5)}/></Section><Section title="Attendance snapshot" meta="Subject-level view"><AttendanceTable rows={attendanceRows.slice(0,5)}/></Section></div>}
 {tab==='academics'&&<div className="stack"><Section title="Marks & results" meta="All available academic records"><MarkTable rows={subjectRows}/></Section><Section title="Semester results"><ResultTable rows={Array.isArray(results)?results:(results?.results||[])} /></Section></div>}
 {tab==='attendance'&&<Section title="Attendance" meta="Recorded attendance"><AttendanceTable rows={attendanceRows}/></Section>}
 {tab==='resources'&&<Section title="Learning resources" meta="Faculty-shared resources"><ResourceGrid rows={Array.isArray(resources)?resources:(resources?.resources||[])} /></Section>}
 {tab==='achievements'&&<div className="stack"><Section title="Add an achievement" meta="Submissions are reviewed by faculty"><AchievementForm onDone={()=>api('/student/achievements').then(setAch)}/></Section><Section title="SkillFolio" meta="Your academic & co-curricular story"><AchievementGrid rows={ach?.achievements||[]} /></Section></div>}
 {tab==='mentor'&&<MentorStudent/>}{tab==='notifications'&&<NotificationsPage/>}
 </>}

function FacultyDashboard(){const [subjects,setSubjects]=useState([]),[subject,setSubject]=useState(''),[section,setSection]=useState('A'),[data,setData]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState('');useEffect(()=>{api('/faculty/subjects').then(x=>setSubjects(x.subjects||[])).catch(e=>setError(e.message))},[]);const load=async()=>{if(!subject)return;setBusy(true);setError('');try{setData(await api('/faculty/class-intelligence?subject_id='+subject+'&section='+section))}catch(e){setError(e.message)}finally{setBusy(false)}};return <><PageHero kicker="FACULTY OPERATIONS" title="Your teaching workspace." text="Review requests, manage academic operations, and monitor class progress." icon={Users}/><Section title="Class dashboard" meta="Student roster with attendance and marks for the selected class"><div className="form-grid"><select value={subject} onChange={e=>setSubject(e.target.value)}><option value="">Choose subject</option>{subjects.map(x=><option key={x.id} value={x.id}>{x.code} · {x.name}</option>)}</select><select value={section} onChange={e=>setSection(e.target.value)}><option value="A">Section A</option><option value="B">Section B</option></select><button className="primary" disabled={!subject||busy} onClick={load}>{busy?'Loading students…':'Show student details'}</button></div>{error&&<div className="toast">{error}</div>}{data&&<><div className="stats"><Stat label="Students" value={data.student_count} sub={data.subject+' · Section '+data.section} icon={Users}/><Stat label="Class attendance" value={data.attendance_average==null?'No records':data.attendance_average+'%'} sub="Recorded sessions" icon={CalendarCheck}/><Stat label="Class assessment" value={data.assessment_average==null?'No records':data.assessment_average+'%'} sub="Across recorded marks" icon={ClipboardCheck}/></div>{data.students?.length?<div className="table-wrap"><table><thead><tr><th>Student ID</th><th>Student name</th><th>Attendance</th><th>Average marks</th><th>Follow-up</th></tr></thead><tbody>{data.students.map(x=><tr key={x.register_number}><td>{x.register_number}</td><td>{x.student}</td><td>{x.attendance==null?'No records':x.attendance+'%'}</td><td>{x.average_marks==null?'No records':x.average_marks+'%'}</td><td>{x.attention==='REVIEW'?'Review':'On track'}</td></tr>)}</tbody></table></div>:<Empty text="No students are enrolled in this subject and section."/>}</>}</Section><div className="stats"><Stat label="Academic workflows" value="Attendance & marks" sub="Manual and AI-assisted entry" icon={BrainCircuit} tone="violet"/><Stat label="Safety gate" value="Human review" sub="Confirm before each academic write" icon={ShieldCheck} tone="green"/><Stat label="Student support" value="Requests & reviews" sub="Available in the support navigation" icon={MessageCircle} tone="blue"/></div></>}
function Faculty({tab}){const [parse,setParse]=useState(''),[parsed,setParsed]=useState(null),[validation,setValidation]=useState(null),[busy,setBusy]=useState(false),[type,setType]=useState('attendance'),[msg,setMsg]=useState('');useEffect(()=>{setType(tab==='marks'?'marks':'attendance');setParsed(null);setValidation(null)},[tab]);
 const parseIt=async()=>{setBusy(true);setMsg('');setValidation(null);try{const r=await api(`/faculty/${type}/parse`,{method:'POST',body:JSON.stringify({text:parse})});setParsed(r);setMsg('AI interpretation ready. Review before saving.')}catch(e){setMsg(e.message)}finally{setBusy(false)}};
 const validate=async()=>{setBusy(true);setMsg('');try{let body;if(type==='attendance'){const a=parsed?.attendance||parsed?.data||parsed;body={attendance:{subject_code:a.subject_code,date:a.date||new Date().toISOString().slice(0,10),period:a.period,section:a.section,absent_student_ids:a.absent_student_ids||[]}}}else{const m=parsed?.marks||parsed?.data||parsed;body={marks:{subject_code:m.subject_code,assessment_name:m.assessment_name,marks:Object.fromEntries((m.records||[]).map(x=>[x.register_number,x.marks]))}}}const r=await api(`/faculty/${type}/validate`,{method:'POST',body:JSON.stringify(body)});setValidation(r);setMsg(r.status==='READY_FOR_CONFIRMATION'?'Validation passed. Nothing is saved yet.':'Validation needs attention.')}catch(e){setMsg(e.message)}finally{setBusy(false)}};
 const confirm=async()=>{if(!validation||validation.status!=='READY_FOR_CONFIRMATION')return;setBusy(true);try{let body;if(type==='attendance'){const a=parsed?.attendance||parsed?.data||parsed;body={attendance:{subject_code:a.subject_code,date:a.date||new Date().toISOString().slice(0,10),period:a.period,section:a.section,absent_student_ids:a.absent_student_ids||[]}}}else{const m=parsed?.marks||parsed?.data||parsed;body={marks:{subject_code:m.subject_code,assessment_name:m.assessment_name,marks:Object.fromEntries((m.records||[]).map(x=>[x.register_number,x.marks]))}}}const r=await api(`/faculty/${type}/confirm`,{method:'POST',body:JSON.stringify(body)});setMsg(r.message||'Committed successfully.');setParsed(null);setValidation(null);setParse('')}catch(e){setMsg(e.message)}finally{setBusy(false)}};
 if(tab==='mentor'||tab==='reviews'||tab==='resources'||tab==='insights')return <FacultyAux tab={tab}/>;
 if(tab==='notifications')return <NotificationsPage/>;
 if(tab==='home')return <FacultyDashboard/>
 return <><PageHero kicker="FACULTY OPERATIONS" title="Move from busywork to intelligent workflows." text="Interpret natural language, validate against academic records, then approve the transaction." icon={Users}/>{tab==='home'&&<div className="stats"><Stat label="Operations" value="2" sub="AI-assisted workflows" icon={BrainCircuit} tone="violet"/><Stat label="Safety gate" value="HITL" sub="Human approval required" icon={ShieldCheck} tone="green"/><Stat label="Attendance" value="Ready" sub="Parse → validate → confirm" icon={CalendarCheck} tone="blue"/><Stat label="Marks" value="Ready" sub="Interpret → validate → commit" icon={ClipboardCheck} tone="gold"/></div>}<FacultyManual/>{tab==='marks'&&<BulkMarksUpload/>}<div className="workflow-switch"><button className={type==='attendance'?'selected':''} onClick={()=>{setType('attendance');setParsed(null);setValidation(null)}}><CalendarCheck size={17}/> Smart Attendance</button><button className={type==='marks'?'selected':''} onClick={()=>{setType('marks');setParsed(null);setValidation(null)}}><ClipboardCheck size={17}/> Smart Marks</button></div><div className="workflow-grid"><Section title={type==='attendance'?'Describe the class':'Describe the marks'} meta="Gemini interprets; PostgreSQL validates"><textarea className="ai-input" value={parse} onChange={e=>setParse(e.target.value)} placeholder={type==='attendance'?'Today DBMS period 2 section A. Absent: 2116231401107, 2116231401121...':'For CB23721 Project Evaluation I, maximum marks 100. 2116231401103 scored 82...'} /><button className="primary" onClick={parseIt} disabled={busy||parse.trim().length<3}>{busy?<Loader2 className="spin" size={17}/>:<Sparkles size={17}/>}Interpret with Gemini</button></Section><Section title="AI interpretation" meta="Review before validation"><JsonPreview data={parsed}/>{parsed&&<button className="secondary" onClick={validate} disabled={busy}>{busy?<Loader2 className="spin" size={16}/>:<ShieldCheck size={16}/>}Validate against academic records</button>}</Section></div>{validation&&<Section title="Validation preview" meta="No database write happens until you confirm"><ValidationView data={validation}/>{validation.status==='READY_FOR_CONFIRMATION'&&<button className="primary success" onClick={confirm} disabled={busy}>{busy?<Loader2 className="spin" size={17}/>:<CheckCircle2 size={17}/>}Confirm & save</button>}</Section>}{msg&&<div className={msg.includes('passed')||msg.includes('success')||msg.includes('ready')?'toast good':'toast'}>{msg}</div>}</>}

function FacultyManual(){const [mode,setMode]=useState('attendance'),[subjects,setSubjects]=useState([]),[subject,setSubject]=useState(''),[section,setSection]=useState('A'),[roster,setRoster]=useState([]),[present,setPresent]=useState({}),[assessments,setAssessments]=useState([]),[assessment,setAssessment]=useState(''),[marks,setMarks]=useState({}),[date,setDate]=useState(new Date().toISOString().slice(0,10)),[period,setPeriod]=useState(1),[msg,setMsg]=useState('');useEffect(()=>{api('/faculty/subjects').then(x=>setSubjects(x.subjects||[]))},[]);const choose=async id=>{setSubject(id);setMsg('');const path=mode==='attendance'?`/faculty/subjects/${id}/roster?section=${section}`:`/faculty/subjects/${id}/assessments`;try{const r=await api(path);if(mode==='attendance'){setRoster(r.students||[]);setPresent(Object.fromEntries((r.students||[]).map(s=>[s.register_number,true])))}else{setAssessments(r.assessments||[]);const rr=await api(`/faculty/subjects/${id}/roster?section=${section}`);setRoster(rr.students||[]);setMarks({})}}catch(e){setMsg(e.message)}};const submit=async()=>{try{let r;if(mode==='attendance'){const a={subject_code:subjects.find(s=>String(s.id)===subject)?.code,date,period:Number(period),section,absent_student_ids:roster.filter(s=>!present[s.register_number]).map(s=>s.register_number)};r=await api('/faculty/attendance/manual/confirm',{method:'POST',body:JSON.stringify(a)})}else{r=await api('/faculty/marks/manual/confirm',{method:'POST',body:JSON.stringify({subject_code:subjects.find(s=>String(s.id)===subject)?.code,assessment_name:assessment,marks})})}setMsg(r.status==='COMMITTED'?'Saved and audited.':r.message||r.status||'Request completed.');}catch(e){setMsg(e.message)}};return <Section title="Manual academic entry" meta="Validated and audited by the same server services used for assisted entry"><div className="workflow-switch"><button className={mode==='attendance'?'selected':''} onClick={()=>{setMode('attendance');setSubject('');setRoster([])}}>Manual Attendance</button><button className={mode==='marks'?'selected':''} onClick={()=>{setMode('marks');setSubject('');setAssessments([])}}>Manual Marks</button></div><div className="form-grid"><select value={subject} onChange={e=>choose(e.target.value)}><option value="">Choose subject</option>{subjects.map(s=><option key={s.id} value={s.id}>{s.code} · {s.name}</option>)}</select>{mode==='attendance'&&<><select value={section} onChange={e=>{setSection(e.target.value);if(subject)api(`/faculty/subjects/${subject}/roster?section=${e.target.value}`).then(x=>{setRoster(x.students||[]);setPresent(Object.fromEntries((x.students||[]).map(s=>[s.register_number,true])))} )}}><option>A</option><option>B</option></select><input type="date" value={date} onChange={e=>setDate(e.target.value)}/><input type="number" min="1" max="10" value={period} onChange={e=>setPeriod(e.target.value)}/></>}{mode==='marks'&&<select value={assessment} onChange={e=>setAssessment(e.target.value)}><option value="">Choose assessment</option>{assessments.map(a=><option key={a.id} value={a.name}>{a.name} · max {a.max_marks}</option>)}</select>}</div>{mode==='attendance'&&roster.length>0&&<><div className="actions"><button className="secondary" onClick={()=>setPresent(Object.fromEntries(roster.map(s=>[s.register_number,true])))}>Mark all present</button><button className="secondary" onClick={()=>setPresent(Object.fromEntries(roster.map(s=>[s.register_number,false])))}>Clear all</button><span>{roster.length} students · {Object.values(present).filter(Boolean).length} present · {Object.values(present).filter(x=>!x).length} absent</span></div><div className="table-wrap"><table><thead><tr><th>Register number</th><th>Student</th><th>Department</th><th>Section</th><th>Present</th></tr></thead><tbody>{roster.map(s=><tr key={s.id}><td>{s.register_number}</td><td>{s.name}</td><td>{s.department}</td><td>{s.section}</td><td><label className="attendance-toggle"><input type="checkbox" checked={!!present[s.register_number]} onChange={e=>setPresent({...present,[s.register_number]:e.target.checked})}/><span className="toggle-track"/><b>{present[s.register_number]?'Present':'Absent'}</b></label></td></tr>)}</tbody></table></div></>}{mode==='marks'&&assessments.length>0&&<div className="table-wrap"><table><thead><tr><th>Assessment entry</th><th>Register number</th><th>Name</th><th>Department</th><th>Section</th><th>Marks</th></tr></thead><tbody>{(roster.length?roster:[]).map(s=><tr key={s.id}><td>{assessment}</td><td>{s.register_number}</td><td>{s.name}</td><td>{s.department}</td><td>{s.section}</td><td><input type="number" min="0" value={marks[s.register_number]??''} onChange={e=>setMarks({...marks,[s.register_number]:Number(e.target.value)})}/></td></tr>)}</tbody></table></div>}{(roster.length||mode==='marks'&&assessment)&&<button className="primary" onClick={submit}>Save {mode}</button>}{msg&&<div className="toast">{msg}</div>}</Section>}
function BulkMarksUpload(){const[subjects,setSubjects]=useState([]),[assessments,setAssessments]=useState([]),[subject,setSubject]=useState(''),[assessment,setAssessment]=useState(''),[file,setFile]=useState(null),[preview,setPreview]=useState(null),[busy,setBusy]=useState(false),[msg,setMsg]=useState('');useEffect(()=>{api('/faculty/subjects').then(x=>setSubjects(x.subjects||[]))},[]);const selectSubject=async id=>{setSubject(id);setAssessment('');setPreview(null);if(id){const r=await api(`/faculty/subjects/${id}/assessments`);setAssessments(r.assessments||[])}};const form=()=>{const f=new FormData();f.append('subject_code',subjects.find(s=>String(s.id)===subject)?.code||'');f.append('assessment_name',assessment);if(file)f.append('file',file);return f};const validate=async()=>{setBusy(true);setMsg('');try{setPreview(await api('/faculty/marks/upload/validate',{method:'POST',body:form()}))}catch(e){setMsg(e.message)}finally{setBusy(false)}};const confirm=async()=>{setBusy(true);try{const r=await api('/faculty/marks/upload/confirm',{method:'POST',body:form()});setMsg(r.message||`${r.committed_records||0} marks committed.`);setPreview(null);setFile(null)}catch(e){setMsg(e.message)}finally{setBusy(false)}};return <Section title="CSV / XLSX marks upload" meta="Review validation results before committing"><div className="form-grid"><select value={subject} onChange={e=>selectSubject(e.target.value)}><option value="">Choose subject</option>{subjects.map(s=><option key={s.id} value={s.id}>{s.code} · {s.name}</option>)}</select><select value={assessment} onChange={e=>setAssessment(e.target.value)}><option value="">Choose assessment</option>{assessments.map(a=><option key={a.id} value={a.name}>{a.name} · max {a.max_marks}</option>)}</select><input type="file" accept=".csv,.xlsx" onChange={e=>{setFile(e.target.files[0]);setPreview(null)}}/><button className="secondary" disabled={!file||!assessment||busy} onClick={validate}>{busy?'Validating…':'Validate and preview'}</button></div>{preview&&<div className="validation"><div><b>{preview.status}</b>{(preview.errors||[]).map((e,i)=><p key={i}>{e}</p>)}{(preview.warnings||[]).map((e,i)=><p key={i}>{e}</p>)}<pre>{JSON.stringify(preview.preview,null,2)}</pre></div></div>}{preview?.status==='READY_FOR_CONFIRMATION'&&<button className="primary success" disabled={busy} onClick={confirm}>Confirm and commit upload</button>}{msg&&<div className="toast">{msg}</div>}</Section>}
function PageHero({kicker,title,text,icon:Icon}){return <div className="hero-card"><div className="hero-glow"/><div><span className="eyebrow"><Icon size={14}/>{kicker}</span><h1>{title}</h1><p>{text}</p></div><div className="hero-chip"><BrainCircuit size={18}/><span>Agentic layer<br/><b>Human controlled</b></span></div></div>}
function Pulse({data}){return <div className="pulse"><div className="pulse-main"><span>Current academic signal</span><strong>{data?.risk_status||data?.standing_status||'No automated risk score'}</strong><p>{data?.risk_summary||'No risk summary is available. Review the records below for current academic information.'}</p></div><div className="mini-metrics"><div><span>Semester</span><b>{fmt(data?.student?.semester)}</b></div><div><span>Section</span><b>{fmt(data?.student?.section)}</b></div><div><span>Department</span><b>{fmt(data?.student?.department_name)}</b></div></div></div>}
function MarkTable({rows=[]}){if(!rows.length)return <Empty text="No marks are available yet."/>;return <div className="table-wrap"><table><thead><tr><th>Subject</th><th>Assessment</th><th>Marks</th></tr></thead><tbody>{rows.map((r,i)=><tr key={i}><td><b>{r.subject_code||r.code||'—'}</b><small>{r.subject_name||r.subject||''}</small></td><td>{r.assessment_name||r.assessment||r.name||'—'}</td><td><strong>{fmt(r.marks_obtained??r.marks??r.score)}</strong>{r.max_marks&&<small> / {r.max_marks}</small>}</td></tr>)}</tbody></table></div>}
function AttendanceTable({rows=[]}){if(!rows.length)return <Empty text="No attendance records are available yet."/>;return <div className="table-wrap"><table><thead><tr><th>Subject</th><th>Present</th><th>Total</th><th>Attendance</th></tr></thead><tbody>{rows.map((r,i)=>{const v=r.attendance_percentage??r.percentage??(r.total?100*r.present/r.total:0);return <tr key={i}><td><b>{r.subject_code||r.code||'—'}</b><small>{r.subject_name||r.subject||''}</small></td><td>{fmt(r.present)}</td><td>{fmt(r.total)}</td><td><div className="bar"><i style={{width:`${Math.min(100,Math.max(0,Number(v)||0))}%`}}/></div><b>{r.total?pct(v):'No attendance recorded'}</b></td></tr>})}</tbody></table></div>}
function ResultTable({rows=[]}){if(!rows.length)return <Empty text="No semester results are available yet."/>;return <div className="result-grid">{rows.map((r,i)=><div className="result" key={i}><span>Semester {r.semester}</span><strong>{fmt(r.sgpa)}</strong><small>CGPA {fmt(r.cgpa)}</small></div>)}</div>}
async function downloadProtected(url,name){if(!url)return;const res=await fetch(url,{headers:{Authorization:`Bearer ${localStorage.getItem('edunexus_token')}`}});if(!res.ok)throw new Error('File download failed');const objectUrl=URL.createObjectURL(await res.blob());const a=document.createElement('a');a.href=objectUrl;a.download=name||'download';a.click();URL.revokeObjectURL(objectUrl)}
function ResourceGrid({rows=[]}){if(!rows.length)return <Empty text="No resources have been shared yet."/>;return <div className="resource-grid">{rows.map((r,i)=><div className="resource" key={i}><div className="resource-icon"><BookOpen/></div><div><b>{r.title||r.name}</b><span>{r.resource_type||r.type||'Learning resource'}</span><small>{r.subject_code||''}</small></div><button className="icon-btn" disabled={!r.file_url} onClick={()=>downloadProtected(r.file_url,r.file_name||r.title)} aria-label="Download resource"><ArrowUpRight size={16}/></button></div>)}</div>}
function AchievementGrid({rows=[]}){if(!rows.length)return <Empty text="Build your SkillFolio by adding achievements."/>;return <div className="achievement-grid">{rows.map((r,i)=><div className="achievement" key={i}><Target size={20}/><b>{r.title}</b><span>{r.category||'Achievement'}</span><small>{r.verification_status||'Pending verification'}{r.achievement_date?` · ${r.achievement_date}`:''}</small>{r.certificate_name&&<button className="secondary" onClick={()=>downloadProtected(r.certificate_url,r.certificate_name)}>{r.certificate_name}</button>}{r.faculty_message&&<p>{r.faculty_message}</p>}</div>)}</div>}
function AchievementForm({onDone}){const [v,setV]=useState({title:'',category:'',description:'',achievement_date:''}),[file,setFile]=useState(null),[msg,setMsg]=useState('');const submit=async e=>{e.preventDefault();const f=new FormData();Object.entries(v).forEach(([k,x])=>x&&f.append(k,x));if(file)f.append('certificate',file);try{await api('/student/achievements',{method:'POST',body:f});setMsg('Achievement submitted for faculty review.');setV({title:'',category:'',description:'',achievement_date:''});setFile(null);onDone()}catch(x){setMsg(x.message)}};return <form className="form-grid" onSubmit={submit}><input required placeholder="Title" value={v.title} onChange={e=>setV({...v,title:e.target.value})}/><input required placeholder="Category" value={v.category} onChange={e=>setV({...v,category:e.target.value})}/><input type="date" value={v.achievement_date} onChange={e=>setV({...v,achievement_date:e.target.value})}/><textarea placeholder="Description" value={v.description} onChange={e=>setV({...v,description:e.target.value})}/><input type="file" accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.ppt,.pptx,.txt" onChange={e=>setFile(e.target.files[0])}/><button className="primary">Submit achievement</button>{msg&&<span>{msg}</span>}</form>}
function MentorStudent(){const [directory,setDirectory]=useState([]),[rows,setRows]=useState([]),[v,setV]=useState({faculty_id:'',project_domain:'',query:'',description:''}),[msg,setMsg]=useState('');const load=()=>Promise.all([api('/faculty/directory'),api('/student/mentor-requests')]).then(([a,b])=>{setDirectory(a.faculty||[]);setRows(b.requests||[])});useEffect(()=>{load()},[]);const submit=async e=>{e.preventDefault();const f=new FormData();Object.entries(v).forEach(([k,x])=>f.append(k,x));try{const r=await api('/student/mentor-requests',{method:'POST',body:f});setMsg(`Request saved. Email status: ${r.email_status}.`);setV({faculty_id:'',project_domain:'',query:'',description:''});load()}catch(x){setMsg(x.message)}};return <div className="stack"><Section title="Request faculty support" meta="Choose a faculty member and describe your project"><form className="form-grid" onSubmit={submit}><select required value={v.faculty_id} onChange={e=>setV({...v,faculty_id:e.target.value})}><option value="">Select faculty</option>{directory.map(f=><option value={f.id} key={f.id}>{f.name} · {f.designation||'Faculty'}</option>)}</select><input required placeholder="Project domain / area" value={v.project_domain} onChange={e=>setV({...v,project_domain:e.target.value})}/><input required placeholder="Your query" value={v.query} onChange={e=>setV({...v,query:e.target.value})}/><textarea required placeholder="Project context and description" value={v.description} onChange={e=>setV({...v,description:e.target.value})}/><button className="primary">Submit request</button>{msg&&<span>{msg}</span>}</form></Section><Section title="My requests" meta="Status and faculty messages"><div className="stack">{rows.map(r=><div className="request-row" key={r.id}><b>{r.project_domain}</b><span>{r.faculty} · {r.status}</span><p>{r.query}</p><small>{r.faculty_message||'No faculty message yet'} · Email: {r.email_status}</small></div>)}</div></Section></div>}
function NotificationsPage(){const [rows,setRows]=useState([]),[msg,setMsg]=useState('');const load=()=>api('/notifications').then(x=>setRows(x.notifications||[]));useEffect(()=>{load()},[]);const mark=async id=>{try{await api(`/notifications/${id}/read`,{method:'POST'});load()}catch(e){setMsg(e.message)}};return <><PageHero kicker="NOTIFICATIONS" title="Updates that need your attention." text="Workflow notifications are recorded in EduNexus." icon={Activity}/><Section title="Recent notifications" meta={`${rows.filter(n=>!n.is_read).length} unread`}><div className="stack">{rows.map(n=><div className="request-row" key={n.id}><b>{n.title}</b><span>{n.created_at?new Date(n.created_at).toLocaleString():''} · {n.is_read?'Read':'Unread'}</span><p>{n.message}</p>{!n.is_read&&<button className="secondary" onClick={()=>mark(n.id)}>Mark read</button>}</div>)}</div>{msg}</Section></>}
function AdminStudentForm({onCreated}){const [departments,setDepartments]=useState([]),[values,setValues]=useState({register_number:'',name:'',department_id:'',year_of_study:'1',semester:'1',section:'A',academic_year:new Date().getFullYear()+'-'+String((new Date().getFullYear()+1)%100).padStart(2,'0'),username:'',email:'',password:''}),[busy,setBusy]=useState(false),[message,setMessage]=useState('');useEffect(()=>{api('/admin/departments').then(x=>setDepartments(x.departments||[])).catch(e=>setMessage(e.message))},[]);const change=(key,value)=>setValues(old=>({...old,[key]:value}));const submit=async e=>{e.preventDefault();setBusy(true);setMessage('');try{const result=await api('/admin/students',{method:'POST',body:JSON.stringify({...values,department_id:Number(values.department_id),year_of_study:Number(values.year_of_study),semester:Number(values.semester)})});setMessage('Student created. Login username: '+result.student.username+'.');setValues(old=>({...old,register_number:'',name:'',username:'',email:'',password:''}));onCreated()}catch(e){setMessage(e.message)}finally{setBusy(false)}};return <Section title="Add a student" meta="Select the department and study year; matching subjects are enrolled automatically"><form className="form-grid" onSubmit={submit}><input required placeholder="Student ID / register number" value={values.register_number} onChange={e=>change('register_number',e.target.value)}/><input required placeholder="Student full name" value={values.name} onChange={e=>change('name',e.target.value)}/><select required value={values.department_id} onChange={e=>change('department_id',e.target.value)}><option value="">Choose department</option>{departments.map(d=><option key={d.id} value={d.id}>{d.name} · {d.code}</option>)}</select><div className="form-grid"><label>Year of study<select value={values.year_of_study} onChange={e=>{const y=e.target.value;change('year_of_study',y);change('semester',String((Number(y)-1)*2+1))}}>{[1,2,3,4].map(y=><option value={y} key={y}>{y}{y===1?'st':y===2?'nd':y===3?'rd':'th'} year</option>)}</select></label><label>Semester<select value={values.semester} onChange={e=>change('semester',e.target.value)}>{[1,2,3,4,5,6,7,8].filter(v=>Math.ceil(v/2)===Number(values.year_of_study)).map(v=><option key={v} value={v}>Semester {v}</option>)}</select></label></div><div className="form-grid"><label>Academic year<input required placeholder="2026-27" value={values.academic_year} onChange={e=>change('academic_year',e.target.value)}/></label><label>Section<input required maxLength="20" value={values.section} onChange={e=>change('section',e.target.value.toUpperCase())}/></label></div><input required placeholder="Login username" autoComplete="off" value={values.username} onChange={e=>change('username',e.target.value)}/><input required type="email" placeholder="Student email" value={values.email} onChange={e=>change('email',e.target.value)}/><input required type="password" minLength="12" placeholder="Initial password (12+ characters)" autoComplete="new-password" value={values.password} onChange={e=>change('password',e.target.value)}/><button className="primary" disabled={busy||!departments.length}>{busy?'Creating student…':'Add student'}</button>{message&&<div className="toast">{message}</div>}</form></Section>}
function Admin({tab}){const [data,setData]=useState(null),[students,setStudents]=useState([]);const loadStudents=()=>api('/admin/students').then(x=>setStudents(x.students||[]));useEffect(()=>{api('/admin/overview').then(setData);if(tab==='students')loadStudents()},[tab]);if(!data)return <PageHero kicker="ADMINISTRATION" title="System overview" text="Read-only institutional monitoring." icon={ShieldCheck}/>;return <><PageHero kicker="ADMINISTRATION" title={tab==='students'?'Student records':'System overview'} text="Read-only institutional monitoring and audit activity." icon={ShieldCheck}/>{tab==='students'?<><AdminStudentForm onCreated={loadStudents}/><Section title="Student records" meta={`${students.length} students`}><div className="table-wrap"><table><thead><tr><th>Register</th><th>Name</th><th>Department</th><th>Semester</th><th>Section</th><th>Attendance</th><th>CGPA</th><th>Status</th></tr></thead><tbody>{students.map(s=><tr key={s.register_number}><td>{s.register_number}</td><td>{s.name}</td><td>{s.department}</td><td>{s.semester}</td><td>{s.section}</td><td>{s.attendance==null?'—':`${s.attendance}%`}</td><td>{s.cgpa??'—'}</td><td>{s.status}</td></tr>)}</tbody></table></div></Section></>:<><div className="stats">{Object.entries(data.counts||{}).map(([k,v])=><Stat key={k} label={k.replaceAll('_',' ')} value={v} sub="Current database count" icon={Activity}/>)}</div><Section title="Recent audit activity" meta="Latest 50 records"><div className="table-wrap"><table><thead><tr><th>Time</th><th>User</th><th>Action</th><th>Entity</th><th>Details</th></tr></thead><tbody>{(data.audit_activity||[]).map((a,i)=><tr key={i}><td>{a.timestamp?new Date(a.timestamp).toLocaleString():'—'}</td><td>{a.user||'System'}</td><td>{a.action}</td><td>{a.entity}</td><td>{a.details}</td></tr>)}</tbody></table></div></Section></>}</>}
function ResourceItem({row,subjects,onChanged,onError}){const [editing,setEditing]=useState(false),[busy,setBusy]=useState(false),[title,setTitle]=useState(row.title||''),[description,setDescription]=useState(row.description||''),[subjectId,setSubjectId]=useState(String(row.subject_id||'')),[type,setType]=useState(row.resource_type||'DOCUMENT');const save=async e=>{e.preventDefault();setBusy(true);try{const f=new FormData();f.append('title',title);f.append('description',description);f.append('subject_id',subjectId);f.append('resource_type',type);await api('/faculty/resources/'+row.id,{method:'PATCH',body:f});setEditing(false);await onChanged()}catch(e){onError(e.message)}finally{setBusy(false)}};const remove=async()=>{if(!window.confirm('Delete this resource?'))return;setBusy(true);try{await api('/faculty/resources/'+row.id,{method:'DELETE'});await onChanged()}catch(e){onError(e.message)}finally{setBusy(false)}};const view=async()=>{setBusy(true);try{await downloadProtected(row.file_url,row.file_name||row.title)}catch(e){onError(e.message)}finally{setBusy(false)}};return <div className="request-row"><b>{row.title}</b><span>{row.subject_code} · {row.resource_type}</span><p>{row.description}</p><small>{row.file_name||'No attachment'}</small><div className="actions">{row.file_url&&<button className="secondary" disabled={busy} onClick={view}>View file</button>}<button className="secondary" disabled={busy} onClick={()=>setEditing(!editing)}>{editing?'Cancel':'Edit metadata'}</button><button className="secondary" disabled={busy} onClick={remove}>Delete</button></div>{editing&&<form className="form-grid" onSubmit={save}><input required aria-label="Resource title" value={title} onChange={e=>setTitle(e.target.value)}/><textarea aria-label="Description" value={description} onChange={e=>setDescription(e.target.value)}/><select required aria-label="Subject" value={subjectId} onChange={e=>setSubjectId(e.target.value)}>{subjects.map(x=><option key={x.id} value={x.id}>{x.code} · {x.name}</option>)}</select><select aria-label="Resource type" value={type} onChange={e=>setType(e.target.value)}>{['DOCUMENT','NOTES','VIDEO','LINK'].map(x=><option key={x}>{x}</option>)}</select><button className="primary" disabled={busy}>{busy?'Saving…':'Save changes'}</button></form>}</div>}
function FacultyAux({tab}){const [rows,setRows]=useState([]),[subjects,setSubjects]=useState([]),[subject,setSubject]=useState(''),[section,setSection]=useState('A'),[report,setReport]=useState(null),[message,setMessage]=useState('');const load=()=>api(tab==='mentor'?'/faculty/mentor-requests':tab==='reviews'?'/faculty/achievement-reviews':'/faculty/resources').then(x=>setRows(x.requests||x.achievements||x.resources||[]));useEffect(()=>{load();api('/faculty/subjects').then(x=>setSubjects(x.subjects||[]))},[tab]);const decide=async(path,id,status)=>{const messageText=window.prompt('Message for the student (optional)')||'';try{await api(`${path}/${id}/decision`,{method:'POST',body:JSON.stringify({status,message:messageText})});load()}catch(e){setMessage(e.message)}};const analyze=async()=>{try{setReport(await api(`/faculty/class-intelligence?subject_id=${subject}&section=${section}`))}catch(e){setMessage(e.message)}};return <><PageHero kicker="FACULTY WORKSPACE" title={tab==='mentor'?'Mentor requests':tab==='reviews'?'Achievement reviews':tab==='insights'?'Class intelligence':'Faculty resources'} text={tab==='insights'?'Read-only class measures calculated from academic records.':'Review and manage academic work from one focused workspace.'} icon={tab==='insights'?TrendingUp:tab==='resources'?CloudUpload:Users}/>{tab==='mentor'&&<Section title="Assigned mentor requests" meta={`${rows.length} requests`}><div className="stack">{rows.map(r=><div className="request-row" key={r.id}><b>{r.student} · {r.register_number}</b><span>{r.project_domain} · {r.status}</span><p>{r.query}: {r.description}</p><small>Semester {r.semester} · {r.department} · {r.faculty_message||'No response sent'}</small>{r.status==='PENDING'&&<div className="actions"><button className="primary" onClick={()=>decide('/faculty/mentor-requests',r.id,'APPROVED')}>Approve</button><button className="secondary" onClick={()=>decide('/faculty/mentor-requests',r.id,'REJECTED')}>Reject</button></div>}</div>)}</div>{message}</Section>}{tab==='reviews'&&<Section title="SkillFolio submissions" meta={`${rows.filter(x=>x.status==='PENDING').length} pending`}><div className="stack">{rows.map(r=><div className="request-row" key={r.id}><b>{r.title} · {r.student}</b><span>{r.category} · {r.status}</span><p>{r.description}</p><small>{r.register_number} · {r.achievement_date||'Date not provided'} · {r.certificate_name||'No certificate'}</small>{r.certificate_url&&<button className="secondary" onClick={()=>downloadProtected(r.certificate_url,r.certificate_name)}>View certificate</button>}{r.status==='PENDING'&&<div className="actions"><button className="primary" onClick={()=>decide('/faculty/achievement-reviews',r.id,'APPROVED')}>Approve</button><button className="secondary" onClick={()=>decide('/faculty/achievement-reviews',r.id,'REJECTED')}>Reject</button></div>}</div>)}</div></Section>}{tab==='resources'&&<><Section title="Upload a learning resource" meta="Files are stored locally for Evaluation I"><ResourceForm subjects={subjects} onDone={load}/></Section><Section title="Your resources" meta={`${rows.length} resources`}><div className="stack">{rows.map(r=><ResourceItem key={r.id} row={r} subjects={subjects} onChanged={load} onError={setMessage}/>)}</div>{message}</Section></>}{tab==='insights'&&<Section title="Class snapshot" meta="Database aggregates"><div className="form-grid"><select value={subject} onChange={e=>setSubject(e.target.value)}><option value="">Choose a subject</option>{subjects.map(s=><option key={s.id} value={s.id}>{s.code} · {s.name}</option>)}</select><select value={section} onChange={e=>setSection(e.target.value)}><option>A</option><option>B</option></select><button className="primary" disabled={!subject} onClick={analyze}>Load class snapshot</button></div>{report&&<><div className="stats">{['student_count','attendance_average','assessment_average','highest','lowest'].map(k=><Stat key={k} label={k.replaceAll('_',' ')} value={report[k]??'No records'} sub={report.subject} icon={Activity}/>)}</div><div className="table-wrap"><table><thead><tr><th>Student</th><th>Register</th><th>Attendance</th><th>Average marks</th><th>Attention</th></tr></thead><tbody>{report.students.map(s=><tr key={s.register_number}><td>{s.student}</td><td>{s.register_number}</td><td>{s.attendance==null?'No records':`${s.attendance}%`}</td><td>{s.average_marks==null?'No records':`${s.average_marks}%`}</td><td>{s.attention}</td></tr>)}</tbody></table></div></>}{message}</Section>}</>}
function ResourceForm({subjects,onDone}){const [v,setV]=useState({title:'',description:'',subject_id:'',resource_type:'DOCUMENT'}),[file,setFile]=useState(null),[msg,setMsg]=useState('');const submit=async e=>{e.preventDefault();const f=new FormData();Object.entries(v).forEach(([k,x])=>f.append(k,x));if(file)f.append('file',file);try{await api('/faculty/resources',{method:'POST',body:f});setMsg('Resource saved.');onDone()}catch(x){setMsg(x.message)}};return <form className="form-grid" onSubmit={submit}><input required placeholder="Title" value={v.title} onChange={e=>setV({...v,title:e.target.value})}/><textarea placeholder="Description" value={v.description} onChange={e=>setV({...v,description:e.target.value})}/><select required value={v.subject_id} onChange={e=>setV({...v,subject_id:e.target.value})}><option value="">Choose subject</option>{subjects.map(s=><option key={s.id} value={s.id}>{s.code} · {s.name}</option>)}</select><select value={v.resource_type} onChange={e=>setV({...v,resource_type:e.target.value})}><option>DOCUMENT</option><option>NOTES</option><option>VIDEO</option><option>LINK</option></select><input type="file" onChange={e=>setFile(e.target.files[0])}/><button className="primary">Upload resource</button>{msg}</form>}
function JsonPreview({data}){if(!data)return <Empty text="Your interpreted fields will appear here."/>;const x=data.attendance||data.marks||data.data||data;return <div className="json-card">{Object.entries(x).map(([k,v])=><div key={k}><span>{k.replaceAll('_',' ')}</span><b>{typeof v==='object'?JSON.stringify(v):String(v??'Not provided')}</b></div>)}</div>}
function ValidationView({data}){if(data.status!=='READY_FOR_CONFIRMATION')return <div className="validation fail"><AlertCircle/><div><b>Validation failed</b>{(data.errors||[data.detail]).filter(Boolean).map((e,i)=><p key={i}>{e}</p>)}</div></div>;const p=data.preview||data;return <div className="validation pass"><CheckCircle2/><div><b>Ready for confirmation</b><div className="validation-stats"><span>{p.total_records??p.total_students} records</span><span>{p.valid_records??p.present_count} valid</span><span>{p.invalid_records??p.absent_count??0} invalid</span></div></div></div>}
function ErrorState({error}){return <div className="error-state"><AlertCircle/><h2>Unable to load this workspace</h2><p>{error}</p></div>}
function AadhiCard(){return <div className="aadhi-card"><div className="aadhi-avatar"><img src="/aadhi-3d.png"/></div><div><b>Ask Aadhi anything</b><p>Academic help, campus guidance and your next best question.</p><button className="secondary" onClick={()=>window.dispatchEvent(new Event('open-aadhi'))}>Ask Aadhi <ArrowUpRight size={15}/></button></div></div>}
function Aadhi(){
    const [open,setOpen]=useState(false);
    const [q,setQ]=useState('');
    const [messages,setMessages]=useState([]);
    const [busy,setBusy]=useState(false);

    useEffect(()=>{
        const f=()=>setOpen(true);
        window.addEventListener('open-aadhi',f);
        return()=>window.removeEventListener('open-aadhi',f);
    },[]);

    const send=async()=>{
        const question=q.trim();

        if(!question || busy)return;

        setMessages(prev=>[
            ...prev,
            {
                role:'user',
                text:question
            }
        ]);

        setQ('');
        setBusy(true);

        try{
            const result=await api('/copilot/ask',{
                method:'POST',
                body:JSON.stringify({
                    question,
                    top_k:5
                })
            });

            setMessages(prev=>[
                ...prev,
                {
                    role:'assistant',
                    text:result.answer,
                    route:result.route,
                    sources:result.sources||[]
                }
            ]);
        }catch(error){
            setMessages(prev=>[
                ...prev,
                {
                    role:'assistant',
                    text:`I couldn't process that request right now. ${error.message}`
                }
            ]);
        }finally{
            setBusy(false);
        }
    };

    const askSuggestion=(question)=>{
        setQ(question);
    };

    return <>
        <button
            className="aadhi-fab"
            onClick={()=>setOpen(!open)}
            aria-label="Ask Aadhi"
        >
            <span className="fab-ring"/>
            <img src="/aadhi-3d.png"/>
        </button>

        {open&&
        <div className="aadhi-chat">

            <div className="chat-head">
                <div>
                    <b>Ask Aadhi</b>
                    <span>Campus companion</span>
                </div>

                <button
                    className="icon-btn"
                    onClick={()=>setOpen(false)}
                >
                    <X size={17}/>
                </button>
            </div>

            <div className="chat-body">

                {messages.length===0&&
                    <div className="aadhi-bubble">
                        <img src="/aadhi.png"/>
                        <div>
                            <b>Hey! I'm Aadhi 👋</b>
                            <p>
                                Ask me about your academics, campus resources,
                                attendance, marks, results, or university policies.
                            </p>
                        </div>
                    </div>
                }

                {messages.map((message,index)=>
                    <div
                        key={index}
                        className={
                            message.role==='user'
                                ? 'chat-message user-message'
                                : 'chat-message assistant-message'
                        }
                    >
                        <div className="message-content">
                            <p>{message.text}</p>
                        </div>
                    </div>
                )}

                {busy&&
                    <div className="chat-message assistant-message">
                        <img src="/aadhi.png"/>
                        <div className="message-content">
                            <div className="typing">
                                <span/>
                                <span/>
                                <span/>
                            </div>
                        </div>
                    </div>
                }

                {messages.length===0&&
                    <div className="suggestions">
                        <button onClick={()=>askSuggestion('Show my academic highlights')}>
                            Academic highlights
                        </button>

                        <button onClick={()=>askSuggestion('What resources should I read?')}>
                            Study resources
                        </button>

                        <button onClick={()=>askSuggestion('What is my attendance percentage?')}>
                            Attendance
                        </button>

                        <button onClick={()=>askSuggestion('What are my weak subjects?')}>
                            My performance
                        </button>
                    </div>
                }

            </div>

            <div className="chat-input">
                <input
                    value={q}
                    onChange={e=>setQ(e.target.value)}
                    onKeyDown={e=>{
                        if(e.key==='Enter'){
                            e.preventDefault();
                            send();
                        }
                    }}
                    placeholder="Ask Aadhi..."
                    disabled={busy}
                />

                <button
                    onClick={send}
                    disabled={busy||!q.trim()}
                >
                    {busy
                        ? <Loader2 className="spin" size={18}/>
                        : <ArrowUpRight size={18}/>
                    }
                </button>
            </div>

            <div className="chat-note">
                AI answers are grounded in EduNexus academic and institutional data.
            </div>

        </div>}
    </>
}
function App(){const [user,setUser]=useState(()=>JSON.parse(localStorage.getItem('edunexus_user')||'null')),[tab,setTab]=useState('home');const signout=()=>{logout();setUser(null);setTab('home')};if(!user)return <Login onLogin={setUser}/>;return <Shell user={user} tab={tab} setTab={setTab} onLogout={signout}>{user.role==='FACULTY'?<Faculty tab={tab}/>:user.role==='ADMIN'?<Admin tab={tab}/>:<Student tab={tab}/>}</Shell>}
createRoot(document.getElementById('root')).render(<App/>);








