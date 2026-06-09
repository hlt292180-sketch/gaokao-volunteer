import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import ScoreConvert from './pages/ScoreConvert'
import UniversityList from './pages/UniversityList'
import UniversityDetail from './pages/UniversityDetail'
import MajorList from './pages/MajorList'
import MajorDetail from './pages/MajorDetail'
import Assessment from './pages/Assessment'
import VolunteerCheck from './pages/VolunteerCheck'
import PlanGenerate from './pages/PlanGenerate'
import PlanList from './pages/PlanList'
import PlanDetail from './pages/PlanDetail'
import Profile from './pages/Profile'
import Upgrade from './pages/Upgrade'
import Admin from './pages/Admin'
import Disclaimer from './pages/Disclaimer'
import About from './pages/About'
import Contact from './pages/Contact'
import MyFavorites from './pages/MyFavorites'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
          <Route path="score-convert" element={<ScoreConvert />} />
          <Route path="universities" element={<UniversityList />} />
          <Route path="universities/:id" element={<UniversityDetail />} />
          <Route path="majors" element={<MajorList />} />
          <Route path="majors/:id" element={<MajorDetail />} />
          <Route path="assessment" element={<ProtectedRoute><Assessment /></ProtectedRoute>} />
          <Route path="volunteer-check" element={<ProtectedRoute><VolunteerCheck /></ProtectedRoute>} />
          <Route path="plan/generate" element={<ProtectedRoute><PlanGenerate /></ProtectedRoute>} />
          <Route path="plans" element={<ProtectedRoute><PlanList /></ProtectedRoute>} />
          <Route path="plans/:id" element={<ProtectedRoute><PlanDetail /></ProtectedRoute>} />
          <Route path="profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="upgrade" element={<ProtectedRoute><Upgrade /></ProtectedRoute>} />
          <Route path="admin" element={<ProtectedRoute><Admin /></ProtectedRoute>} />
          <Route path="disclaimer" element={<Disclaimer />} />
          <Route path="about" element={<About />} />
          <Route path="contact" element={<Contact />} />
          <Route path="my-favorites" element={<ProtectedRoute><MyFavorites /></ProtectedRoute>} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
