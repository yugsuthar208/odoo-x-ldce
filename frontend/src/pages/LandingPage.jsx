import React from 'react';
import { Link } from 'react-router-dom';
import { Search, MapPin, Calendar, Mountain, ChevronDown, ArrowRight, ArrowLeft, Menu } from 'lucide-react';
import './LandingPage.css';

export default function LandingPage() {
  return (
    <div className="lp-wrapper">
      {/* Navbar */}
      <nav className="lp-navbar">
        <div className="lp-nav-left">
          <a href="#destinations">Destinations</a>
          <a href="#package">Package</a>
          <a href="#pricing">Pricing</a>
          <a href="#about">About Us</a>
        </div>
        <div className="lp-nav-center">
          <span className="lp-logo-text">GlobeTrotter</span>
        </div>
        <div className="lp-nav-right">
          <button className="lp-lang-btn">EN</button>
          <Link to="/login" className="lp-btn-talk">Let's Talk</Link>
          <button className="lp-menu-btn">
            <Menu size={20} />
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="lp-hero-section">
        <div className="lp-hero-container">
          <img 
            src="https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=2940&auto=format&fit=crop" 
            alt="Cinematic landscape" 
            className="lp-hero-bg" 
          />
          
          <div className="lp-hero-overlay"></div>

          <h1 className="lp-hero-title">GLOBETROTTER</h1>
          
          <div className="lp-hero-content">
            <div className="lp-hero-left">
              <p className="lp-hero-subtitle">
                EXPLORE THE<br/>
                BEAUTY OF NATURE<br/>
                LIKE NEVER BEFORE
              </p>
              <Link to="/signup" className="lp-btn-start">
                <div className="lp-btn-icon"><ArrowRight size={14} color="#000" /></div>
                <span>START YOUR JOURNEY</span>
              </Link>
            </div>
            
            <div className="lp-hero-center">
              <div className="lp-scroll-indicator">
                <div className="lp-mouse">
                  <div className="lp-wheel"></div>
                </div>
                <span>Scroll Now</span>
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
          
          <div className="lp-hero-carousel-controls">
            <button className="lp-carousel-btn"><ArrowLeft size={16}/></button>
            <div className="lp-carousel-dots">
              <span className="lp-dot active"></span>
              <span className="lp-dot"></span>
              <span className="lp-dot"></span>
            </div>
            <button className="lp-carousel-btn"><ArrowRight size={16}/></button>
          </div>
        </div>
      </section>

      {/* Floating Search Bar */}
      <div className="lp-search-wrapper">
        <div className="lp-search-bar">
          <div className="lp-search-field">
            <MapPin size={20} className="lp-field-icon" />
            <div className="lp-field-text">
              <label>City or address</label>
            </div>
          </div>
          <div className="lp-search-divider"></div>
          <div className="lp-search-field">
            <Calendar size={20} className="lp-field-icon" />
            <div className="lp-field-text">
              <label>Add Dates</label>
            </div>
          </div>
          <div className="lp-search-divider"></div>
          <div className="lp-search-field">
            <Mountain size={20} className="lp-field-icon" />
            <div className="lp-field-text">
              <label>Landscape Type</label>
            </div>
            <ChevronDown size={16} className="lp-chevron" />
          </div>
          <button className="lp-search-submit">
            <Search size={20} color="#fff" />
          </button>
        </div>
      </div>

      {/* Recommended Destinations */}
      <section className="lp-destinations" id="destinations">
        <div className="lp-section-header">
          <h2>Recommended Destination</h2>
          <div className="lp-slider-controls">
            <button className="lp-slider-btn"><ArrowLeft size={18}/></button>
            <button className="lp-slider-btn"><ArrowRight size={18}/></button>
          </div>
        </div>
        
        <div className="lp-cards-grid">
          {/* Card 1 */}
          <div className="lp-card">
            <div className="lp-card-image-wrap">
              <img src="https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?q=80&w=600" alt="Australia" />
              <div className="lp-badge lp-badge-top-right">
                <span className="lp-flag">🇦🇺</span> Australia
              </div>
              <div className="lp-badge lp-badge-bottom-left">
                <span className="lp-star">★</span> 4.9
              </div>
            </div>
            <div className="lp-card-body">
              <h3>Sunset Cruise in Whitehaven Beach</h3>
              <p>Sail through the stunning Whitsunday Islands with incredible ocean views...</p>
              <Link to="/explore" className="lp-card-cta">
                Booking Now <ArrowRight size={14} className="lp-cta-arrow"/>
              </Link>
            </div>
          </div>

          {/* Card 2 */}
          <div className="lp-card">
            <div className="lp-card-image-wrap">
              <img src="https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?q=80&w=600" alt="Switzerland" />
              <div className="lp-badge lp-badge-top-right">
                <span className="lp-flag">🇨🇭</span> Switzerland
              </div>
              <div className="lp-badge lp-badge-bottom-left">
                <span className="lp-star">★</span> 4.8
              </div>
            </div>
            <div className="lp-card-body">
              <h3>Mount Titlis and Lucerne Day Tour</h3>
              <p>Experience the snowy peaks of Mount Titlis and the beautiful city of Lucerne...</p>
              <Link to="/explore" className="lp-card-cta">
                Booking Now <ArrowRight size={14} className="lp-cta-arrow"/>
              </Link>
            </div>
          </div>

          {/* Card 3 */}
          <div className="lp-card">
            <div className="lp-card-image-wrap">
              <img src="https://images.unsplash.com/photo-1533105079780-92b9be482077?q=80&w=600" alt="Greece" />
              <div className="lp-badge lp-badge-top-right">
                <span className="lp-flag">🇬🇷</span> Greece
              </div>
              <div className="lp-badge lp-badge-bottom-left">
                <span className="lp-star">★</span> 4.9
              </div>
            </div>
            <div className="lp-card-body">
              <h3>Santorini Volcano and Hot Springs</h3>
              <p>Explore the volcanic islands and swim in the therapeutic hot springs...</p>
              <Link to="/explore" className="lp-card-cta">
                Booking Now <ArrowRight size={14} className="lp-cta-arrow"/>
              </Link>
            </div>
          </div>

          {/* Card 4 */}
          <div className="lp-card">
            <div className="lp-card-image-wrap">
              <img src="https://images.unsplash.com/photo-1527004013197-933c4bcc61f4?q=80&w=600" alt="Japan" />
              <div className="lp-badge lp-badge-top-right">
                <span className="lp-flag">🇯🇵</span> Japan
              </div>
              <div className="lp-badge lp-badge-bottom-left">
                <span className="lp-star">★</span> 4.7
              </div>
            </div>
            <div className="lp-card-body">
              <h3>Mount Fuji and Hakone Day Trip</h3>
              <p>See the iconic Mount Fuji and take a relaxing cruise on Lake Ashi...</p>
              <Link to="/explore" className="lp-card-cta">
                Booking Now <ArrowRight size={14} className="lp-cta-arrow"/>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Elevate Your Adventures */}
      <section className="lp-elevate" id="about">
        <div className="lp-elevate-left">
          <h2>Elevate Your Adventures</h2>
          <p className="lp-elevate-desc">
            Discover a world of new possibilities with GlobeTrotter. Your journey begins here, where every detail is crafted for your perfect experience. Let us guide you to the most breathtaking destinations on Earth.
          </p>
          
          <div className="lp-features-grid">
            <div className="lp-feature">
              <div className="lp-feature-icon-wrapper">✦</div>
              <div>
                <h4>Diving and Snorkeling</h4>
                <p>Explore the breathtaking underwater world with expert guides.</p>
              </div>
            </div>
            <div className="lp-feature">
              <div className="lp-feature-icon-wrapper">✧</div>
              <div>
                <h4>Professional Tour Guide</h4>
                <p>Connect with local experts who know the land perfectly.</p>
              </div>
            </div>
          </div>
        </div>
        <div className="lp-elevate-right">
          <div className="lp-elevate-image-wrap">
            <img 
              src="https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?q=80&w=800&auto=format&fit=crop" 
              alt="Norway Fjords" 
            />
            <div className="lp-elevate-badge lp-badge-tl">
              <span className="lp-flag">🇳🇴</span> Norway
            </div>
            <div className="lp-elevate-badge lp-badge-tr">
              Recommended
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="lp-footer">
        <div className="lp-footer-content">
          <div className="lp-footer-logo">GlobeTrotter</div>
          <div className="lp-footer-links">
            <a href="#destinations">Destinations</a>
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Contact Us</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
