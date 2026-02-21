import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './features/auth/AuthContext';
import Layout from './components/layout/Layout';
import MatrizResumen from './features/dashboard/MatrizResumen';
import TraceabilityView from './features/dashboard/TraceabilityView';
import RiskView from './features/risk/RiskView';
import TimeAnalysisView from './features/dashboard/TimeAnalysisView';
import KPIsTab from './features/dashboard/KPIsTab';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = React.useState({
    company_id: 'TENANT_001',
    username: 'admin',
    password: 'admin123'
  });

  const [loading, setLoading] = React.useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    const result = await login(formData.username, formData.password, formData.company_id);
    if (result.success) {
      navigate('/');
    } else {
      alert("Login failed: " + (result.message || "Check credentials"));
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="glass-card p-8 w-full max-w-md">
        <h2 className="text-2xl font-bold text-center mb-6 text-primary">SECURE ACCESS</h2>
        <p className="text-center text-xs text-slate-400 mb-8 font-mono tracking-widest">RESTRICTED AREA // FORENSIC SYSTEM</p>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">ID Empresa</label>
            <input
              type="text"
              name="company_id"
              value={formData.company_id}
              onChange={handleChange}
              className="input-field bg-slate-50"
              placeholder="TENANT_ID"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Usuario</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="input-field bg-slate-50"
              placeholder="Usuario"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Contraseña</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="input-field bg-slate-50"
              placeholder="••••••••"
            />
          </div>

          <button type="submit" disabled={loading} className="w-full btn-primary mt-6 py-3 font-bold tracking-wide shadow-lg shadow-primary/30">
            {loading ? 'AUTENTICANDO...' : 'INGRESAR AL SISTEMA'}
          </button>
        </form>
      </div>
    </div>
  );
};

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) return <div className="flex h-screen items-center justify-center">Cargando...</div>;

  if (!user) return <Navigate to="/login" replace />;

  return children;
};

import DetalleUUIDView from './features/dashboard/DetalleUUIDView';
import KoniaAnalitica from './features/dashboard/KoniaAnalitica';

const PlaceholderView = ({ title }) => (
  <div className="p-8">
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center">
      <h2 className="text-2xl font-bold text-slate-400 mb-2 uppercase tracking-widest">{title}</h2>
      <p className="text-slate-500">Módulo en proceso de migración para la plataforma KONIA.</p>
    </div>
  </div>
);

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route path="/" element={
            <ProtectedRoute>
              <Layout>
                <MatrizResumen />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/detalle-uuid" element={
            <ProtectedRoute>
              <Layout>
                <DetalleUUIDView />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/trazabilidad/:uuid" element={
            <ProtectedRoute>
              <Layout>
                <TraceabilityView />
              </Layout>
            </ProtectedRoute>
          } />



          <Route path="/trazabilidad" element={
            <ProtectedRoute>
              <Layout>
                <TraceabilityView />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/analisis-temporal" element={
            <ProtectedRoute>
              <Layout>
                <TimeAnalysisView />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/riesgos/:uuid" element={
            <ProtectedRoute>
              <Layout>
                <RiskView />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/riesgos" element={
            <ProtectedRoute>
              <Layout>
                <RiskView />
              </Layout>
            </ProtectedRoute>
          } />

          {/* New Dropdown Routes */}
          <Route path="/kpis" element={
            <ProtectedRoute>
              <Layout titre="Indicadores Clave (KPIS)">
                <KPIsTab />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/analitica/:subtab?" element={
            <ProtectedRoute>
              <Layout titre="Analítica Avanzada">
                <KoniaAnalitica />
              </Layout>
            </ProtectedRoute>
          } />

          {[
            { path: '/prellenado', title: 'Prellenado de Declaraciones' },
            { path: '/analisis-estructural', title: 'Análisis Estructural' },
            { path: '/tendencias', title: 'Tendencias y Pronósticos' },
            { path: '/materialidad', title: 'Materialidad CFDI' },
            { path: '/materialidad/documentos', title: 'Gestión de Documentos' },
            { path: '/materialidad/seguimiento', title: 'Seguimiento REPSE' },
            { path: '/riesgos/ranking', title: 'Ranking de Riesgo' },
            { path: '/compliance', title: 'Compliance Fiscal' },
            { path: '/compliance/integridad', title: 'Integridad de Flujo' },
            { path: '/compliance/saldos', title: 'Saldos y Devoluciones' },
            { path: '/compliance/pagos', title: 'Pagos Provisionales' },
            { path: '/configuracion', title: 'Configuración General' },
            { path: '/configuracion/modelos', title: 'Gestión de Modelos AI' },
          ].map(route => (
            <Route
              key={route.path}
              path={route.path}
              element={
                <ProtectedRoute>
                  <Layout titre={route.title}>
                    <PlaceholderView title={route.title} />
                  </Layout>
                </ProtectedRoute>
              }
            />
          ))}

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
