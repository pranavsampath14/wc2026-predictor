import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { GROUPS, API_NAME_MAP, TEAM_CODES } from '../data/tournamentData'
import ReactCountryFlag from 'react-country-flag'
import PredictionPanel from '../components/PredictionPanel'

const API_URL = 'http://localhost:5001/predict'

export default function Group() {
  const { groupId } = useParams()
  const navigate = useNavigate()
  const [openMatch, setOpenMatch] = useState(null)

  const group = GROUPS[groupId?.toUpperCase()]


  if (!group) {
    return (
      <div className="not-found">
        <p>Group "{groupId}" not found.</p>
        <button onClick={() => navigate('/')}>Back to home</button>
      </div>
    )
  }


  function toggleMatch(idx) {
    setOpenMatch(prev => (prev === idx ? null : idx))
  }

  return (
    <div className="group-page">
      {group.matches.map((match, idx) => (
        <div key={idx} className='match-item' onClick={() => toggleMatch(idx)}>
          {/* home country flag + name */}
          <div className='match-display'>
            <div className='team-details'>
              <ReactCountryFlag countryCode={TEAM_CODES[match.home]} svg style={{ width: '1.75em', height: '1.75em' }} />
              <span>{match.home}</span>
            </div>
            {/* game details (date & time) */}
            <div className='game-details'>
              <div className='game-timing'>
                <span>{match.date}</span>
                <span>{match.timeAEST} AEST</span>
              </div>
              <div className='game-location'>
                {match.venue}
              </div>
            </div>
            {/* away country flag + name */}
            <div className='team-details away'>
              <span>{match.away}</span>
              <ReactCountryFlag countryCode={TEAM_CODES[match.away]} svg style={{ width: '1.75em', height: '1.75em' }} />
            </div>

          </div>
          
          {openMatch === idx && (
            <PredictionPanel home = {match.home} away={match.away}/>
          )}
        </div>
      ))}
    </div>
  )
}
