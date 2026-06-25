import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Group from './pages/Group'
import Simulation from './pages/Simulation'
import Header from './components/Header'
import './index.css'

export default function App() {
  return (
    <>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/group/:groupId" element={<Group />} />
        <Route path="/simulation" element={<Simulation />} />
      </Routes>
    </>
  )
}