import { useState, useEffect } from 'react'
import ReactCountryFlag from 'react-country-flag'
import { TEAM_CODES } from '../data/tournamentData'

const API_URL = 'http://localhost:5001/predict'

export default function PredictionPanel({ home, away }) {
  const [state, setState] = useState('loading')
  const [result, setResult] = useState(null)

  useEffect(() => {
    fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ home_team: home, away_team: away })
    })
      .then(res => res.json())
      .then(data => {
        setResult(data)
        setState('done')
      })
      .catch(() => setState('error'))
  }, [home, away])

  if (state === 'loading') {
    return (
      <div className='prediction-panel'>
        <span className='prediction-loading'>Running prediction...</span>
      </div>
    )
  }

  if (state === 'error') {
    return (
      <div className='prediction-panel'>
        <span className='prediction-error'>Could not reach API — make sure Flask is running on port 5001</span>
      </div>
    )
  }

  const homeProb = result[home] ?? 0
  const awayProb = result[away] ?? 0
  const drawProb = result['draw'] ?? 0

  const maxProb = Math.max(homeProb, drawProb, awayProb)

  return (
    <div className='prediction-panel'>
      <div className='prob-row'>
        <div className='prob-team'>
          <span className={homeProb === maxProb ? 'prob-label winner' : 'prob-label'}>{home}</span>
        </div>
        <div className='prob-track'>
          <div className='prob-fill home' style={{ width: `${Math.round(homeProb * 100)}%` }} />
        </div>
        <span className='prob-pct'>{Math.round(homeProb * 100)}%</span>
      </div>

      <div className='prob-row'>
        <div className='prob-team'>
          <span className='prob-label'>Draw</span>
        </div>
        <div className='prob-track'>
          <div className='prob-fill draw' style={{ width: `${Math.round(drawProb * 100)}%` }} />
        </div>
        <span className='prob-pct'>{Math.round(drawProb * 100)}%</span>
      </div>

      <div className='prob-row'>
        <div className='prob-team'>
          <span className={awayProb === maxProb ? 'prob-label winner' : 'prob-label'}>{away}</span>
        </div>
        <div className='prob-track'>
          <div className='prob-fill away' style={{ width: `${Math.round(awayProb * 100)}%` }} />
        </div>
        <span className='prob-pct'>{Math.round(awayProb * 100)}%</span>
      </div>
    </div>
  )
}