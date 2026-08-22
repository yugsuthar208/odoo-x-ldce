import React, { useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, MapPin, Globe, ChevronDown, ArrowRight, ArrowLeft, Menu, Star, Route, Calculator, Compass, Sparkles, Map, CalendarClock } from 'lucide-react';
import { motion, useScroll, useTransform, useMotionValue, useSpring } from 'framer-motion';
import './LandingPage.css';

// --- 3D Tilt Card Component ---
function TiltCard({ children }) {
  const ref = useRef(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  
  const springConfig = { damping: 20, stiffness: 300, mass: 0.5 };
  const mouseXSpring = useSpring(x, springConfig);
  const mouseYSpring = useSpring(y, springConfig);
  
  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["15deg", "-15deg"]);
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-15deg", "15deg"]);

  const handleMouseMove = (e) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const xPct = mouseX / width - 0.5;
    const yPct = mouseY / height - 0.5;
    x.set(xPct);
    y.set(yPct);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        rotateX,
        rotateY,
        transformStyle: "preserve-3d",
      }}
      whileHover={{ scale: 1.05, zIndex: 10 }}
      className="lp-card-tilt-wrapper"
    >
      <div style={{ transform: "translateZ(30px)", height: "100%" }}>
        {children}
      </div>
    </motion.div>
  );
}

// --- Main Page Component ---
export default function LandingPage() {
  const navigate = useNavigate();
  const { scrollY } = useScroll();
  
  const heroY = useTransform(scrollY, [0, 1000], [0, 400]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    navigate('/explore');
  };

  const fadeUp = {
    hidden: { opacity: 0, y: 40 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } }
  };
  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.15 }
    }
  };

  return (
    <div className="lp-wrapper">
      {/* Navbar */}
      <motion.nav 
        className="lp-navbar glass-nav"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <div className="lp-nav-left">
          <a href="#how-it-works" className="hover-link">Features</a>
          <a href="#destinations" className="hover-link">Destinations</a>
          <a href="#ai-magic" className="hover-link">AI Magic</a>
          <a href="#" className="hover-link">Privacy</a>
        </div>
        <div className="lp-nav-center">
          <span className="lp-logo-text magnetic-text">TRIPORA</span>
        </div>
        <div className="lp-nav-right">
          <Link to="/login" className="lp-lang-btn hover-link" style={{ textDecoration: 'none' }}>Log In</Link>
          <Link to="/signup" className="lp-btn-talk glow-on-hover">Start Planning</Link>
          <button className="lp-menu-btn">
            <Menu size={20} />
          </button>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section className="lp-hero-section overflow-hidden">
        <div className="lp-hero-container">
          <motion.img 
            style={{ y: heroY }}
            src="https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=2940&auto=format&fit=crop" 
            alt="Cinematic landscape" 
            className="lp-hero-bg parallax-img" 
          />
          <div className="lp-hero-overlay"></div>

          <motion.h1 
            className="lp-hero-title" 
            style={{ fontSize: '13vw' }}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 1.2, ease: "easeOut" }}
          >
            TRIPORA
          </motion.h1>
          
          <div className="lp-hero-content">
            <motion.div 
              className="lp-hero-left"
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 1, delay: 0.5 }}
            >
              <p className="lp-hero-subtitle" style={{ textTransform: 'uppercase' }}>
                Plan trips that<br/>
                plan themselves<br/>
                <span className="subtitle-sm" style={{ fontSize: '14px', opacity: 0.8, textTransform: 'none', display: 'block', marginTop: '8px' }}>Say goodbye to chaotic spreadsheets.</span>
              </p>
              <Link to="/signup" className="lp-btn-start btn-magnetic">
                <div className="lp-btn-icon"><ArrowRight size={14} color="#000" /></div>
                <span>START PLANNING FREE</span>
              </Link>
            </motion.div>
            
            <motion.div 
              className="lp-hero-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.5, duration: 1 }}
            >
              <div className="lp-scroll-indicator">
                <div className="lp-mouse">
                  <motion.div 
                    className="lp-wheel"
                    animate={{ y: [0, 10, 0] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                  />
                </div>
                <span>See how it works</span>
              </div>
            </motion.div>
            
            <motion.div 
              className="lp-hero-right"
              initial={{ x: 50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 1, delay: 0.5 }}
            >
              <div className="lp-hero-thumbnail float-animation">
                <img 
                  src="https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?q=80&w=600&auto=format&fit=crop" 
                  alt="Thumbnail destination" 
                />
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Floating Search Bar */}
      <motion.div 
        className="lp-search-wrapper"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 1, duration: 0.8 }}
      >
        <form onSubmit={handleSearchSubmit} className="lp-search-bar glass-panel">
          <div className="lp-search-field hover-glow">
            <MapPin size={20} className="lp-field-icon text-accent" />
            <div className="lp-field-text">
              <label>Search cities...</label>
            </div>
          </div>
          <div className="lp-search-divider"></div>
          <div className="lp-search-field hover-glow">
            <Globe size={20} className="lp-field-icon text-accent" />
            <div className="lp-field-text">
              <label>Region (All)</label>
            </div>
            <ChevronDown size={16} className="lp-chevron" />
          </div>
          <button type="submit" className="lp-search-submit glow-on-hover">
            <Search size={20} color="#fff" />
          </button>
        </form>
      </motion.div>

      {/* Recommended Destinations */}
      <motion.section 
        className="lp-destinations" 
        id="destinations"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={fadeUp}
      >
        <div className="lp-section-header">
          <h2>Curated Destinations</h2>
          <div className="lp-slider-controls">
            <button className="lp-slider-btn btn-magnetic"><ArrowLeft size={18}/></button>
            <button className="lp-slider-btn btn-magnetic"><ArrowRight size={18}/></button>
          </div>
        </div>
        
        <motion.div className="lp-cards-grid hide-scrollbar" variants={staggerContainer}>
          {[
            { name: 'Paris', country: 'France', flag: '🇫🇷', score: '9.8', img: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800', desc: 'The City of Light is renowned for its world-class art, fashion, gastronomy, and culture.' },
            { name: 'Rome', country: 'Italy', flag: '🇮🇹', score: '9.6', img: 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800', desc: 'A living open-air museum boasting nearly 3,000 years of globally influential art and architecture.' },
            { name: 'Tokyo', country: 'Japan', flag: '🇯🇵', score: '9.9', img: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=800', desc: 'Mixes ultra-modern skyscrapers and neon signs with historic temples. A culinary capital.' },
            { name: 'Bali', country: 'Indonesia', flag: '🇮🇩', score: '9.5', img: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800', desc: 'An island paradise known for its forested volcanic mountains, iconic rice paddies, and coral reefs.' },
            { name: 'Prague', country: 'Czech Rep', flag: '🇨🇿', score: '9.3', img: 'https://images.unsplash.com/photo-1519677100203-a0e668c92439?w=800', desc: 'Known as the City of a Hundred Spires, featuring colorful baroque buildings and Gothic churches.' },
            { name: 'Vienna', country: 'Austria', flag: '🇦🇹', score: '9.4', img: 'https://images.unsplash.com/photo-1516550893923-42d28e5677af?w=800', desc: 'Austria’s capital lies in the country’s east on the Danube River. Known for its Imperial palaces.' },
            { name: 'Lisbon', country: 'Portugal', flag: '🇵🇹', score: '9.5', img: 'https://images.unsplash.com/photo-1548707309-dcebe6120111?w=800', desc: 'A coastal capital city known for its cafe culture and soulful Fado music.' },
            { name: 'Athens', country: 'Greece', flag: '🇬🇷', score: '9.2', img: 'https://images.unsplash.com/photo-1518105779142-d9715649bbde?w=800', desc: 'The heart of Ancient Greece, a powerful civilization and empire.' },
          ].map((city, i) => (
            <motion.div key={i} variants={fadeUp}>
              <TiltCard>
                <div className="lp-card glass-card">
                  <div className="lp-card-image-wrap">
                    <img src={city.img} alt={city.name} className="scale-on-hover" />
                    <div className="lp-badge lp-badge-top-right glass-badge">
                      <span className="lp-flag">{city.flag}</span> {city.country}
                    </div>
                    <div className="lp-badge lp-badge-bottom-left glass-badge text-accent">
                      <span className="lp-star">★</span> {city.score}
                    </div>
                  </div>
                  <div className="lp-card-body">
                    <h3>{city.name}</h3>
                    <p>{city.desc}</p>
                    <Link to="/explore" className="lp-card-cta hover-underline">
                      View Destination <ArrowRight size={14} className="lp-cta-arrow"/>
                    </Link>
                  </div>
                </div>
              </TiltCard>
            </motion.div>
          ))}
        </motion.div>
      </motion.section>

      {/* NEW: Travel Styles Section (Alternating Layout) */}
      <section className="vibe-section" style={{ padding: "140px 5%", maxWidth: "1400px", margin: "0 auto" }}>
        <motion.div 
          style={{ textAlign: "center", marginBottom: "100px" }}
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
        >
          <h2 style={{ fontSize: "4.5rem", letterSpacing: "-2px", marginBottom: "24px", lineHeight: 1.1 }}>
            Curate your <span className="gradient-text">vibe.</span>
          </h2>
          <p style={{ fontSize: "1.25rem", color: "var(--ink-soft)", maxWidth: "650px", margin: "0 auto", lineHeight: 1.6 }}>
            Our AI engine deeply understands your unique travel persona. Explore the aesthetic and experiential modalities we perfectly pair with your state of mind.
          </p>
        </motion.div>

        <div style={{ display: "flex", flexDirection: "column", gap: "140px" }}>
          {[
            { 
              name: "Adventure", category: "Thrill & Action", 
              img: "https://images.unsplash.com/photo-1522199755839-a2bacb67c546?q=80&w=800&auto=format&fit=crop", 
              desc: "For those who chase adrenaline. Discover hidden trails, conquer peaks, and experience raw nature. Our engine filters out the noise to put you right in the center of the action.",
              tags: ["Hiking", "Extreme Sports", "Off-Grid"]
            },
            { 
              name: "Luxury", category: "Elegance & Comfort",
              img: "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?q=80&w=800&auto=format&fit=crop", 
              desc: "Five-star everything. From private infinity pools to Michelin-starred dining, we curate exclusive experiences that define opulence and pristine service.",
              tags: ["Resorts", "Fine Dining", "First Class"]
            },
            { 
              name: "Cultural", category: "History & Art",
              img: "https://images.unsplash.com/photo-1518398046578-8cca57782e17?q=80&w=800&auto=format&fit=crop", 
              desc: "Immerse yourself in history. Walk through ancient ruins, explore world-renowned museums, and connect with local traditions and vibrant artistic communities.",
              tags: ["Museums", "Heritage", "Local Cuisine"]
            },
            { 
              name: "Relaxation", category: "Wellness & Peace",
              img: "https://images.unsplash.com/photo-1540541338287-41700207dee6?q=80&w=800&auto=format&fit=crop", 
              desc: "Unplug and unwind. Serene beaches, silent mountain retreats, and holistic wellness centers designed to rejuvenate your mind, body, and spirit.",
              tags: ["Spa", "Beaches", "Mindfulness"]
            }
          ].map((style, i) => {
            const isEven = i % 2 === 0;
            return (
              <div key={i} className={`vibe-row ${!isEven ? 'reverse' : ''}`}>
                <motion.div 
                  className="vibe-row-img"
                  style={{ height: "550px", borderRadius: "32px", overflow: "hidden", boxShadow: "0 30px 60px rgba(0,0,0,0.12)" }}
                  initial={{ opacity: 0, x: isEven ? -80 : 80, scale: 0.95 }}
                  whileInView={{ opacity: 1, x: 0, scale: 1 }}
                  viewport={{ once: true, margin: "-100px" }}
                  transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                >
                  <img src={style.img} alt={style.name} style={{ width: "100%", height: "100%", objectFit: "cover" }} className="scale-on-hover" />
                </motion.div>
                
                <motion.div 
                  className="vibe-row-content"
                  initial={{ opacity: 0, x: isEven ? 80 : -80 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: "-100px" }}
                  transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1], delay: 0.1 }}
                >
                  <div style={{ display: "inline-block", padding: "8px 16px", background: "var(--surface)", borderRadius: "99px", color: "var(--ink-soft)", fontWeight: 600, fontSize: "0.85rem", letterSpacing: "2px", textTransform: "uppercase", marginBottom: "24px", border: "1px solid rgba(0,0,0,0.05)" }}>
                    0{i+1} — {style.category}
                  </div>
                  <h3 style={{ fontSize: "3.5rem", fontWeight: 700, letterSpacing: "-1.5px", marginBottom: "24px", lineHeight: 1.1 }}>
                    {style.name}
                  </h3>
                  <p style={{ fontSize: "1.2rem", color: "var(--ink-soft)", lineHeight: 1.7, marginBottom: "40px" }}>
                    {style.desc}
                  </p>
                  
                  <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
                    {style.tags.map(tag => (
                      <span key={tag} className="glass-badge" style={{ padding: "10px 20px", borderRadius: "12px", fontSize: "0.95rem", fontWeight: 500, color: "var(--ink)", border: "1px solid rgba(0,0,0,0.06)", display: "flex", alignItems: "center", gap: "6px" }}>
                        <Sparkles size={14} color="var(--ink-soft)" /> {tag}
                      </span>
                    ))}
                  </div>
                </motion.div>
              </div>
            )
          })}
        </div>
      </section>

      {/* AI Itinerary Magic Section */}
      <motion.section 
        className="lp-ai-magic" 
        id="ai-magic"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={fadeUp}
      >
        <div className="lp-ai-container glass-panel-dark">
          <div className="lp-ai-content">
            <Sparkles size={32} className="text-accent float-animation" style={{ color: '#fff' }} />
            <h2 className="gradient-text-light">Intelligent Itinerary Generation</h2>
            <p>Our machine learning engine builds personalized day-by-day plans in seconds. We optimize travel routes, predict precise budget requirements, and match activities exactly to your vibe.</p>
            
            <div className="lp-ai-stats">
              <motion.div className="ai-stat-box" whileHover={{ scale: 1.05 }}>
                <Map className="mb-2" size={24} color="#fff" />
                <h4>Smart Routing</h4>
                <span>Eliminates zigzagging across the city</span>
              </motion.div>
              <motion.div className="ai-stat-box" whileHover={{ scale: 1.05 }}>
                <CalendarClock className="mb-2" size={24} color="#fff" />
                <h4>Pacing Engine</h4>
                <span>Ensures you're never rushed or bored</span>
              </motion.div>
            </div>
          </div>
          <div className="lp-ai-visual">
            <TiltCard>
              <img src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800" alt="Data Visualization" className="rounded-xl shadow-2xl ai-image" />
            </TiltCard>
          </div>
        </div>
      </motion.section>

      {/* Features Section */}
      <motion.section 
        className="lp-elevate" 
        id="how-it-works"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={fadeUp}
      >
        <div className="lp-elevate-left">
          <h2>The perfect route, mapped out</h2>
          <p className="lp-elevate-desc">
            Visualize your entire journey on an interactive map. Adjust stops, reorganize days, and let our AI optimize the travel time between your destinations.
          </p>
          
          <div className="lp-features-grid">
            <motion.div className="lp-feature hover-lift" whileHover={{ y: -5 }}>
              <div className="lp-feature-icon-wrapper pulse-glow"><Calculator size={20}/></div>
              <div>
                <h4>AI-Powered Budget Predictor</h4>
                <p>Stop guessing how much you'll spend. Our trained ML model predicts your exact costs.</p>
              </div>
            </motion.div>
            <motion.div className="lp-feature hover-lift" whileHover={{ y: -5 }}>
              <div className="lp-feature-icon-wrapper pulse-glow"><Compass size={20}/></div>
              <div>
                <h4>Discover your next obsession</h4>
                <p>Browse highly-curated destinations based on your travel style and region.</p>
              </div>
            </motion.div>
          </div>
        </div>
        <div className="lp-elevate-right">
          <TiltCard>
            <div className="lp-elevate-image-wrap rounded-2xl overflow-hidden shadow-2xl glass-panel">
              <img 
                src="https://images.unsplash.com/photo-1524661135-423995f22d0b?q=80&w=800&auto=format&fit=crop" 
                alt="Interactive Map Visualization" 
                className="scale-on-hover"
              />
              <div className="lp-elevate-badge lp-badge-tl glass-badge-dark">
                <Route size={14} style={{ marginRight: '6px' }} /> 15+ Map Styles
              </div>
              <div className="lp-elevate-badge lp-badge-tr glass-badge-dark text-accent">
                94% Accuracy
              </div>
            </div>
          </TiltCard>
        </div>
      </motion.section>

      {/* Stats Strip */}
      <motion.section 
        className="lp-stats-section"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 1 }}
      >
        <div className="lp-stats-grid">
          {[ { num: '20+', label: 'Destinations' }, { num: '100+', label: 'Activities' }, { num: '50k', label: 'Trips Planned' } ].map((stat, i) => (
            <motion.div 
              key={i} 
              className="lp-stat hover-lift"
              initial={{ scale: 0.5, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.2, type: "spring", stiffness: 100 }}
              whileHover={{ y: -10 }}
            >
              <h3 className="gradient-text">{stat.num}</h3>
              <p>{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Testimonials */}
      <motion.section 
        className="lp-testimonials"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        variants={fadeUp}
      >
        <h2 style={{ textAlign: 'center', marginBottom: '40px', fontSize: '32px' }}>Don't just take our word for it</h2>
        <div className="lp-testimonials-grid">
          {[
            { quote: "TRIPORA completely changed how I plan my solo trips. The budget predictor was spot on for my week in Tokyo.", initials: "A", name: "Aisha", title: "Solo Traveler" },
            { quote: "Finally, a tool that lets our whole friend group collaborate in real-time without using a messy spreadsheet.", initials: "M", name: "Marcus", title: "Group Trip Organizer" },
            { quote: "The interactive map view is a lifesaver. Being able to see how far apart activities are saved us so much transit time.", initials: "S", name: "Sarah", title: "Digital Nomad" }
          ].map((test, i) => (
            <motion.div 
              key={i} 
              className="lp-testimonial-card glass-card hover-lift"
              variants={fadeUp}
              whileHover={{ y: -10, boxShadow: "0 25px 50px -12px rgba(0,0,0,0.15)" }}
            >
              <p className="lp-testimonial-quote">"{test.quote}"</p>
              <div className="lp-testimonial-author">
                <div className="lp-avatar">{test.initials}</div>
                <div>
                  <div className="lp-author-name">{test.name}</div>
                  <div className="lp-author-title">{test.title}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Footer */}
      <footer className="lp-footer">
        <div className="lp-footer-content">
          <div className="lp-footer-logo magnetic-text">TRIPORA</div>
          <div className="lp-footer-links">
            <a href="#how-it-works" className="hover-underline">Features</a>
            <a href="#destinations" className="hover-underline">About</a>
            <a href="#" className="hover-underline">Privacy</a>
            <a href="#" className="hover-underline">Terms</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
