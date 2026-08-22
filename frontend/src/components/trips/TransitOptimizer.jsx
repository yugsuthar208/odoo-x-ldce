import React, { useState } from 'react';
import { tripService } from '../../services/tripService';
import { useToast } from '../common/Toast';
import { Train, Plane, Bus, Car, Clock, Compass, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function TransitOptimizer({ trip, onRefresh }) {
  const { addToast } = useToast();
  const [selectedMode, setSelectedMode] = useState('all');
  const [loadingLeg, setLoadingLeg] = useState(null);

  const getModeIcon = (mode) => {
    switch (mode?.toLowerCase()) {
      case 'train': return <Train className="w-5 h-5 text-amber-500" />;
      case 'flight': return <Plane className="w-5 h-5 text-blue-500" />;
      case 'bus': return <Bus className="w-5 h-5 text-emerald-500" />;
      case 'cab': return <Car className="w-5 h-5 text-purple-500" />;
      default: return <Compass className="w-5 h-5 text-neutral-400" />;
    }
  };

  const handleSelectOption = async (legId, optionId) => {
    setLoadingLeg(legId);
    try {
      await tripService.selectTransitOption(trip.id, legId, optionId);
      addToast({ message: "Transit option selected & budget updated!" });
      if (onRefresh) onRefresh();
    } catch (err) {
      addToast({ message: err.message || "Failed to select option", type: "error" });
    } finally {
      setLoadingLeg(null);
    }
  };

  if (!trip?.transit_legs || trip.transit_legs.length === 0) {
    return (
      <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 text-center text-neutral-400">
        Add some stops to your trip to generate transit options automatically!
      </div>
    );
  }

  // Helper to find city names
  const getCityName = (stopId) => {
    if (!stopId) return trip.origin_city || "Origin";
    const stop = trip.stops?.find(s => s.id === stopId);
    return stop?.city_name || "Unknown City";
  };

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="pb-4 border-b border-neutral-800">
        <h2 className="text-xl font-bold text-white mt-1">Multi-Modal Travel</h2>
        <p className="text-sm text-neutral-400">Select your preferred transport for each leg of the journey.</p>
      </div>

      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {['all', 'train', 'flight', 'bus', 'cab'].map((mode) => (
          <button
            key={mode}
            onClick={() => setSelectedMode(mode)}
            className={`px-3 py-1 text-xs rounded-lg font-medium transition capitalize cursor-pointer ${
              selectedMode === mode
                ? 'bg-amber-500 text-black font-semibold'
                : 'bg-neutral-800/60 text-neutral-400 hover:bg-neutral-800'
            }`}
          >
            {mode === 'all' ? 'All Modes' : mode}
          </button>
        ))}
      </div>

      {trip.transit_legs.map((leg) => (
        <div key={leg.id} className="space-y-4">
          <div className="flex items-center gap-3 bg-neutral-950/80 px-4 py-2.5 rounded-xl border border-neutral-800/80">
            <span className="text-sm font-semibold text-white">{getCityName(leg.from_stop_id)}</span>
            <ArrowRight className="w-4 h-4 text-amber-400" />
            <span className="text-sm font-semibold text-amber-400">{getCityName(leg.to_stop_id)}</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {leg.options
              .filter(opt => selectedMode === 'all' || opt.mode === selectedMode)
              .map(opt => {
                const isSelected = leg.selected_option_id === opt.id;
                return (
                  <div
                    key={opt.id}
                    className={`bg-neutral-950 border ${isSelected ? 'border-amber-500 shadow-md shadow-amber-500/10' : 'border-neutral-800'} rounded-xl p-4.5 flex flex-col justify-between transition relative`}
                  >
                    {isSelected && (
                      <div className="absolute -top-2 -right-2 bg-amber-500 text-black p-1 rounded-full shadow-lg">
                        <CheckCircle2 className="w-4 h-4" />
                      </div>
                    )}
                    <div>
                      <div className="flex items-center gap-2.5">
                        <div className="p-2 bg-neutral-900 rounded-lg border border-neutral-800">
                          {getModeIcon(opt.mode)}
                        </div>
                        <div>
                          <h4 className="text-sm font-bold text-white">{opt.provider}</h4>
                          <div className="flex items-center gap-2 text-xs text-neutral-400 mt-0.5">
                            <Clock className="w-3.5 h-3.5" />
                            <span>~{opt.duration_hours}h</span>
                          </div>
                        </div>
                      </div>

                      <div className="mt-4 flex items-center justify-between p-2.5 bg-neutral-900/90 rounded-lg border border-neutral-800/80 text-xs">
                        <div className="text-amber-400 font-bold text-sm">
                          ₹{opt.cost_per_person.toLocaleString('en-IN')}
                          <span className="text-[10px] text-neutral-400 font-normal"> / person</span>
                        </div>
                        <div className="text-[11px] text-neutral-400">
                          Total: ₹{opt.total_estimated_cost.toLocaleString('en-IN')}
                        </div>
                      </div>
                    </div>

                    <button
                      disabled={loadingLeg === leg.id}
                      onClick={() => handleSelectOption(leg.id, opt.id)}
                      className={`mt-4 w-full py-2 rounded-lg text-xs font-semibold transition ${
                        isSelected 
                          ? 'bg-amber-500/10 text-amber-500 border border-amber-500/30' 
                          : 'bg-neutral-800 hover:bg-neutral-700 text-white'
                      }`}
                    >
                      {loadingLeg === leg.id ? "Updating..." : isSelected ? "Selected" : "Select Option"}
                    </button>
                  </div>
                );
              })}
          </div>
        </div>
      ))}
    </div>
  );
}
