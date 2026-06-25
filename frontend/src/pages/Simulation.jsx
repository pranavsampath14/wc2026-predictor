import { useState, useEffect } from 'react'
import ReactCountryFlag from 'react-country-flag'
import { TEAM_CODES } from '../data/tournamentData'

const API_URL = 'https://wc2026-predictor-15jf.onrender.com/simulate'

function TeamRow({ rank, team, prob, maxProb, color }) {
  return (
    <div className='sim-team-row'>
      <span className='sim-rank'>{rank}</span>
      <ReactCountryFlag countryCode={TEAM_CODES[team]} svg style={{ width: '1.1em', height: '1.1em' }} />
      <span className='sim-team-name'>{team}</span>
      <div className='sim-bar-track'>
        <div className='sim-bar-fill' style={{ width: `${(prob / maxProb) * 100}%`, background: color }} />
      </div>
      <span className='sim-prob-val'>{Math.round(prob * 100)}%</span>
    </div>
  )
}

function StageSection({ title, teams, color }) {
  const maxProb = teams[0][1]
  return (
    <div className='sim-stage-section'>
      <p className='sim-section-label'>{title}</p>
      {teams.map(([team, prob], i) => (
        <TeamRow key={team} rank={i + 1} team={team} prob={prob} maxProb={maxProb} color={color} />
      ))}
    </div>
  )
}

export default function Simulation() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(API_URL)
      .then(res => res.json())
      .then(json => {
        setData(json)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className='simulation-page'><span className='sim-loading'>Loading simulation...</span></div>
  }

  const sorted = (key) => Object.entries(data)
    .map(([team, stats]) => [team, stats[key]])
    .sort((a, b) => b[1] - a[1])

  const top4Winners = sorted('winner').slice(0, 4)
  const top4Finals = sorted('final').slice(0, 4)
  const top4Semis = sorted('sf').slice(0, 4)
  const top4QF = sorted('qf').slice(0, 4)
  const top8QF = sorted('qf').slice(0, 8)

  const finalist1 = sorted('final')[0][0]
  const finalist2 = sorted('final')[1][0]
  const finalist1WinProb = data[finalist1].winner
  const finalist2WinProb = data[finalist2].winner

  return (
    <div className='simulation-page'>

      {/* Hero winner banner */}
      <div className='sim-hero'>
        <div className='sim-hero-label'>World Cup winner</div>
        <div className='sim-hero-team'>
          <ReactCountryFlag countryCode={TEAM_CODES[top4Winners[0][0]]} svg style={{ width: '3em', height: '3em' }} />
          <span className='sim-hero-name'>{top4Winners[0][0]}</span>
        </div>
        <div className='sim-hero-prob'>{Math.round(top4Winners[0][1] * 100)}% probability</div>
      </div>

      {/* Most likely final */}
      <p className='sim-section-label'>Most likely final</p>
      <div className='sim-final-card'>
        <div className='sim-finalist'>
          <ReactCountryFlag countryCode={TEAM_CODES[finalist1]} svg style={{ width: '2em', height: '2em' }} />
          <div>
            <div className='sim-finalist-name'>{finalist1}</div>
            <div className='sim-finalist-prob'>{Math.round(finalist1WinProb * 100)}% to win</div>
          </div>
        </div>
        <span className='sim-vs-badge'>FINAL</span>
        <div className='sim-finalist sim-finalist--right'>
          <div style={{ textAlign: 'right' }}>
            <div className='sim-finalist-name'>{finalist2}</div>
            <div className='sim-finalist-prob'>{Math.round(finalist2WinProb * 100)}% to win</div>
          </div>
          <ReactCountryFlag countryCode={TEAM_CODES[finalist2]} svg style={{ width: '2em', height: '2em' }} />
        </div>
      </div>

      {/* Top semifinalists */}
      <p className='sim-section-label'>Top semifinalists</p>
      <div className='sim-semi-card'>
        {sorted('sf').slice(0, 4).map(([team, prob], i) => (
          <div key={team} className='sim-semi-team'>
            <span className='sim-semi-rank'>{i + 1}</span>
            <ReactCountryFlag countryCode={TEAM_CODES[team]} svg style={{ width: '1.2em', height: '1.2em' }} />
            <span className='sim-semi-name'>{team}</span>
            <div className='sim-semi-bar-track'>
              <div className='sim-semi-bar-fill' style={{ width: `${(prob / sorted('sf')[0][1]) * 100}%` }} />
            </div>
            <span className='sim-semi-prob'>{Math.round(prob * 100)}%</span>
          </div>
        ))}
      </div>

      {/* Top 8 QF */}
      <p className='sim-section-label'>Top 8 quarterfinalists</p>
      <div className='sim-qf-grid'>
        {top8QF.map(([team, prob]) => (
          <div key={team} className='sim-qf-card'>
            <ReactCountryFlag countryCode={TEAM_CODES[team]} svg style={{ width: '1.8em', height: '1.8em' }} />
            <div className='sim-qf-name'>{team}</div>
            <div className='sim-qf-prob'>{Math.round(prob * 100)}% QF</div>
          </div>
        ))}
      </div>

    </div>
  )
}