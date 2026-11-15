import { useMemo, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { Float, MeshDistortMaterial, Sphere, Stars } from "@react-three/drei";
import { motion } from "framer-motion";
import {
  Activity, ArrowUpRight, Bell, BrainCircuit, BriefcaseBusiness,
  ChartNoAxesCombined, ChevronDown, ChevronRight, CircleHelp, CloudUpload,
  Database, FileSpreadsheet, Gauge, LayoutDashboard, Lightbulb, Menu,
  MoreHorizontal, Plus, Search, Send, Settings2, ShieldCheck, Sparkles,
  TrendingUp, Utensils, Zap
} from "lucide-react";
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

type Section = "Overview" | "Data workspace" | "AI advisor" | "Insights";
const salesData = [
  { month: "May", revenue: 38500, profit: 11200 },
  { month: "Jun", revenue: 42800, profit: 13800 },
  { month: "Jul", revenue: 39700, profit: 11900 },
  { month: "Aug", revenue: 51600, profit: 17400 },
  { month: "Sep", revenue: 48200, profit: 15900 },
  { month: "Oct", revenue: 62400, profit: 21800 },
  { month: "Nov", revenue: 58300, profit: 19600 }
];
const products = [
  { name: "Premium package", category: "Services", revenue: "₹18,420", share: 82, color: "blue" },
  { name: "Core subscription", category: "Subscriptions", revenue: "₹12,850", share: 64, color: "mint" },
  { name: "Add-on bundle", category: "Accessories", revenue: "₹8,640", share: 43, color: "violet" },
  { name: "Starter plan", category: "Subscriptions", revenue: "₹6,290", share: 31, color: "coral" }
];

function Orb() {
  return <div className="orb-wrap" aria-label="Animated 3D AI orb">
    <div className="orb-halo halo-one" /><div className="orb-halo halo-two" />
    <Canvas camera={{ position: [0, 0, 4.4], fov: 42 }} dpr={[1, 1.5]}>
      <ambientLight intensity={0.8} />
      <pointLight position={[3, 3, 4]} intensity={18} color="#55c8ff" />
      <pointLight position={[-3, -2, 2]} intensity={12} color="#287bff" />
      <Float speed={1.4} rotationIntensity={0.45} floatIntensity={0.7}>
        <Sphere args={[1.18, 96, 96]}>
          <MeshDistortMaterial color="#1768dc" roughness={0.16} metalness={0.72} distort={0.34} speed={2.2} />
        </Sphere>
      </Float>
      <Stars radius={4} depth={2} count={180} factor={2} saturation={0} fade speed={0.5} />
    </Canvas>
    <div className="orb-core" />
  </div>;
}

function Sidebar({ active, setActive, mobileOpen, closeMobile }: {
  active: Section; setActive: (s: Section) => void; mobileOpen: boolean; closeMobile: () => void;
}) {
  const nav: { label: Section; icon: typeof LayoutDashboard }[] = [
    { label: "Overview", icon: LayoutDashboard }, { label: "Data workspace", icon: Database },
    { label: "AI advisor", icon: BrainCircuit }, { label: "Insights", icon: Lightbulb }
  ];
  return <>
    {mobileOpen && <button className="mobile-scrim" onClick={closeMobile} aria-label="Close navigation" />}
    <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
      <div className="brand"><div className="brand-mark"><Activity size={19} /></div><span>salesmind<span className="brand-ai">.ai</span></span></div>
      <div className="workspace-switch"><div className="workspace-avatar">A</div><div><b>Acme workspace</b><small>Business account</small></div><ChevronDown size={15} /></div>
      <div className="nav-label">WORKSPACE</div>
      <nav>{nav.map(({ label, icon: Icon }) => <button key={label} className={`nav-item ${active === label ? "active" : ""}`} onClick={() => { setActive(label); closeMobile(); }}><Icon size={17} /><span>{label}</span>{label === "AI advisor" && <span className="nav-new">AI</span>}</button>)}</nav>
      <div className="sidebar-bottom">
        <div className="help-card"><div className="help-icon"><CircleHelp size={17} /></div><b>Need a hand?</b><p>Explore the SalesMind guide and get more from your data.</p><button onClick={() => setActive("Insights")}>Explore guide <ChevronRight size={13} /></button></div>
        <button className="nav-item"><Settings2 size={17} /><span>Settings</span></button>
        <div className="profile-row"><div className="profile-avatar">AR</div><div><b>Aditya Raman</b><small>Free workspace</small></div><MoreHorizontal size={18} /></div>
      </div>
    </aside>
  </>;
}

function MetricCard({ title, value, change, icon: Icon, tone, note }: {
  title: string; value: string; change: string; icon: typeof TrendingUp; tone: string; note: string;
}) {
  return <motion.div className="metric-card glass-card" whileHover={{ y: -4, transition: { duration: 0.2 } }}>
    <div className="metric-top"><span>{title}</span><div className={`metric-icon ${tone}`}><Icon size={17} /></div></div>
    <div className="metric-value">{value}</div>
    <div className="metric-foot"><span className="trend-up"><ArrowUpRight size={13} /> {change}</span><span>{note}</span></div>
  </motion.div>;
}

export default function App() {
  const [active, setActive] = useState<Section>("Overview");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profile, setProfile] = useState("Small business");
  const [fileName, setFileName] = useState("");
  const [uploadMessage, setUploadMessage] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([{ role: "assistant", text: "Hi Aditya — I’m your SalesMind business advisor. Ask me about revenue trends, margins, products, or opportunities hiding in your data." }]);
  const fileRef = useRef<HTMLInputElement>(null);
  const [range, setRange] = useState("Last 7 months");

  const pageTitle = active === "Overview" ? "Good evening, Aditya" : active;
  const pageSub = active === "Overview" ? "Here’s what’s happening with your business today." :
    active === "Data workspace" ? "Bring your business data together in one intelligent workspace." :
    active === "AI advisor" ? "Ask better questions. Make more confident decisions." : "Turn business signals into your next best move.";

  const chartData = useMemo(() => range === "Last 7 months" ? salesData : salesData.slice(-3), [range]);

async function handleFile(file?: File) {
  if (!file) return;

  if (!file.name.toLowerCase().endsWith(".csv")) {
    setUploadMessage("CSV preview is currently supported. Excel support will be added with the backend.");
    return;
  }

  setFileName(file.name);

  try {
    const content = await file.text();
    const rows = content.trim().split(/\r?\n/);

    if (rows.length < 2) {
      setUploadMessage("The CSV file appears empty or has no data rows.");
      return;
    }

    const columns = rows[0].split(",").length;

    setUploadMessage(
      `${(rows.length - 1).toLocaleString()} rows detected · ${columns} columns. Backend connection is the next integration step.`
    );
  } catch {
    setUploadMessage("We couldn't read this CSV file.");
  }
}

  function sendQuestion() {
    const clean = question.trim();
    if (!clean) return;
    setMessages(prev => [...prev, { role: "user", text: clean }, { role: "assistant", text: "The advisor interface is ready. Connect the FastAPI analytics endpoint to return evidence-grounded answers from your uploaded dataset. No business figures are being invented in this preview." }]);
    setQuestion("");
  }

  return <div className="app-shell">
    <Sidebar active={active} setActive={setActive} mobileOpen={mobileOpen} closeMobile={() => setMobileOpen(false)} />
    <main className="main-area">
      <header className="topbar">
        <button className="icon-button mobile-menu" onClick={() => setMobileOpen(true)} aria-label="Open menu"><Menu size={19} /></button>
        <div className="breadcrumb"><span>Workspace</span><ChevronRight size={14} /><b>{active}</b></div>
        <div className="top-actions"><div className="search-box"><Search size={15} /><span>Search anything...</span><kbd>⌘ K</kbd></div><button className="icon-button notification" aria-label="Notifications"><Bell size={17} /><i /></button><div className="top-avatar">AR</div></div>
      </header>

      <div className="page-content">
        <div className="page-heading">
          <div><div className="eyebrow"><span className="live-dot" /> BUSINESS INTELLIGENCE <span className="eyebrow-sep">/</span> NOVEMBER 2026</div><h1>{pageTitle}<span className="heading-period">.</span></h1><p>{pageSub}</p></div>
          <div className="heading-actions"><button className="button-secondary" onClick={() => setActive("Data workspace")}><Plus size={16} /> Add data</button><button className="button-primary" onClick={() => setActive("AI advisor")}><Sparkles size={16} /> Ask SalesMind</button></div>
        </div>

        {active === "Overview" && <>
          <section className="hero-panel">
            <div className="hero-copy"><div className="hero-tag"><Sparkles size={13} /> YOUR AI BUSINESS PARTNER</div><h2>See the bigger picture.<br/><span>Move your business forward.</span></h2><p>Make sense of your numbers, uncover hidden opportunities, and turn everyday data into your next smart move.</p><div className="hero-cta"><button className="button-primary" onClick={() => setActive("Data workspace")}>Explore your data <ChevronRight size={16} /></button><span><ShieldCheck size={14} /> Your data stays yours</span></div></div>
            <div className="hero-visual"><Orb /><div className="orb-caption"><span className="live-dot" /> SALESMIND INTELLIGENCE <span>ONLINE</span></div><div className="float-chip chip-top"><span className="chip-dot mint-dot" /> Patterns detected <b>+12</b></div><div className="float-chip chip-bottom"><TrendingUp size={15} /><span>Growth opportunity</span><b>+18.6%</b></div></div>
            <div className="hero-grid" />
          </section>

          <div className="section-heading"><div><h3>Business pulse</h3><p>A snapshot of your key performance indicators</p></div><button className="text-button" onClick={() => setActive("Insights")}>View report <ChevronRight size={14} /></button></div>
          <div className="metrics-grid">
            <MetricCard title="Total revenue" value="₹4,28,650" change="12.8%" note="vs. last period" icon={TrendingUp} tone="blue" />
            <MetricCard title="Net profit" value="₹1,16,420" change="8.4%" note="vs. last period" icon={Activity} tone="mint" />
            <MetricCard title="Orders processed" value="1,284" change="6.2%" note="vs. last period" icon={BriefcaseBusiness} tone="violet" />
            <MetricCard title="Profit margin" value="27.2%" change="2.1%" note="vs. last period" icon={Gauge} tone="coral" />
          </div>

          <div className="dashboard-grid">
            <section className="panel chart-panel"><div className="panel-heading"><div><h3>Revenue overview</h3><p>Track your revenue and profitability over time</p></div><select value={range} onChange={e => setRange(e.target.value)}><option>Last 7 months</option><option>Last 3 months</option></select></div><div className="chart-legend"><span><i className="legend-blue" /> Revenue</span><span><i className="legend-mint" /> Profit</span></div><div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><AreaChart data={chartData} margin={{ top: 12, right: 8, left: -18, bottom: 0 }}><defs><linearGradient id="revFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#287BFF" stopOpacity={0.25}/><stop offset="95%" stopColor="#287BFF" stopOpacity={0}/></linearGradient><linearGradient id="profitFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#10D6B0" stopOpacity={0.18}/><stop offset="95%" stopColor="#10D6B0" stopOpacity={0}/></linearGradient></defs><CartesianGrid stroke="#ffffff" strokeOpacity={0.055} vertical={false}/><XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: "#71819b", fontSize: 11 }} dy={10}/><YAxis axisLine={false} tickLine={false} tick={{ fill: "#71819b", fontSize: 10 }} tickFormatter={v => `₹${v/1000}k`}/><Tooltip contentStyle={{ background: "#10233f", border: "1px solid #29405f", borderRadius: 12, color: "#fff" }} formatter={(v) => `₹${Number(v).toLocaleString("en-IN")}`}/><Area type="monotone" dataKey="revenue" stroke="#3988ff" strokeWidth={2.5} fill="url(#revFill)"/><Area type="monotone" dataKey="profit" stroke="#10d6b0" strokeWidth={2} fill="url(#profitFill)"/></AreaChart></ResponsiveContainer></div><div className="chart-note"><span><i className="trend-dot" /> Revenue is trending upward</span><span>Illustrative preview data</span></div></section>

            <section className="panel product-panel"><div className="panel-heading"><div><h3>Top performers</h3><p>Revenue by product or service</p></div><button className="icon-button subtle"><MoreHorizontal size={18}/></button></div><div className="product-list">{products.map((p, i) => <div className="product-row" key={p.name}><div className={`product-rank rank-${i+1}`}>{String(i+1).padStart(2, "0")}</div><div className="product-info"><div><b>{p.name}</b><span>{p.category}</span></div><div className="product-bar"><i className={`bar-${p.color}`} style={{ width: `${p.share}%` }}/></div></div><strong>{p.revenue}</strong></div>)}</div><button className="panel-link" onClick={() => setActive("Insights")}>Explore product insights <ArrowUpRight size={14}/></button></section>
          </div>

          <section className="insight-banner"><div className="insight-icon"><Sparkles size={19}/></div><div><div className="insight-label">A THOUGHT FROM SALESMIND</div><h3>Your next growth opportunity is closer than you think.</h3><p>Connect your actual sales data to discover specific trends, margin leaks and high-value opportunities.</p></div><button className="button-secondary" onClick={() => setActive("AI advisor")}>Explore insights <ChevronRight size={15}/></button></section>
        </>}

        {active === "Data workspace" && <section className="workspace-layout">
          <div className="panel upload-panel"><div className="section-kicker"><Database size={15}/> DATA MANAGEMENT</div><h2>Bring your numbers<br/><span>into focus.</span></h2><p className="muted-copy">Upload your sales data and let SalesMind organize the details into a clear picture of your business.</p>
            <div className="dropzone" onDragOver={e => e.preventDefault()} onDrop={e => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }} onClick={() => fileRef.current?.click()} role="button" tabIndex={0} onKeyDown={e => e.key === "Enter" && fileRef.current?.click()}><div className="upload-icon"><CloudUpload size={24}/></div><b>Drop your dataset here</b><span>or <u>browse files</u> from your device</span><small>CSV files supported · Excel integration coming soon</small><input ref={fileRef} type="file" accept=".csv" hidden onChange={e => handleFile(e.target.files?.[0])}/></div>
            {fileName && <div className="file-confirm"><FileSpreadsheet size={18}/><div><b>{fileName}</b><small>{uploadMessage}</small></div><ShieldCheck size={17}/></div>}
            {!fileName && <div className="privacy-note"><ShieldCheck size={15}/> Upload preview runs locally in your browser. Connect the API to enable server-side analysis.</div>}
          </div>
          <div className="panel profile-panel"><div className="section-kicker"><Settings2 size={15}/> BUSINESS CONTEXT</div><h3>Tell us about your business</h3><p className="muted-copy">We'll tailor the metrics and recommendations to your business model.</p><label className="field-label">BUSINESS PROFILE</label><div className="profile-options">{[{name:"Small business",icon:BriefcaseBusiness,desc:"Retail, services & independent shops"},{name:"Large business",icon:ChartNoAxesCombined,desc:"Multi-team and multi-region operations"},{name:"Restaurant",icon:Utensils,desc:"Menu, orders & meal combinations"}].map(({name,icon:Icon,desc})=><button key={name} className={`profile-option ${profile===name?"selected":""}`} onClick={() => setProfile(name)}><div className="option-icon"><Icon size={18}/></div><div><b>{name}</b><small>{desc}</small></div><span className="radio-dot"/></button>)}</div><div className="profile-note"><Sparkles size={15}/> Selected profile: <b>{profile}</b></div><button className="button-primary full-button" onClick={() => setUploadMessage(fileName ? "Profile saved for this preview. Connect the API to run analysis." : "Choose a dataset first, then connect the API to analyze it.")}>Continue to analysis <ChevronRight size={16}/></button></div>
        </section>}

        {active === "AI advisor" && <section className="advisor-layout"><div className="panel advisor-intro"><div className="advisor-orb"><Orb/></div><div className="section-kicker"><Sparkles size={14}/> SALESMIND ADVISOR</div><h2>Think like a strategist.<br/><span>Act with clarity.</span></h2><p className="muted-copy">Ask questions about your business and get practical, evidence-led guidance. Connect your dataset to enable live analysis.</p><div className="advisor-capabilities"><span><ShieldCheck size={14}/> Evidence-first answers</span><span><Zap size={14}/> Practical next steps</span></div></div><div className="panel chat-panel"><div className="chat-header"><div className="advisor-avatar"><BrainCircuit size={18}/></div><div><b>SalesMind AI</b><small><i className="live-dot"/> Business advisor · Preview</small></div><button className="icon-button subtle"><MoreHorizontal size={18}/></button></div><div className="chat-messages">{messages.map((m,i)=><div key={i} className={`message ${m.role}`}><div className="message-avatar">{m.role==="assistant"?<Sparkles size={14}/>: "AR"}</div><div className="message-bubble">{m.text}</div></div>)}</div><div className="suggested-questions"><small>TRY ASKING</small>{["Where am I losing margin?","Which products drive profit?","How can I grow revenue?"].map(q=><button key={q} onClick={() => setQuestion(q)}>{q}<ArrowUpRight size={12}/></button>)}</div><form className="chat-input" onSubmit={e => {e.preventDefault();sendQuestion();}}><input value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Ask anything about your business..."/><button type="submit" aria-label="Send question"><Send size={17}/></button></form><div className="chat-disclaimer">SalesMind can make mistakes. Verify important business decisions against your source data.</div></div></section>}

        {active === "Insights" && <section className="insights-page"><div className="insights-hero panel"><div className="insight-icon large"><Lightbulb size={22}/></div><div><div className="section-kicker">INTELLIGENCE, NOT JUST INFORMATION</div><h2>Make your next move<br/><span>your smartest one.</span></h2><p className="muted-copy">SalesMind turns patterns into priorities. Connect a real dataset to unlock grounded recommendations.</p></div><Orb/></div><div className="insight-cards"><div className="panel"><div className="insight-card-icon mint"><TrendingUp size={19}/></div><h3>Find growth opportunities</h3><p>Identify your strongest products, customer segments and sales periods.</p></div><div className="panel"><div className="insight-card-icon coral"><Activity size={19}/></div><h3>Protect your margins</h3><p>Surface cost pressure, loss-making items and profitability risks.</p></div><div className="panel"><div className="insight-card-icon blue"><BrainCircuit size={19}/></div><h3>Plan your next move</h3><p>Turn your business performance into clear, prioritized actions.</p></div></div></section>}
        <footer className="footer"><span>© 2026 SalesMind AI</span><span><i className="live-dot"/> All systems designed for clarity</span><span>Built for better business decisions</span></footer>
      </div>
    </main>
  </div>;
}

