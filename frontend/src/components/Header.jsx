import { useNavigate, useLocation } from 'react-router-dom'

export default function Header() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <header>
      <div className='inner-header'>
        <div className='header-title'>WC 2026 Predictor</div>
        <div className='header-nav'>
          <button className={'nav-tab'}
            style={{
              backgroundColor: location.pathname === '/' ? 'rgba(55,138,221,0.25)' : 'transparent',
              borderColor: location.pathname === '/' ? 'rgba(55,138,221,0.5)' : 'transparent',
              color: location.pathname === '/' ? 'white' : 'rgba(255,255,255,0.5)',
            }}
              onClick={()=> navigate("/")
            }
          >
            Predict
          </button>

          <button className={'nav-tab'}
            style={{
              backgroundColor: location.pathname === '/simulation' ? 'rgba(55,138,221,0.25)' : 'transparent',
              borderColor: location.pathname === '/simulation' ? 'rgba(55,138,221,0.5)' : 'transparent',
              color: location.pathname === '/simulation' ? 'white' : 'rgba(255,255,255,0.5)',
            }}
              onClick={()=> navigate("/simulation")
            }
          >
            Simulation
          </button>
          {/* <div className='header-name'>Pranav Sampath</div> */}
        </div>
      </div>
    </header>
  )
}