import './LandingPage.css'

const SCHOOLS = [
  ['JGLS', 'Jindal Global Law School', '#1 Law School in India, 5 years running'],
  ['JGBS', 'Jindal Global Business School', '14 programmes, 120+ global partners'],
  ['JSIA', "Jindal School of International Affairs", "India's First Global Policy School"],
  ['JSGP', 'Jindal School of Government & Public Policy', 'Economics, Public Policy, Ph.D.'],
  ['JSLH', 'Jindal School of Liberal Arts & Humanities', '10+ majors, dual degrees abroad'],
  ['JSJC', 'Jindal School of Journalism & Communication', 'Journalism, Film, Corporate Comms'],
  ['JSAA', 'Jindal School of Art & Architecture', 'B.Arch, B.Des, global pathways'],
  ['JSBF', 'Jindal School of Banking & Finance', 'B.Com, Finance, Capital Markets'],
]

const QUICK_LINKS = [
  ['Admissions', 'Entrance tests, eligibility & how to apply'],
  ['Fee Structure', 'Programme fees, hostel & payment schedules'],
  ['Academic Calendar', 'Semester dates, exams & holidays 2024-25'],
  ['Hostel & Campus Life', 'Residence halls, dining & amenities'],
]

export default function LandingPage({ onAskAssistant }) {
  return (
    <div className="lp">
      <header className="lp-nav">
        <div className="lp-nav-inner">
          <span className="lp-logo">JGU</span>
          <nav className="lp-nav-links">
            <a href="#schools">Schools</a>
            <a href="#admissions">Admissions</a>
            <a href="#campus">Campus Life</a>
            <a href="#contact">Contact</a>
          </nav>
          <button className="lp-nav-cta" onClick={onAskAssistant}>Ask JGU Assistant</button>
        </div>
      </header>

      <section className="lp-hero">
        <div className="lp-hero-copy">
          <p className="lp-eyebrow">Institution of Eminence &middot; Est. 2009</p>
          <h1>O.P. Jindal Global University</h1>
          <p className="lp-sub">
            A non-profit, research-intensive global university in Sonipat, India —
            12 interdisciplinary schools, 13,000+ students, faculty from 50+ countries.
          </p>
          <div className="lp-hero-actions">
            <button className="lp-btn-primary" onClick={onAskAssistant}>
              Ask the AI Assistant
            </button>
            <a className="lp-btn-ghost" href="#admissions">Explore Admissions</a>
          </div>
        </div>
        <div className="lp-hero-ledger">
          <div className="ledger-row"><span>Ranking</span><strong>#1 Private University, India (QS 2023)</strong></div>
          <div className="ledger-row"><span>Schools</span><strong>12 + 4 research institutes</strong></div>
          <div className="ledger-row"><span>Students</span><strong>13,000+ from every Indian state &amp; 50+ countries</strong></div>
          <div className="ledger-row"><span>Faculty</span><strong>1,200+ full-time</strong></div>
          <div className="ledger-row"><span>Global ties</span><strong>450+ collaborations, 75+ countries</strong></div>
        </div>
      </section>

      <section className="lp-quicklinks" id="admissions">
        {QUICK_LINKS.map(([title, desc]) => (
          <button key={title} className="quicklink-card" onClick={onAskAssistant}>
            <span className="quicklink-title">{title}</span>
            <span className="quicklink-desc">{desc}</span>
            <span className="quicklink-arrow">Ask the assistant &rarr;</span>
          </button>
        ))}
      </section>

      <section className="lp-schools" id="schools">
        <h2>Twelve Schools, One University</h2>
        <div className="schools-grid">
          {SCHOOLS.map(([code, name, note]) => (
            <div key={code} className="school-card">
              <span className="school-code">{code}</span>
              <h3>{name}</h3>
              <p>{note}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="lp-campus" id="campus">
        <h2>Campus Life</h2>
        <div className="campus-grid">
          <div className="campus-item"><h4>Global Library</h4><p>~79,000+ volumes and extensive electronic databases across schools.</p></div>
          <div className="campus-item"><h4>Wellness &amp; Health</h4><p>JGU Health Centre, Centre for Wellness &amp; Counselling (CWCS), SUKOON mental health centre.</p></div>
          <div className="campus-item"><h4>Dining &amp; Residence</h4><p>Vidya Devi Jindal Dining Block (7,000+ capacity), double/triple/four-sharing halls of residence.</p></div>
          <div className="campus-item"><h4>Career Services</h4><p>Office of Career Services (OCS) plus school-level career and professional development teams.</p></div>
        </div>
      </section>

      <footer className="lp-footer" id="contact">
        <div>
          <strong>O.P. Jindal Global University</strong>
          <p>Sonipat Narela Road, Sonipat, Haryana, India &middot; www.jgu.edu.in</p>
        </div>
        <button className="lp-btn-primary" onClick={onAskAssistant}>Have a question? Ask the AI Assistant</button>
      </footer>
    </div>
  )
}
