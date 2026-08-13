import { Navigate, Route, Routes } from "react-router-dom";
import { api } from "./api/client";
import { useResource } from "./api/useResource";
import { ResourceState } from "./components/ResourceState";
import { WorkbenchShell } from "./components/WorkbenchShell";
import { BenchmarkPage } from "./pages/BenchmarkPage";
import { InvestigationPage } from "./pages/InvestigationPage";
import { MethodologyPage } from "./pages/MethodologyPage";

export default function App() {
  const incidents = useResource(api.incidents, "incidents");
  if (incidents.loading) return <ResourceState loading />;
  if (!incidents.data?.length) return <ResourceState error={incidents.error ?? "The dataset contains no incidents."} onRetry={incidents.reload} />;
  const first = incidents.data[0].id;
  return <Routes><Route element={<WorkbenchShell incidents={incidents.data} />}><Route index element={<Navigate to={`/incidents/${first}`} replace />} /><Route path="incidents/:incidentId" element={<InvestigationPage />} /><Route path="benchmark" element={<BenchmarkPage />} /><Route path="methodology" element={<MethodologyPage />} /><Route path="*" element={<Navigate to={`/incidents/${first}`} replace />} /></Route></Routes>;
}
