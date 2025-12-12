import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Farm from './pages/Farm'
import Ponds from './pages/Ponds'
import Batches from './pages/Batches'
import Inventory from './pages/Inventory'
import DailyOperations from './pages/DailyOperations'
import Accounting from './pages/Accounting'
import Harvests from './pages/Harvests'
import SalesOrders from './pages/SalesOrders'
import Invoices from './pages/Invoices'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import AuditLogs from './pages/AuditLogs'
import BiologicalAssetRevaluations from './pages/BiologicalAssetRevaluations'
import Billing from './pages/Billing'
import SuperAdminDashboard from './pages/SuperAdminDashboard'
import ProtectedFeature from './components/common/ProtectedFeature'
import GlobalLoader from './components/common/GlobalLoader'
import ToastContainer from './components/common/ToastContainer'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return !isAuthenticated ? <>{children}</> : <Navigate to="/dashboard" replace />
}

function App() {
  return (
    <BrowserRouter>
      {/* Global UI Components */}
      <GlobalLoader />
      <ToastContainer />
      
      <Routes>
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/farm"
          element={
            <ProtectedRoute>
              <Farm />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ponds"
          element={
            <ProtectedRoute>
              <Ponds />
            </ProtectedRoute>
          }
        />
        <Route
          path="/batches"
          element={
            <ProtectedRoute>
              <Batches />
            </ProtectedRoute>
          }
        />
        <Route
          path="/inventory"
          element={
            <ProtectedRoute>
              <Inventory />
            </ProtectedRoute>
          }
        />
        <Route
          path="/operations"
          element={
            <ProtectedRoute>
              <DailyOperations />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <ProtectedFeature feature="reports">
                <Reports />
              </ProtectedFeature>
            </ProtectedRoute>
          }
        />
        <Route
          path="/accounting"
          element={
            <ProtectedRoute>
              <ProtectedFeature feature="accounting">
                <Accounting />
              </ProtectedFeature>
            </ProtectedRoute>
          }
        />
        <Route
          path="/harvests"
          element={
            <ProtectedRoute>
              <ProtectedFeature feature="sales">
                <Harvests />
              </ProtectedFeature>
            </ProtectedRoute>
          }
        />
        <Route
          path="/sales-orders"
          element={
            <ProtectedRoute>
              <ProtectedFeature feature="sales">
                <SalesOrders />
              </ProtectedFeature>
            </ProtectedRoute>
          }
        />
        <Route
          path="/invoices"
          element={
            <ProtectedRoute>
              <ProtectedFeature feature="sales">
                <Invoices />
              </ProtectedFeature>
            </ProtectedRoute>
          }
        />
        <Route
          path="/billing"
          element={
            <ProtectedRoute>
              <Billing />
            </ProtectedRoute>
          }
        />
        <Route
          path="/saas-admin"
          element={
            <ProtectedRoute>
              <SuperAdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/audit-logs"
          element={
            <ProtectedRoute>
              <ProtectedFeature feature="accounting">
                <AuditLogs />
              </ProtectedFeature>
            </ProtectedRoute>
          }
        />
        <Route
          path="/biological-asset-revaluations"
          element={
            <ProtectedRoute>
              <ProtectedFeature feature="accounting">
                <BiologicalAssetRevaluations />
              </ProtectedFeature>
            </ProtectedRoute>
          }
        />
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
