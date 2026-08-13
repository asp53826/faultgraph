import { Activity, BookOpen, Gauge, PanelLeftClose, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import type { IncidentSummary } from "../api/types";
import { CommandSearch } from "./CommandSearch";
import { StatusMark } from "./StatusMark";

interface WorkbenchShellProps {
  incidents: IncidentSummary[];
}

export function WorkbenchShell({ incidents }: WorkbenchShellProps) {
  const [commandsOpen, setCommandsOpen] = useState(false);
  const [railOpen, setRailOpen] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();
  useEffect(() => {
    function handleKeydown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setCommandsOpen((value) => !value);
      }
    }
    window.addEventListener("keydown", handleKeydown);
    return () => window.removeEventListener("keydown", handleKeydown);
  }, []);
  const inIncident = location.pathname.startsWith("/incidents/");
  return (
    <div className={`workbench ${railOpen ? "" : "workbench--rail-closed"}`}>
      <header className="topbar">
        <button className="brand" type="button" onClick={() => { void navigate(incidents[0] ? `/incidents/${incidents[0].id}` : "/"); }} aria-label="FaultGraph home">
          <span className="brand__mark" aria-hidden="true"><i /><i /><i /></span>
          <span><strong>FaultGraph</strong><small>causal incident workbench</small></span>
        </button>
        <nav aria-label="Research views">
          <NavLink to={incidents[0] ? `/incidents/${incidents[0].id}` : "/"} className={inIncident ? "active" : ""}><Activity size={14} /> Investigate</NavLink>
          <NavLink to="/benchmark"><Gauge size={14} /> Benchmark</NavLink>
          <NavLink to="/methodology"><BookOpen size={14} /> Method</NavLink>
        </nav>
        <div className="topbar__actions">
          <StatusMark tone="trace" label="deterministic lab" />
          <button className="search-trigger" type="button" onClick={() => setCommandsOpen(true)}><Search size={14} /><span>Find</span><kbd>⌘K</kbd></button>
        </div>
      </header>
      <aside className="incident-rail" aria-label="Incident index">
        <div className="incident-rail__heading"><span>Incident index</span><button className="icon-button" type="button" onClick={() => setRailOpen(false)} aria-label="Close incident index"><PanelLeftClose size={15} /></button></div>
        <div className="incident-rail__list">
          {incidents.map((incident) => <NavLink key={incident.id} to={`/incidents/${incident.id}`} className="incident-link"><span className={`incident-link__severity ${incident.severity === "SEV-1" ? "is-critical" : ""}`}>{incident.severity}</span><strong>{incident.title}</strong><small>{incident.id}</small><span className="incident-link__meta">{incident.affected_nodes} nodes · {(incident.confidence * 100).toFixed(0)}%</span></NavLink>)}
        </div>
        <footer><span>Source</span><strong>synthetic-exchange-v1</strong><small>3 labeled incidents</small></footer>
      </aside>
      {!railOpen ? <button className="rail-reopen" type="button" onClick={() => setRailOpen(true)} aria-label="Open incident index"><PanelLeftClose size={15} /></button> : null}
      <main className="workspace"><Outlet /></main>
      <CommandSearch open={commandsOpen} onOpenChange={setCommandsOpen} incidents={incidents} />
    </div>
  );
}
