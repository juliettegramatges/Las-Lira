import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Layout from './components/common/Layout'
import TableroPage from './pages/TableroPage'
import InventarioPage from './pages/InventarioPage'
import ProductosPage from './pages/ProductosPage'
import PedidosPage from './pages/PedidosPage'
import RutasPage from './pages/RutasPage'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/tablero" replace />} />
          <Route path="tablero" element={<TableroPage />} />
          <Route path="pedidos" element={<PedidosPage />} />
          <Route path="rutas" element={<RutasPage />} />
          <Route path="inventario" element={<InventarioPage />} />
          <Route path="productos" element={<ProductosPage />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App

