import * as Dialog from "@radix-ui/react-dialog";
import { FlaskConical, Gauge, Network, Search, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { IncidentSummary } from "../api/types";

interface CommandSearchProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  incidents: IncidentSummary[];
}

export function CommandSearch({ open, onOpenChange, incidents }: CommandSearchProps) {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();
  useEffect(() => { if (!open) setQuery(""); }, [open]);
  const commands = useMemo(() => [
    ...incidents.map((incident) => ({
      id: incident.id,
      label: incident.title,
      meta: incident.id,
      icon: Network,
      path: `/incidents/${incident.id}`,
    })),
    { id: "benchmark", label: "Open benchmark report", meta: "research", icon: Gauge, path: "/benchmark" },
    { id: "method", label: "Inspect causal method", meta: "assumptions", icon: FlaskConical, path: "/methodology" },
  ], [incidents]);
  const filtered = commands.filter((command) => `${command.label} ${command.meta}`.toLowerCase().includes(query.toLowerCase()));
  function select(path: string) {
    void navigate(path);
    onOpenChange(false);
  }
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="command-search" aria-describedby="command-description">
          <Dialog.Title className="sr-only">Go to a FaultGraph view</Dialog.Title>
          <Dialog.Description id="command-description" className="sr-only">Search incidents and research views.</Dialog.Description>
          <div className="command-search__input"><Search size={17} /><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Find an incident or research view" aria-label="Search commands" /><Dialog.Close className="icon-button" aria-label="Close search"><X size={16} /></Dialog.Close></div>
          <div className="command-search__list" role="listbox" aria-label="Commands">
            {filtered.length ? filtered.map((command) => {
              const Icon = command.icon;
              return <button type="button" role="option" aria-selected="false" key={command.id} onClick={() => select(command.path)}><Icon size={16} /><span><strong>{command.label}</strong><small>{command.meta}</small></span><kbd>↵</kbd></button>;
            }) : <p className="command-empty">No matching incident or view.</p>}
          </div>
          <footer><span><kbd>⌘</kbd><kbd>K</kbd> open</span><span><kbd>esc</kbd> close</span></footer>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
