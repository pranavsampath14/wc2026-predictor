import { useNavigate } from 'react-router-dom'
import { GROUPS } from '../data/tournamentData'
import GroupCard from '../components/GroupCard'
import centreTrophy from '../assets/centre-trophy-2.png'
import logo from '../assets/logo-1.webp'

const GROUP_ACCENTS = {
  A: '#e84040', B: '#f07020', C: '#f5c518', D: '#378ADD',
  E: '#22c97a', F: '#00bcd4', G: '#a78bfa', H: '#f472b6',
  I: '#f59e0b', J: '#60a5fa', K: '#34d399', L: '#fb923c',
}

export default function Home() {
  const groupEntries = Object.entries(GROUPS)



  return (
    <div className="home">
      <div className='groups-grid'>
        {groupEntries.map(([id, group]) => (
          <GroupCard key={id} id={id} group={group} />
        ))}
      </div>
    </div>
  )

}