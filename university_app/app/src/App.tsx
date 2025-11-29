import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'sonner'
import { AuthProvider } from './contexts/AuthContext'
import Index from './pages/Index'

function App() {
  return (
    <AuthProvider>
    <Router>
      <Routes>
        <Route path="/" element={<Index />} />
      </Routes>
      <Toaster />
    </Router>
    </AuthProvider>
  )
}

export default App

