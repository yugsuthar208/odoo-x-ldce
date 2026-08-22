import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, MapPin, Globe, ChevronDown, ArrowRight, ArrowLeft, Menu, Star, Route, Calculator, Compass } from 'lucide-react';
import './LandingPage.css';

export default function LandingPage() {
  const navigate = useNavigate();

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    navigate('/explore');
  };

  return (
    <div className="lp-wrapper">
      {/* Navbar - Uses existing links */}
      <nav className="lp-navbar">
        <div className="lp-nav-left">
          <a href="#how-it-works">Features</a>
          <a href="#destinations">Destinations</a>
          <a href="#">Privacy</a>
          <a href="#">Terms</a>
        </div>
        <div className="lp-nav-center">
          <span className="lp-logo-text">TRIPORA</span>
        </div>
        <div className="lp-nav-right">
          <Link to="/login" className="lp-lang-btn" style={{ textDecoration: 'none' }}>Log In</Link>
          <Link to="/signup" className="lp-btn-talk">Start Planning</Link>
          <button className="lp-menu-btn">
            <Menu size={20} />
          </button>
        </div>
      </nav>

      {/* Hero Section - Uses existing messaging */}
      <section className="lp-hero-section">
        <div className="lp-hero-container">
          <img 
            src="https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=2940&auto=format&fit=crop" 
            alt="Cinematic landscape" 
            className="lp-hero-bg" 
          />
          <div className="lp-hero-overlay"></div>

          <h1 className="lp-hero-title" style={{ fontSize: '13vw' }}>TRIPORA</h1>
          
          <div className="lp-hero-content">
            <div className="lp-hero-left">
              <p className="lp-hero-subtitle" style={{ textTransform: 'uppercase' }}>
                Plan trips that<br/>
                plan themselves<br/>
                <span style={{ fontSize: '14px', opacity: 0.8, textTransform: 'none', display: 'block', marginTop: '8px' }}>Say goodbye to chaotic spreadsheets.</span>
              </p>
              {/* Existing function: Start planning free -> /signup */}
              <Link to="/signup" className="lp-btn-start">
                <div className="lp-btn-icon"><ArrowRight size={14} color="#000" /></div>
                <span>START PLANNING FREE</span>
              </Link>
            </div>
            
            <div className="lp-hero-center">
              <div className="lp-scroll-indicator">
                <div className="lp-mouse">
                  <div className="lp-wheel"></div>
                </div>
                <span>See how it works</span>
              </div>
            </div>
            
            <div className="lp-hero-right">
              <div className="lp-hero-thumbnail">
                <img 
                  src="https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?q=80&w=600&auto=format&fit=crop" 
                  alt="Thumbnail destination" 
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Floating Search Bar - Mapped to ExplorePage functionality */}
      <div className="lp-search-wrapper">
        <form onSubmit={handleSearchSubmit} className="lp-search-bar">
          <div className="lp-search-field">
            <MapPin size={20} className="lp-field-icon" />
            <div className="lp-field-text">
              <label>Search cities...</label>
            </div>
          </div>
          <div className="lp-search-divider"></div>
          <div className="lp-search-field">
            <Globe size={20} className="lp-field-icon" />
            <div className="lp-field-text">
              <label>Region (All)</label>
            </div>
            <ChevronDown size={16} className="lp-chevron" />
          </div>
          <button type="submit" className="lp-search-submit">
            <Search size={20} color="#fff" />
          </button>
        </form>
      </div>

      {/* Recommended Destinations - Uses actual seed data from project */}
      <section className="lp-destinations" id="destinations">
        <div className="lp-section-header">
          <h2>Curated Destinations</h2>
          <div className="lp-slider-controls">
            <button className="lp-slider-btn"><ArrowLeft size={18}/></button>
            <button className="lp-slider-btn"><ArrowRight size={18}/></button>
          </div>
        </div>
        
        <div className="lp-cards-grid">
          {/* Card 1: Paris */}
          <div className="lp-card">
            <div className="lp-card-image-wrap">
              <img src="https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800" alt="Paris" />
              <div className="lp-badge lp-badge-top-right">
                <span className="lp-flag">🇫🇷</span> France
              </div>
              <div className="lp-badge lp-badge-bottom-left">
                <span className="lp-star">★</span> 9.8
              </div>
            </div>
            <div className="lp-card-body">
              <h3>Paris</h3>
              <p>The City of Light is renowned for its world-class art, fashion, gastronomy, and culture...</p>
              <Link to="/explore" className="lp-card-cta">
                View Destination <ArrowRight size={14} className="lp-cta-arrow"/>
              </Link>
            </div>
          </div>

          {/* Card 2: Rome */}
          <div className="lp-card">
            <div className="lp-card-image-wrap">
              <img src="https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800" alt="Rome" />
              <div className="lp-badge lp-badge-top-right">
                <span className="lp-flag">🇮🇹</span> Italy
              </div>
              <div className="lp-badge lp-badge-bottom-left">
                <span className="lp-star">★</span> 9.6
              </div>
            </div>
            <div className="lp-card-body">
              <h3>Rome</h3>
              <p>A living open-air museum boasting nearly 3,000 years of globally influential art and architecture...</p>
              <Link to="/explore" className="lp-card-cta">
                View Destination <ArrowRight size={14} className="lp-cta-arrow"/>
              </Link>
            </div>
          </div>

          {/* Card 3: Tokyo */}
          <div className="lp-card">
            <div className="lp-card-image-wrap">
              <img src="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=800" alt="Tokyo" />
              <div className="lp-badge lp-badge-top-right">
                <span className="lp-flag">🇯🇵</span> Japan
              </div>
              <div className="lp-badge lp-badge-bottom-left">
                <span className="lp-star">★</span> 9.9
              </div>
            </div>
            <div className="lp-card-body">
              <h3>Tokyo</h3>
              <p>Mixes ultra-modern skyscrapers and neon signs with historic temples. A culinary capital...</p>
              <Link to="/explore" className="lp-card-cta">
                View Destination <ArrowRight size={14} className="lp-cta-arrow"/>
              </Link>
            </div>
          </div>

          {/* Card 4: Bali */}
          <div className="lp-card">
            <div className="lp-card-image-wrap">
              <img src="https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800" alt="Bali" />
              <div className="lp-badge lp-badge-top-right">
                <span className="lp-flag">🇮🇩</span> Indonesia
              </div>
              <div className="lp-badge lp-badge-bottom-left">
                <span className="lp-star">★</span> 9.5
              </div>
            </div>
            <div className="lp-card-body">
              <h3>Bali</h3>
              <p>An island paradise known for its forested volcanic mountains, iconic rice paddies, and coral reefs...</p>
              <Link to="/explore" className="lp-card-cta">
                View Destination <ArrowRight size={14} className="lp-cta-arrow"/>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section - Uses existing "How it works" content */}
      <section className="lp-elevate" id="how-it-works">
        <div className="lp-elevate-left">
          <h2>The perfect route, mapped out</h2>
          <p className="lp-elevate-desc">
            Visualize your entire journey on an interactive map. Adjust stops, reorganize days, and let our AI optimize the travel time between your destinations.
          </p>
          
          <div className="lp-features-grid">
            <div className="lp-feature">
              <div className="lp-feature-icon-wrapper"><Calculator size={20}/></div>
              <div>
                <h4>AI-Powered Budget Predictor</h4>
                <p>Stop guessing how much you'll spend. Our trained ML model predicts your exact costs.</p>
              </div>
            </div>
            <div className="lp-feature">
              <div className="lp-feature-icon-wrapper"><Compass size={20}/></div>
              <div>
                <h4>Discover your next obsession</h4>
                <p>Browse highly-curated destinations based on your travel style and region.</p>
              </div>
            </div>
          </div>
        </div>
        <div className="lp-elevate-right">
          <div className="lp-elevate-image-wrap">
            <img 
              src="https://images.unsplash.com/photo-1524661135-423995f22d0b?q=80&w=800&auto=format&fit=crop" 
              alt="Interactive Map Visualization" 
            />
            <div className="lp-elevate-badge lp-badge-tl">
              <Route size={14} style={{ marginRight: '6px' }} /> 15+ Map Styles
            </div>
            <div className="lp-elevate-badge lp-badge-tr">
              94% Accuracy
            </div>
          </div>
        </div>
      </section>

      {/* Kept Functionality: Stats Strip & Testimonials (Restyled to match reference aesthetic) */}
      <section className="lp-stats-section">
        <div className="lp-stats-grid">
          <div className="lp-stat">
            <h3>20+</h3>
            <p>Destinations</p>
          </div>
          <div className="lp-stat">
            <h3>100+</h3>
            <p>Activities</p>
          </div>
          <div className="lp-stat">
            <h3>50k</h3>
            <p>Trips Planned</p>
          </div>
        </div>
      </section>

      <section className="lp-testimonials">
        <h2 style={{ textAlign: 'center', marginBottom: '40px', fontSize: '32px' }}>Don't just take our word for it</h2>
        <div className="lp-testimonials-grid">
          <div className="lp-testimonial-card">
            <p className="lp-testimonial-quote">"TRIPORA completely changed how I plan my solo trips. The budget predictor was spot on for my week in Tokyo."</p>
            <div className="lp-testimonial-author">
              <div className="lp-avatar">A</div>
              <div>
                <div className="lp-author-name">Aisha</div>
                <div className="lp-author-title">Solo Traveler</div>
              </div>
            </div>
          </div>
          <div className="lp-testimonial-card">
            <p className="lp-testimonial-quote">"Finally, a tool that lets our whole friend group collaborate in real-time without using a messy spreadsheet."</p>
            <div className="lp-testimonial-author">
              <div className="lp-avatar">M</div>
              <div>
                <div className="lp-author-name">Marcus</div>
                <div className="lp-author-title">Group Trip Organizer</div>
              </div>
            </div>
          </div>
          <div className="lp-testimonial-card">
            <p className="lp-testimonial-quote">"The interactive map view is a lifesaver. Being able to see how far apart activities are saved us so much transit time."</p>
            <div className="lp-testimonial-author">
              <div className="lp-avatar">S</div>
              <div>
                <div className="lp-author-name">Sarah</div>
                <div className="lp-author-title">Digital Nomad</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer - Uses existing links */}
      <footer className="lp-footer">
        <div className="lp-footer-content">
          <div className="lp-footer-logo">TRIPORA</div>
          <div className="lp-footer-links">
            <a href="#how-it-works">Features</a>
            <a href="#destinations">About</a>
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
