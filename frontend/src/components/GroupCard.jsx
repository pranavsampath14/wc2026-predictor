import { useNavigate } from 'react-router-dom'
import ReactCountryFlag from 'react-country-flag'
import { TEAM_CODES } from '../data/tournamentData'

const GROUP_ACCENTS = {
  A: '#c0392b', B: '#d35400', C: '#b7950b', D: '#1a6fa8',
  E: '#1e8449', F: '#148a8a', G: '#7d3c98', H: '#c0397a',
  I: '#b7770d', J: '#2471a3', K: '#1a7a4a', L: '#ba4a00',
}

export default function GroupCard({ id, group }) {
  const navigate = useNavigate()
  const accent = GROUP_ACCENTS[id]

  return (
    <div className='group-card' onClick={() => navigate(`/group/${id}`)}>
      <div className='card-accent-bar' style={{ background: accent }}>
          <span className='card-letter'>{id}</span>
      </div>
      <div className='card-teams'>
          {group.teams.map((team, i) => (
          <div key={team} className='card-team'>
            <span>{team}</span>
            <ReactCountryFlag countryCode={TEAM_CODES[team]} svg style={{ width: '1.75em', height: '1.75em' }} />
            
          </div>
          ))}
      </div>
    </div>
  )
}