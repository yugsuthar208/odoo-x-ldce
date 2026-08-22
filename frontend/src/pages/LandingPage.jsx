import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import "./LandingPage.css";

// Utility for scroll animations
function useScrollReveal() {
  const [elements, setElements] = useState([]);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 }
    );

    const targetElements = document.querySelectorAll('.scroll-reveal');
    targetElements.forEach((el) => observer.observe(el));
    setElements(targetElements);

    return () => {
      targetElements.forEach((el) => observer.unobserve(el));
    };
  }, []);
}

function AnimatedCounter({ end, duration = 2000 }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);

  useEffect(() => {
    let startTime;
    let observer;
    let hasRun = false;

    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = timestamp - startTime;
      const percentage = Math.min(progress / duration, 1);
      
      // Easing function: easeOutQuart
      const easeOut = 1 - Math.pow(1 - percentage, 4);
      setCount(Math.floor(easeOut * end));

      if (progress < duration) {
        requestAnimationFrame(animate);
      } else {
        setCount(end);
      }
    };

    observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && !hasRun) {
        hasRun = true;
        requestAnimationFrame(animate);
      }
    }, { threshold: 0.5 });

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => {
      if (observer && ref.current) observer.unobserve(ref.current);
    };
  }, [end, duration]);

  return <span ref={ref}>{count}</span>;
}

export default function LandingPage() {
  useScrollReveal();

  const handleMouseMove = (e) => {
    const mockup = document.getElementById('hero-mockup');
    if (!mockup) return;
    
    // Parallax drift based on mouse position
    const { clientX, clientY } = e;
    const { innerWidth, innerHeight } = window;
    
    const x = (clientX / innerWidth - 0.5) * 12; // max 6px drift
    const y = (clientY / innerHeight - 0.5) * 12;

    mockup.style.transform = `translate(${x}px, ${y}px)`;
  };

  return (
    <div className="landing-page" onMouseMove={handleMouseMove}>
      
      {/* 1. Hero Section */}
      <section className="hero">
        <div className="hero-content scroll-reveal">
          <h1 className="hero-title">Plan trips that plan themselves</h1>
          <p className="hero-subtitle">
            Say goodbye to chaotic spreadsheets. TRIPORA uses AI to build your itinerary, predict your budget, and keep your group in sync.
          </p>
          <div className="hero-actions">
            <Link to="/signup" className="btn btn--accent">Start planning free</Link>
            <a href="#how-it-works" className="btn btn--ghost">See how it works</a>
          </div>
        </div>
        
        <div className="hero-mockup-container scroll-reveal" style={{ transitionDelay: "200ms" }}>
          <div className="browser-mockup" id="hero-mockup" style={{ transition: "transform 0.1s ease-out" }}>
            <div className="browser-header">
              <div className="browser-dot"></div>
              <div className="browser-dot"></div>
              <div className="browser-dot"></div>
            </div>
            <div className="browser-content skeleton-ui">
              TRIPORA DASHBOARD MOCKUP
            </div>
          </div>
        </div>
      </section>

      {/* 2. Feature Sections */}
      <div id="how-it-works">
        <section className="landing-section feature-section scroll-reveal">
          <div className="feature-text">
            <h2>The perfect route, mapped out</h2>
            <p>Visualize your entire journey on an interactive map. Adjust stops, reorganize days, and let TRIPORA optimize the travel time between your destinations.</p>
            <div className="feature-stat">15+</div>
            <p style={{ marginTop: '8px', fontSize: '0.875rem' }}>Map styles available</p>
          </div>
          <div className="feature-visual">
            <div className="browser-mockup">
              <div className="browser-header">
                <div className="browser-dot"></div><div className="browser-dot"></div><div className="browser-dot"></div>
              </div>
              <div className="browser-content skeleton-ui" style={{ height: "400px" }}>MAP VIEW MOCKUP</div>
            </div>
          </div>
        </section>

        <section className="landing-section feature-section reverse scroll-reveal">
          <div className="feature-text">
            <h2>AI-Powered Budget Predictor</h2>
            <p>Stop guessing how much you'll spend. Our trained ML model analyzes historical travel data to predict your exact costs across accommodation, food, and transport.</p>
            <div className="feature-stat">94%</div>
            <p style={{ marginTop: '8px', fontSize: '0.875rem' }}>Prediction Accuracy</p>
          </div>
          <div className="feature-visual">
            <div className="browser-mockup">
              <div className="browser-header">
                <div className="browser-dot"></div><div className="browser-dot"></div><div className="browser-dot"></div>
              </div>
              <div className="browser-content skeleton-ui" style={{ height: "400px" }}>BUDGET PREDICTOR MOCKUP</div>
            </div>
          </div>
        </section>

        <section className="landing-section feature-section scroll-reveal">
          <div className="feature-text">
            <h2>Discover your next obsession</h2>
            <p>Browse highly-curated destinations based on your travel style. Filter by region, budget index, and popularity to find the perfect spot.</p>
            <div className="feature-stat">20+</div>
            <p style={{ marginTop: '8px', fontSize: '0.875rem' }}>Curated Destinations</p>
          </div>
          <div className="feature-visual">
            <div className="browser-mockup">
              <div className="browser-header">
                <div className="browser-dot"></div><div className="browser-dot"></div><div className="browser-dot"></div>
              </div>
              <div className="browser-content skeleton-ui" style={{ height: "400px" }}>EXPLORE GRID MOCKUP</div>
            </div>
          </div>
        </section>
      </div>

      {/* 3. Stats Strip */}
      <section className="stats-strip scroll-reveal">
        <div className="stats-grid">
          <div className="stat-item">
            <h3><AnimatedCounter end={20} />+</h3>
            <p>Destinations</p>
          </div>
          <div className="stat-item">
            <h3><AnimatedCounter end={100} />+</h3>
            <p>Activities</p>
          </div>
          <div className="stat-item">
            <h3><AnimatedCounter end={50} />k</h3>
            <p>Trips Planned</p>
          </div>
        </div>
      </section>

      {/* 4. Testimonials */}
      <section className="landing-section testimonials scroll-reveal">
        <h2>Don't just take our word for it</h2>
        <div className="testimonials-grid">
          <div className="testimonial-card">
            <p className="testimonial-quote">"TRIPORA completely changed how I plan my solo trips. The budget predictor was spot on for my week in Tokyo."</p>
            <div className="testimonial-author">
              <div className="testimonial-avatar">A</div>
              <div>
                <div className="testimonial-name">Aisha</div>
                <div className="testimonial-title">Solo Traveler</div>
              </div>
            </div>
          </div>
          <div className="testimonial-card">
            <p className="testimonial-quote">"Finally, a tool that lets our whole friend group collaborate in real-time without using a messy spreadsheet."</p>
            <div className="testimonial-author">
              <div className="testimonial-avatar">M</div>
              <div>
                <div className="testimonial-name">Marcus</div>
                <div className="testimonial-title">Group Trip Organizer</div>
              </div>
            </div>
          </div>
          <div className="testimonial-card">
            <p className="testimonial-quote">"The interactive map view is a lifesaver. Being able to see how far apart activities are saved us so much transit time."</p>
            <div className="testimonial-author">
              <div className="testimonial-avatar">S</div>
              <div>
                <div className="testimonial-name">Sarah</div>
                <div className="testimonial-title">Digital Nomad</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 5. Final CTA */}
      <section className="final-cta scroll-reveal">
        <h2>Ready to build your itinerary?</h2>
        <Link to="/signup" className="btn btn--accent" style={{ fontSize: '1.125rem', padding: '16px 32px' }}>
          Create your first trip
        </Link>
        <p style={{ marginTop: '16px', color: 'rgba(255,255,255,0.6)' }}>Free during beta</p>
      </section>

      {/* 6. Footer */}
      <footer className="footer scroll-reveal">
        <div className="footer-logo">TRIPORA</div>
        <div className="footer-links">
          <a href="#">About</a>
          <a href="#">Features</a>
          <a href="#">Privacy</a>
          <a href="#">Terms</a>
        </div>
      </footer>
    </div>
  );
}
