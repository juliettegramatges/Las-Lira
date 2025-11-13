import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
import Layout from './components/common/Layout'
import LoginPage from './pages/LoginPage'
import ProtectedRoute from './components/common/ProtectedRoute'
import TableroPage from './pages/TableroPage'
import InsumosPage from './pages/InsumosPage'
import ProductosPage from './pages/ProductosPage'
import PedidosPage from './pages/PedidosPage'
import ClientesPage from './pages/ClientesPage'
import RutasPage from './pages/RutasPage'
import CobranzaPage from './pages/CobranzaPage'
import TallerPage from './pages/TallerPage'
import SimuladorCostosPage from './pages/SimuladorCostosPage'
import EventosPage from './pages/EventosPage'
import ReportesPage from './pages/ReportesPage'
import AuditoriaPage from './pages/AuditoriaPage'
import './App.css'

function AppRoutes() {
  const { user, canAccess } = useAuth()

  return (
    <Routes>
      {/* Ruta pública de login */}
      <Route path="/login" element={<LoginPage />} />
      
      {/* Rutas protegidas */}
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/tablero" replace />} />
        
        {/* Rutas accesibles para todos los roles autenticados */}
        <Route 
          path="tablero" 
          element={
            <ProtectedRoute>
              <TableroPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="productos" 
          element={
            <ProtectedRoute>
              <ProductosPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="taller" 
          element={
            <ProtectedRoute>
              <TallerPage />
            </ProtectedRoute>
          } 
        />
        
        {/* Rutas solo para secretaria y admin */}
        {canAccess('cobranza') && (
          <Route 
            path="cobranza" 
            element={
              <ProtectedRoute>
                <CobranzaPage />
              </ProtectedRoute>
            } 
          />
        )}
        {canAccess('clientes') && (
          <Route 
            path="clientes" 
            element={
              <ProtectedRoute>
                <ClientesPage />
              </ProtectedRoute>
            } 
          />
        )}
        
        {/* Rutas solo para admin */}
        {user?.rol === 'admin' && (
          <>
            <Route 
              path="pedidos" 
              element={
                <ProtectedRoute>
                  <PedidosPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="eventos" 
              element={
                <ProtectedRoute>
                  <EventosPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="rutas" 
              element={
                <ProtectedRoute>
                  <RutasPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="inventario" 
              element={
                <ProtectedRoute>
                  <InsumosPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="simulador-costos" 
              element={
                <ProtectedRoute>
                  <SimuladorCostosPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="reportes" 
              element={
                <ProtectedRoute>
                  <ReportesPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="auditoria" 
              element={
                <ProtectedRoute>
                  <AuditoriaPage />
                </ProtectedRoute>
              } 
            />
          </>
        )}
        
        {/* Redirigir rutas no autorizadas */}
        <Route path="*" element={<Navigate to="/tablero" replace />} />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  )
}

export default App

