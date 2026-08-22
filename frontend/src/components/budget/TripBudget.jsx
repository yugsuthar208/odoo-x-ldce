import { useState, useEffect } from "react";
import { tripService } from "../../services/tripService";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import ExpenseList from "./ExpenseList";
import { DollarSign, AlertCircle, TrendingDown, Home, Utensils, Bus, Activity, CreditCard } from "lucide-react";

const COLORS = {
  stay: "#4f46e5",       // indigo-600
  food: "#f59e0b",       // amber-500
  transport: "#10b981",  // emerald-500
  activities: "#ec4899", // pink-500
  misc: "#6b7280"        // gray-500
};

const ICONS = {
  stay: Home,
  food: Utensils,
  transport: Bus,
  activities: Activity,
  misc: CreditCard
};

export default function TripBudget({ tripId, budget, onRefresh }) {
  const [budgetLimit, setBudgetLimit] = useState(budget?.budget_target?.toString() || "");

  const handleUpdateLimit = async () => {
    try {
      await tripService.updateTripBudget(tripId, { total_budget_limit: parseFloat(budgetLimit) });
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error(err);
    }
  };

  if (!budget) {
    return (
      <div className="flex justify-center p-12 text-neutral-400">
        <AlertCircle className="w-6 h-6 animate-pulse" />
      </div>
    );
  }

  const totalCost = budget.cost_breakdown.total_cost || 0;
  
  const chartData = [
    { name: "Accommodation", value: budget.cost_breakdown?.stay_cost || 0, color: COLORS.stay },
    { name: "Food & Dining", value: budget.cost_breakdown?.meals_cost || 0, color: COLORS.food },
    { name: "Transportation", value: budget.cost_breakdown?.transport_cost || 0, color: COLORS.transport },
    { name: "Activities", value: budget.cost_breakdown?.activities_cost || 0, color: COLORS.activities },
    { name: "Miscellaneous", value: budget.cost_breakdown?.misc_cost || 0, color: COLORS.misc }
  ].filter(item => item.value > 0);

  // EMPTY STATE
  if (totalCost === 0) {
    return (
      <div className="fade-in card" style={{ padding: 64, textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ position: "relative", width: 150, height: 150, marginBottom: 24 }}>
          {/* Ghosted Chart SVG Placeholder */}
          <svg viewBox="0 0 100 100" style={{ width: "100%", height: "100%" }}>
            <circle cx="50" cy="50" r="40" fill="none" stroke="var(--border)" strokeWidth="12" strokeDasharray="50 200" strokeLinecap="round" transform="rotate(-90 50 50)" />
            <circle cx="50" cy="50" r="40" fill="none" stroke="var(--border)" strokeWidth="12" strokeDasharray="80 200" strokeLinecap="round" transform="rotate(20 50 50)" opacity="0.6" />
            <circle cx="50" cy="50" r="40" fill="none" stroke="var(--border)" strokeWidth="12" strokeDasharray="60 200" strokeLinecap="round" transform="rotate(130 50 50)" opacity="0.3" />
          </svg>
          <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", color: "var(--ink-soft)" }}>
            <DollarSign size={32} opacity={0.5} />
          </div>
        </div>
        <p style={{ color: "var(--ink-soft)", fontSize: "1.125rem", maxWidth: 300 }}>
          Add stops and activities to see your budget breakdown.
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>
      
      {/* Page Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", paddingBottom: 16, borderBottom: "1px solid var(--border)" }}>
        <div>
          <h2 style={{ fontSize: "1.75rem", marginBottom: 8 }}>Budget & Forecast</h2>
          <p style={{ color: "var(--ink-soft)" }}>Group expense splits, limit tracking, and visualizations.</p>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 24, alignItems: "start" }}>
        
        {/* Left Column: Summary & Chart */}
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          {/* Top Metric */}
          <div className="card" style={{ padding: 24, textAlign: "center", background: budget.is_over_budget ? "var(--error-surface)" : "var(--primary-surface)" }}>
            <h3 style={{ color: "var(--ink-soft)", fontSize: "0.875rem", textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>
              Estimated Group Trip Cost
            </h3>
            <div style={{ fontSize: "2.5rem", fontWeight: "800", color: "var(--ink-dark)" }}>
              ₹{totalCost.toLocaleString('en-IN')}
            </div>

            {/* Per-Person Split Banner */}
            {budget.travelers && (
              <div style={{ marginTop: 12, padding: "10px 14px", background: "var(--surface-alt)", borderRadius: "var(--radius-input)", display: "flex", alignItems: "center", justifyContent: "space-around", fontSize: "0.8125rem" }}>
                <div>
                  <span style={{ color: "var(--ink-soft)", display: "block", fontSize: "0.75rem" }}>Per Person</span>
                  <span style={{ fontWeight: 700, color: "var(--accent)", fontSize: "1rem" }}>
                    ₹{(budget.cost_per_person || 0).toLocaleString('en-IN')}
                  </span>
                </div>
                <div style={{ borderLeft: "1px solid var(--border)", paddingLeft: 12 }}>
                  <span style={{ color: "var(--ink-soft)", display: "block", fontSize: "0.75rem" }}>Group Size</span>
                  <span style={{ fontWeight: 600 }}>{budget.travelers} Travelers</span>
                </div>
                <div style={{ borderLeft: "1px solid var(--border)", paddingLeft: 12 }}>
                  <span style={{ color: "var(--ink-soft)", display: "block", fontSize: "0.75rem" }}>Rooms</span>
                  <span style={{ fontWeight: 600 }}>{budget.rooms} Rooms</span>
                </div>
              </div>
            )}
            
            {budget.budget_target && (
              <div style={{ marginTop: 12, display: "flex", alignItems: "center", justifyContent: "center", gap: 6, fontWeight: "500", color: budget.is_over_budget ? "var(--error-main)" : "var(--primary-main)" }}>
                {budget.is_over_budget ? (
                  <><AlertCircle size={16} /> Over limit by ₹{overage.toLocaleString('en-IN')}</>
                ) : (
                  <><TrendingDown size={16} /> ₹{remaining.toLocaleString('en-IN')} under budget</>
                )}
              </div>
            )}
          </div>

          {/* Pie Chart */}
          <div className="card" style={{ padding: 24, flex: 1 }}>
            <h3 style={{ marginBottom: 16 }}>Cost Distribution</h3>
            {chartData.length > 0 ? (
              <div style={{ height: 250 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `₹${Number(value).toLocaleString('en-IN')}`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p style={{ textAlign: "center", color: "var(--ink-soft)", marginTop: 40 }}>No costs calculated yet.</p>
            )}

            <div style={{ display: "flex", flexWrap: "wrap", gap: 12, justifyContent: "center", marginTop: 16 }}>
              {chartData.map(item => (
                <div key={item.name} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.75rem", color: "var(--ink-medium)" }}>
                  <div style={{ width: 10, height: 10, borderRadius: "50%", background: item.color }} />
                  {item.name}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Breakdown & Controls */}
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          
          <div className="card" style={{ padding: 24 }}>
            <h3 style={{ marginBottom: 16 }}>Budget Target (₹ INR)</h3>
            <div style={{ display: "flex", gap: 8 }}>
              <div className="input-group" style={{ flex: 1, position: "relative" }}>
                <span style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "var(--ink-soft)", pointerEvents: "none", fontWeight: 700 }}>₹</span>
                <input 
                  type="number" 
                  className="input" 
                  style={{ paddingLeft: 36 }}
                  placeholder="Set max budget limit (e.g. 50000)" 
                  value={budgetLimit}
                  onChange={(e) => setBudgetLimit(e.target.value)}
                />
              </div>
              <button className="btn btn--primary" onClick={handleUpdateLimit}>Save</button>
            </div>
          </div>

          <div className="card" style={{ padding: 24, flex: 1 }}>
            <h3 style={{ marginBottom: 20 }}>Detailed Breakdown</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <BreakdownRow icon={ICONS.stay} label="Accommodation" amount={budget.breakdown?.stay} color={COLORS.stay} percent={percent(budget.breakdown?.stay)} />
              <BreakdownRow icon={ICONS.food} label="Food & Dining" amount={budget.breakdown?.food} color={COLORS.food} percent={percent(budget.breakdown?.food)} />
              <BreakdownRow icon={ICONS.transport} label="Transportation" amount={budget.breakdown?.transport} color={COLORS.transport} percent={percent(budget.breakdown?.transport)} />
              <BreakdownRow icon={ICONS.activities} label="Activities" amount={budget.breakdown?.activities} color={COLORS.activities} percent={percent(budget.breakdown?.activities)} />
              <BreakdownRow icon={ICONS.misc} label="Miscellaneous" amount={budget.breakdown?.other} color={COLORS.misc} percent={percent(budget.breakdown?.other)} />
            </div>
          </div>

        </div>
      </div>

      {/* Expenses Table */}
      <ExpenseList tripId={tripId} onExpenseAdded={onRefresh} />

    </div>
  );
}

function BreakdownRow({ icon: Icon, label, amount, color, percent }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div style={{ width: 40, height: 40, borderRadius: "var(--radius-input)", background: `${color}15`, color: color, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Icon size={18} />
        </div>
        <div>
          <div style={{ fontWeight: "600", color: "var(--ink)", fontSize: "0.9375rem" }}>{label}</div>
          <div style={{ fontSize: "0.8125rem", color: "var(--ink-soft)", fontWeight: "500" }}>{Math.round(percent || 0)}% of budget</div>
        </div>
      </div>
      <div style={{ fontWeight: "600", color: "var(--ink)" }}>₹{(amount || 0).toLocaleString('en-IN')}</div>
    </div>
  );
}
