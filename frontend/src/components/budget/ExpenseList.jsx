import { useState, useEffect } from "react";
import { tripService } from "../../services/tripService";
import { Plus, Trash2, FileText } from "lucide-react";

export default function ExpenseList({ tripId, onExpenseAdded }) {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ category: "misc", description: "", estimated_amount: 0 });

  useEffect(() => {
    loadExpenses();
  }, [tripId]);

  const loadExpenses = async () => {
    try {
      const res = await tripService.getExpenses(tripId);
      const data = res?.data || (Array.isArray(res) ? res : []);
      setExpenses(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setExpenses([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await tripService.addExpense(tripId, {
        ...form,
        estimated_amount: parseFloat(form.estimated_amount)
      });
      setShowAdd(false);
      setForm({ category: "misc", description: "", estimated_amount: 0 });
      loadExpenses();
      if (onExpenseAdded) onExpenseAdded();
    } catch (err) {
      console.error(err);
      alert("Failed to add expense");
    }
  };

  const handleDelete = async (id) => {
    try {
      await tripService.deleteExpense(id);
      loadExpenses();
      if (onExpenseAdded) onExpenseAdded(); // refresh budget
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="card" style={{ padding: 24, marginTop: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h3 style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <FileText size={20} className="text-primary" /> Logged Expenses
        </h3>
        <button className="btn btn--primary btn--sm" onClick={() => setShowAdd(!showAdd)}>
          <Plus size={16} /> Add Expense
        </button>
      </div>

      {showAdd && (
        <form onSubmit={handleAdd} style={{ display: "flex", gap: 12, marginBottom: 24, alignItems: "flex-end", flexWrap: "wrap", padding: 16, background: "var(--surface)", borderRadius: "var(--radius-md)" }}>
          <div style={{ flex: 1, minWidth: 150 }}>
            <label className="label">Category</label>
            <select className="input" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} required>
              <option value="transport">Transport</option>
              <option value="stay">Stay</option>
              <option value="food">Food</option>
              <option value="activity">Activity</option>
              <option value="misc">Misc</option>
            </select>
          </div>
          <div style={{ flex: 2, minWidth: 200 }}>
            <label className="label">Description</label>
            <input type="text" className="input" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required />
          </div>
          <div style={{ flex: 1, minWidth: 100 }}>
            <label className="label">Amount</label>
            <input type="number" step="0.01" className="input" value={form.estimated_amount} onChange={(e) => setForm({ ...form, estimated_amount: e.target.value })} required />
          </div>
          <button type="submit" className="btn btn--primary">Save</button>
        </form>
      )}

      {loading ? (
        <p style={{ color: "var(--ink-soft)" }}>Loading expenses...</p>
      ) : expenses.length === 0 ? (
        <p style={{ color: "var(--ink-soft)", fontStyle: "italic" }}>No custom expenses logged yet.</p>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", color: "var(--ink-soft)", fontSize: "0.875rem" }}>
                <th style={{ padding: "8px 0" }}>Date</th>
                <th style={{ padding: "8px 0" }}>Description</th>
                <th style={{ padding: "8px 0" }}>Category</th>
                <th style={{ padding: "8px 0", textAlign: "right" }}>Amount</th>
                <th style={{ padding: "8px 0", width: 40 }}></th>
              </tr>
            </thead>
            <tbody>
              {expenses.map((exp) => (
                <tr key={exp.id} style={{ borderBottom: "1px solid var(--border-light)" }}>
                  <td style={{ padding: "12px 0", fontSize: "0.875rem", color: "var(--ink-medium)" }}>
                    {new Date(exp.created_at).toLocaleDateString()}
                  </td>
                  <td style={{ padding: "12px 0", fontWeight: "500" }}>{exp.description}</td>
                  <td style={{ padding: "12px 0", textTransform: "capitalize", fontSize: "0.875rem" }}>{exp.category}</td>
                  <td style={{ padding: "12px 0", textAlign: "right", fontWeight: "600" }}>${exp.estimated_amount.toFixed(2)}</td>
                  <td style={{ padding: "12px 0", textAlign: "right" }}>
                    <button className="btn btn--icon btn--ghost btn--sm" onClick={() => handleDelete(exp.id)}>
                      <Trash2 size={16} color="var(--error-main)" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
