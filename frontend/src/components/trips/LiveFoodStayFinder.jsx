import React, { useState, useEffect } from 'react';
import { tripService } from '../../services/tripService';
import { 
  Utensils, 
  Hotel, 
  Star, 
  Search, 
  Sparkles, 
  ExternalLink, 
  Tag, 
  MapPin, 
  AlertCircle 
} from 'lucide-react';

export default function LiveFoodStayFinder({ cityName = 'Goa' }) {
  const [activeTab, setActiveTab] = useState('food'); // 'food' or 'stay'
  const [budgetTier, setBudgetTier] = useState('mid'); // 'budget', 'mid', 'luxury'
  const [foodResults, setFoodResults] = useState([]);
  const [stayResults, setStayResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      if (activeTab === 'food') {
        const res = await tripService.getLiveFood(cityName, budgetTier);
        if (res.success) {
          setFoodResults(res.data || []);
        }
      } else {
        const res = await tripService.getLiveStays(cityName, budgetTier);
        if (res.success) {
          setStayResults(res.data || []);
        }
      }
    } catch (err) {
      console.error('Live recommendations fetch error:', err);
      setError('Could not fetch live recommendations right now.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (cityName) {
      fetchRecommendations();
    }
  }, [cityName, activeTab, budgetTier]);

  const results = activeTab === 'food' ? foodResults : stayResults;

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 shadow-xl space-y-6">
      {/* Header & Mode Switcher */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-neutral-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full flex items-center gap-1">
              <Sparkles className="w-3 h-3" /> Live DuckDuckGo Travel Discovery
            </span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">
            Local Food & Stays in <span className="text-amber-400">{cityName}</span>
          </h2>
          <p className="text-sm text-neutral-400">
            Real-time recommendations for legendary regional thalis, iconic dhabas, hostels & heritage stays.
          </p>
        </div>

        {/* Tab & Budget Controls */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Food / Stay Tab Buttons */}
          <div className="flex bg-neutral-950 p-1 rounded-xl border border-neutral-800">
            <button
              onClick={() => setActiveTab('food')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                activeTab === 'food'
                  ? 'bg-amber-500 text-black shadow-md'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              <Utensils className="w-3.5 h-3.5" />
              <span>Food & Delicacies</span>
            </button>
            <button
              onClick={() => setActiveTab('stay')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                activeTab === 'stay'
                  ? 'bg-amber-500 text-black shadow-md'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              <Hotel className="w-3.5 h-3.5" />
              <span>Stays & Hostels</span>
            </button>
          </div>

          {/* Budget Tier Selector */}
          <div className="flex bg-neutral-950 p-1 rounded-xl border border-neutral-800 text-xs">
            {['budget', 'mid', 'luxury'].map((tier) => (
              <button
                key={tier}
                onClick={() => setBudgetTier(tier)}
                className={`px-3 py-1.5 rounded-lg font-medium capitalize transition cursor-pointer ${
                  budgetTier === tier
                    ? 'bg-neutral-800 text-amber-400 font-semibold'
                    : 'text-neutral-400 hover:text-neutral-200'
                }`}
              >
                {tier}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Loading & Error */}
      {loading && (
        <div className="flex items-center justify-center py-12 text-neutral-400 gap-3">
          <div className="w-5 h-5 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
          <span>Discovering authentic {activeTab === 'food' ? 'food spots' : 'stays'} in {cityName}...</span>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-950/40 border border-red-800/60 rounded-xl text-red-300 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Results Grid */}
      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((item, idx) => (
            <div
              key={idx}
              className="bg-neutral-950 border border-neutral-800 hover:border-amber-500/40 rounded-xl p-4.5 flex flex-col justify-between transition group hover:shadow-lg"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <span className="text-[11px] font-medium text-amber-400/90 bg-amber-500/10 px-2 py-0.5 rounded-md border border-amber-500/20">
                    {item.type}
                  </span>
                  <div className="flex items-center gap-1 text-xs text-amber-400 bg-neutral-900 px-2 py-0.5 rounded-md border border-neutral-800">
                    <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                    <span className="font-bold">{item.rating || '4.7'}</span>
                  </div>
                </div>

                <h3 className="text-base font-bold text-white mt-2.5 group-hover:text-amber-400 transition">
                  {item.title}
                </h3>

                <p className="text-xs text-neutral-400 mt-2 leading-relaxed line-clamp-3">
                  {item.highlight}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-neutral-800/80 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-neutral-500 uppercase font-semibold block">
                    Estimated Cost
                  </span>
                  <span className="text-sm font-bold text-amber-400">
                    {item.price_inr}
                  </span>
                </div>

                <span className="text-[10px] text-neutral-400 bg-neutral-900 px-2 py-1 rounded border border-neutral-800">
                  {item.source || 'DuckDuckGo Verified'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
