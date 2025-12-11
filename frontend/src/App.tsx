import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Layout from './components/Layout'
import {
  LoginPage,
  DashboardPage,
  UploadPage,
  ClustersPage,
  ClusterDetailPage,
  AssessmentsPage,
  ApprovalsPage,
  KnowledgePage,
  SettingsPage,
} from './pages'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="clusters" element={<ClustersPage />} />
        <Route path="clusters/:id" element={<ClusterDetailPage />} />
        <Route path="assessments" element={<AssessmentsPage />} />
        <Route path="approvals" element={<ApprovalsPage />} />
        <Route path="knowledge" element={<KnowledgePage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}

export default App
