import { useState, useEffect, createContext, useContext } from "react";
import "./index.css";
import "./App.css";
import "./Sidebar.css";
import "./Auth.css";
import "./Accounts.css";

const API = "http://127.0.0.1:8000";

// ── Auth Context ───────────────────────────────────────────────────────────────
const AuthContext = createContext(null);
const useAuth = () => useContext(AuthContext);

function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token") || null);
  const [user, setUser] = useState(() => localStorage.getItem("username") || null);

  const login = (tk, username) => {
    localStorage.setItem("token", tk);
    localStorage.setItem("username", username);
    setToken(tk);
    setUser(username);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    setToken(null);
    setUser(null);
  };

  const authFetch = async (url, options = {}) => {
    const res = await fetch(`${API}${url}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...(options.headers || {}),
      },
    });
    if (res.status === 401) { logout(); return null; }
    return res;
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout, authFetch }}>
      {children}
    </AuthContext.Provider>
  );
}

// ── Helpers ────────────────────────────────────────────────────────────────────
const fmt = (n) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(n);

// ── Toast ──────────────────────────────────────────────────────────────────────
function Toast({ message, type, onClose }) {
  useEffect(() => {
    const t = setTimeout(onClose, 3500);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className={`toast ${type}`}>
      <span>{type === "success" ? "✓" : "✕"}</span>
      {message}
    </div>
  );
}

// ── Modal ──────────────────────────────────────────────────────────────────────
function Modal({ title, onClose, onSubmit, loading, submitLabel, children }) {
  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h3 className="modal-title">{title}</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        {children}
        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={onSubmit} disabled={loading}>
            {loading ? <span className="spinner" /> : submitLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Sidebar ────────────────────────────────────────────────────────────────────
function Sidebar({ page, setPage }) {
  const { user, logout } = useAuth();

  const navItems = [
    { id: "dashboard", icon: "🏠", label: "Dashboard" },
    { id: "accounts",  icon: "🏦", label: "Accounts"  },
    { id: "transactions", icon: "🔄", label: "Transactions" },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">💳 NovaPay</div>

      {navItems.map((n) => (
        <button
          key={n.id}
          className={`nav-item ${page === n.id ? "active" : ""}`}
          onClick={() => setPage(n.id)}
        >
          <span className="nav-icon">{n.icon}</span>
          <span>{n.label}</span>
        </button>
      ))}

      <div className="sidebar-user">
        <div className="username">👤 {user}</div>
        <div className="role">Account Holder</div>
        <button className="logout-btn" onClick={logout}>Sign Out</button>
      </div>
    </aside>
  );
}

// ── Auth Page ──────────────────────────────────────────────────────────────────
function AuthPage({ onToast }) {
  const { login } = useAuth();
  const [tab, setTab] = useState("login");
  const [form, setForm] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);

  const handle = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleLogin = async () => {
    setLoading(true);
    try {
      const body = new URLSearchParams({
        grant_type: "password",
        username: form.username,
        password: form.password,
      });
      const res = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");
      login(data.access_token, form.username);
      onToast("Welcome back! 👋", "success");
    } catch (e) {
      onToast(e.message, "error");
    }
    setLoading(false);
  };

  const handleRegister = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: form.username, password: form.password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Registration failed");
      onToast("Account created! Please login.", "success");
      setTab("login");
    } catch (e) {
      onToast(e.message, "error");
    }
    setLoading(false);
  };

  const onKey = (e) => {
    if (e.key === "Enter") tab === "login" ? handleLogin() : handleRegister();
  };

  return (
    <div className="auth-page">
      <div className="auth-bg" />
      <div className="auth-card">
        <div className="auth-logo">💳 NovaPay</div>
        <p className="auth-tagline">Your modern banking dashboard</p>

        <div className="auth-tabs">
          <button className={`auth-tab ${tab === "login" ? "active" : ""}`} onClick={() => setTab("login")}>Login</button>
          <button className={`auth-tab ${tab === "register" ? "active" : ""}`} onClick={() => setTab("register")}>Register</button>
        </div>

        <div className="form-group">
          <label className="form-label">Username</label>
          <input className="form-input" name="username" placeholder="Enter username" value={form.username} onChange={handle} onKeyDown={onKey} />
        </div>
        <div className="form-group">
          <label className="form-label">Password</label>
          <input className="form-input" name="password" type="password" placeholder="Enter password" value={form.password} onChange={handle} onKeyDown={onKey} />
        </div>

        <button className="btn btn-primary auth-submit" onClick={tab === "login" ? handleLogin : handleRegister} disabled={loading}>
          {loading ? <span className="spinner" /> : (tab === "login" ? "Login →" : "Create Account →")}
        </button>
      </div>
    </div>
  );
}

// ── Dashboard ──────────────────────────────────────────────────────────────────
function Dashboard({ accounts, transactions }) {
  const totalBalance = accounts.reduce((s, a) => s + a.balance, 0);
  const totalDeposits = transactions.filter((t) => t.amount > 0).reduce((s, t) => s + t.amount, 0);

  const stats = [
    { label: "Total Balance",   value: fmt(totalBalance),    icon: "💰", cls: "c4" },
    { label: "Total Accounts",  value: accounts.length,      icon: "🏦", cls: "c2" },
    { label: "Total Deposits",  value: fmt(totalDeposits),   icon: "📈", cls: "c3" },
    { label: "Transactions",    value: transactions.length,  icon: "🔄", cls: "c1" },
  ];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard 🏠</h1>
        <p className="page-subtitle">Overview of your banking activity</p>
      </div>

      <div className="card-grid">
        {stats.map((s) => (
          <div key={s.label} className={`stat-card ${s.cls}`}>
            <div className="stat-icon">{s.icon}</div>
            <div className="stat-label">{s.label}</div>
            <div className="stat-value">{s.value}</div>
          </div>
        ))}
      </div>

      <div className="card">
        <h3 style={{ marginBottom: 20 }}>Recent Transactions</h3>
        {transactions.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <p>No transactions yet</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Description</th><th>Account</th><th>Amount</th></tr>
              </thead>
              <tbody>
                {transactions.slice(0, 8).map((t) => (
                  <tr key={t.id}>
                    <td>{t.description}</td>
                    <td><span className="chip chip-blue">{t.account_id?.slice(0, 8)}...</span></td>
                    <td className={t.amount >= 0 ? "amount-positive" : "amount-negative"}>
                      {t.amount >= 0 ? "+" : ""}{fmt(t.amount)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Accounts Page ──────────────────────────────────────────────────────────────
function AccountsPage({ accounts, onRefresh, onToast }) {
  const { authFetch } = useAuth();
  const [showCreate, setShowCreate] = useState(false);
  const [showEdit, setShowEdit]     = useState(null);
  const [form, setForm]             = useState({ name: "", balance: "" });
  const [loading, setLoading]       = useState(false);

  const COLORS = ["#4d96ff", "#c77dff", "#6bcb77", "#ffd93d", "#ff6b6b"];

  const handleForm = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const createAccount = async () => {
    setLoading(true);
    try {
      const res = await authFetch("/accounts", {
        method: "POST",
        body: JSON.stringify({ name: form.name, balance: parseFloat(form.balance) }),
      });
      if (!res?.ok) throw new Error("Failed to create account");
      onToast("Account created! 🎉", "success");
      setShowCreate(false);
      setForm({ name: "", balance: "" });
      onRefresh();
    } catch (e) { onToast(e.message, "error"); }
    setLoading(false);
  };

  const updateAccount = async () => {
    setLoading(true);
    try {
      const res = await authFetch(`/accounts/${showEdit.id}`, {
        method: "PUT",
        body: JSON.stringify({ name: form.name, balance: parseFloat(form.balance) }),
      });
      if (!res?.ok) throw new Error("Failed to update account");
      onToast("Account updated! ✅", "success");
      setShowEdit(null);
      setForm({ name: "", balance: "" });
      onRefresh();
    } catch (e) { onToast(e.message, "error"); }
    setLoading(false);
  };

  const deleteAccount = async (id) => {
    if (!confirm("Delete this account?")) return;
    try {
      const res = await authFetch(`/accounts/${id}`, { method: "DELETE" });
      if (!res?.ok) throw new Error("Failed to delete");
      onToast("Account deleted", "success");
      onRefresh();
    } catch (e) { onToast(e.message, "error"); }
  };

  const openEdit = (acc) => {
    setForm({ name: acc.name, balance: acc.balance });
    setShowEdit(acc);
  };

  const formFields =  (
    <>
      <div className="form-group">
        <label className="form-label">Account Holder Name</label>
        <input 
          className="form-input" 
          name = "name"
          placeholder="Full name" 
          value={form.name} 
          onChange={handleForm} 
        />
      </div>
      <div className="form-group">
        <label className="form-label">Balance (₹)</label>
        <input 
        className="form-input" 
        type="number" 
        placeholder="0.00" 
        value={form.balance} 
        onChange= {handleForm} />
      </div>
    </>
  );

  return (
    <div>
      <div className="page-header-row">
        <div>
          <h1 className="page-title">Accounts 🏦</h1>
          <p className="page-subtitle">{accounts.length} account{accounts.length !== 1 ? "s" : ""} found</p>
        </div>
        <button className="btn btn-primary" onClick={() => { setForm({ name: "", balance: "" }); setShowCreate(true); }}>
          + New Account
        </button>
      </div>

      {accounts.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <div className="empty-icon">🏦</div>
            <p>No accounts yet. Create your first one!</p>
          </div>
        </div>
      ) : (
        <div className="card-grid">
          {accounts.map((acc, i) => (
            <div key={acc.id} className="account-card">
              <div className="account-card-header">
                <div>
                  <div className="account-name">{acc.name}</div>
                  <div className="account-number">#{acc.account_number || acc.id?.slice(0, 12)}</div>
                </div>
                <span className="account-badge">Active</span>
              </div>
              <div className="account-balance-label">Current Balance</div>
              <div className="account-balance" style={{ color: COLORS[i % COLORS.length] }}>
                {fmt(acc.balance)}
              </div>
              <div className="account-actions">
                <button className="btn btn-ghost btn-sm" onClick={() => openEdit(acc)}>✏️ Edit</button>
                <button className="btn btn-danger btn-sm" onClick={() => deleteAccount(acc.id)}>🗑 Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <Modal title="Create Account" onClose={() => setShowCreate(false)} onSubmit={createAccount} loading={loading} submitLabel="Create">
          <AccountForm />
        </Modal>
      )}

      {showEdit && (
        <Modal title="Edit Account" onClose={() => setShowEdit(null)} onSubmit={updateAccount} loading={loading} submitLabel="Save Changes">
          <AccountForm />
        </Modal>
      )}
    </div>
  );
}

// ── Transactions Page ──────────────────────────────────────────────────────────
function TransactionsPage({ accounts, transactions, onRefresh, onToast }) {
  const { authFetch } = useAuth();
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm]             = useState({ account_id: "", amount: "", description: "" });
  const [loading, setLoading]       = useState(false);
  const [filter, setFilter]         = useState("");

  const createTransaction = async () => {
    setLoading(true);
    try {
      const res = await authFetch("/transactions", {
        method: "POST",
        body: JSON.stringify({
          account_id: form.account_id,
          amount: parseFloat(form.amount),
          description: form.description,
        }),
      });
      if (!res?.ok) throw new Error("Failed to create transaction");
      onToast("Transaction recorded! ✅", "success");
      setShowCreate(false);
      setForm({ account_id: "", amount: "", description: "" });
      onRefresh();
    } catch (e) { onToast(e.message, "error"); }
    setLoading(false);
  };

  const deleteTransaction = async (id) => {
    if (!confirm("Delete this transaction?")) return;
    try {
      const res = await authFetch(`/transactions/${id}`, { method: "DELETE" });
      if (!res?.ok) throw new Error("Failed to delete");
      onToast("Transaction deleted", "success");
      onRefresh();
    } catch (e) { onToast(e.message, "error"); }
  };

  const getAccountName = (id) =>
    accounts.find((a) => a.id === id)?.name || id?.slice(0, 8) + "...";

  const filtered = filter
    ? transactions.filter((t) => t.account_id === filter)
    : transactions;

  return (
    <div>
      <div className="page-header-row">
        <div>
          <h1 className="page-title">Transactions 🔄</h1>
          <p className="page-subtitle">{filtered.length} transaction{filtered.length !== 1 ? "s" : ""}</p>
        </div>
        <button className="btn btn-primary" onClick={() => { setForm({ account_id: "", amount: "", description: "" }); setShowCreate(true); }}>
          + New Transaction
        </button>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <div className="filter-bar">
          <span className="filter-label">Filter by account:</span>
          <select className="form-input filter-select" value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="">All Accounts</option>
            {accounts.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name} — #{a.account_number || a.id?.slice(0, 8)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="card">
        {filtered.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <p>No transactions found</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Description</th><th>Account</th><th>Amount</th><th>Action</th></tr>
              </thead>
              <tbody>
                {filtered.map((t) => (
                  <tr key={t.id}>
                    <td>{t.description}</td>
                    <td><span className="chip chip-blue">{getAccountName(t.account_id)}</span></td>
                    <td className={t.amount >= 0 ? "amount-positive" : "amount-negative"}>
                      {t.amount >= 0 ? "+" : ""}{fmt(t.amount)}
                    </td>
                    <td>
                      <button className="btn btn-danger btn-sm" onClick={() => deleteTransaction(t.id)}>🗑</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showCreate && (
        <Modal title="New Transaction" onClose={() => setShowCreate(false)} onSubmit={createTransaction} loading={loading} submitLabel="Add Transaction">
          <div className="form-group">
            <label className="form-label">Account</label>
            <select className="form-input" value={form.account_id} onChange={(e) => setForm({ ...form, account_id: e.target.value })}>
              <option value="">Select account...</option>
              {accounts.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} — #{a.account_number || a.id?.slice(0, 8)}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Amount (₹) — negative for withdrawal</label>
            <input className="form-input" type="number" placeholder="e.g. 5000 or -2000" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
          </div>
          <div className="form-group">
            <label className="form-label">Description</label>
            <input className="form-input" placeholder="e.g. Salary, Rent, Transfer..." value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>
        </Modal>
      )}
    </div>
  );
}

// ── App Shell ──────────────────────────────────────────────────────────────────
function AppShell() {
  const { authFetch } = useAuth();
  const [page, setPage]             = useState("dashboard");
  const [accounts, setAccounts]     = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [toast, setToast]           = useState(null);

  const showToast = (message, type = "success") => setToast({ message, type });

  const loadData = async () => {
    const [accRes, txRes] = await Promise.all([
      authFetch("/accounts"),
      authFetch("/transactions"),
    ]);
    if (accRes?.ok) setAccounts(await accRes.json());
    if (txRes?.ok)  setTransactions(await txRes.json());
  };

  useEffect(() => { loadData(); }, []);

  return (
    <div className="app-layout">
      <Sidebar page={page} setPage={setPage} />

      <main className="main-content">
        {page === "dashboard" && (
          <Dashboard accounts={accounts} transactions={transactions} />
        )}
        {page === "accounts" && (
          <AccountsPage accounts={accounts} onRefresh={loadData} onToast={showToast} />
        )}
        {page === "transactions" && (
          <TransactionsPage accounts={accounts} transactions={transactions} onRefresh={loadData} onToast={showToast} />
        )}
      </main>

      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
    </div>
  );
}

// ── Root ───────────────────────────────────────────────────────────────────────
function AppRouter() {
  const { token } = useAuth();
  const [toast, setToast] = useState(null);

  return (
    <>
      {token
        ? <AppShell />
        : <AuthPage onToast={(msg, type) => setToast({ message: msg, type })} />
      }
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
    </>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
}