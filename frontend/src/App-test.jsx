function App() {
  return (
    <div style={{
      padding: '20px',
      backgroundColor: '#f0f0f0',
      minHeight: '100vh'
    }}>
      <h1 style={{
        fontSize: '32px',
        color: '#333',
        marginBottom: '20px'
      }}>
        🌸 Las-Lira - Sistema de Gestión
      </h1>
      <p style={{
        fontSize: '18px',
        color: '#666'
      }}>
        Si ves este mensaje, React está funcionando correctamente.
      </p>
      <div style={{
        marginTop: '20px',
        padding: '15px',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ color: '#ca2d75', marginBottom: '10px' }}>✅ Sistema Activo</h2>
        <ul style={{ lineHeight: '1.8' }}>
          <li>Backend: http://localhost:8000</li>
          <li>Frontend: http://localhost:5174</li>
          <li>Estado: Funcionando</li>
        </ul>
      </div>
    </div>
  )
}

export default App

