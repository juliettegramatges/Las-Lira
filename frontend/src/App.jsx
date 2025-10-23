import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Layout from './components/common/Layout'
import TableroPage from './pages/TableroPage'
import InventarioPage from './pages/InventarioPage'
import ProductosPage from './pages/ProductosPage'
import PedidosPage from './pages/PedidosPage'
import ClientesPage from './pages/ClientesPage'
import RutasPage from './pages/RutasPage'
import CobranzaPage from './pages/CobranzaPage'
import TallerPage from './pages/TallerPage'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/tablero" replace />} />
          <Route path="tablero" element={<TableroPage />} />
          <Route path="pedidos" element={<PedidosPage />} />
          <Route path="taller" element={<TallerPage />} />
          <Route path="clientes" element={<ClientesPage />} />
          <Route path="cobranza" element={<CobranzaPage />} />
          <Route path="rutas" element={<RutasPage />} />
          <Route path="inventario" element={<InventarioPage />} />
          <Route path="productos" element={<ProductosPage />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App

