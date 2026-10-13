import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import db

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wanderlust DBMS",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

db.init_db()

# ─── Design System ───────────────────────────────────────────────────────────
ROLE_CONFIG = {
    "Administrator (Travel Agent)": {
        "color": "#6366f1",
        "bg":    "#eef2ff",
        "icon":  "⚙️",
        "label": "Administrator",
    },
    "Customer (Lead Traveller)": {
        "color": "#0ea5e9",
        "bg":    "#e0f2fe",
        "icon":  "🧳",
        "label": "Customer",
    },
    "Tour Guide": {
        "color": "#10b981",
        "bg":    "#d1fae5",
        "icon":  "🧭",
        "label": "Tour Guide",
    },
}

STATUS_BADGE = {
    "Confirmed":      ("✅", "#dcfce7", "#166534"),
    "Pending Payment":("⏳", "#fef9c3", "#854d0e"),
    "Completed":      ("🏁", "#ede9fe", "#5b21b6"),
    "Cancelled":      ("❌", "#fee2e2", "#991b1b"),
    "Scheduled":      ("🗓️", "#dbeafe", "#1e40af"),
    "In Progress":    ("🚌", "#fef3c7", "#92400e"),
    "Processed":      ("✔️", "#d1fae5", "#065f46"),
    "Approved":       ("👍", "#d1fae5", "#065f46"),
    "Requested":      ("📨", "#ffedd5", "#9a3412"),
    "Rejected":       ("🚫", "#fee2e2", "#991b1b"),
}

def badge_html(status: str) -> str:
    icon, bg, fg = STATUS_BADGE.get(status, ("•", "#f1f5f9", "#334155"))
    return (
        f'<span style="background:{bg};color:{fg};padding:3px 10px;border-radius:9999px;'
        f'font-size:12px;font-weight:600;white-space:nowrap;">{icon} {status}</span>'
    )

# ─── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Emoji rendering: always use system emoji font for emoji characters */
@font-face {
    font-family: 'EmojiFont';
    src: local('Apple Color Emoji'), local('Segoe UI Emoji'), local('Noto Color Emoji');
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Sidebar: target only text nodes, not SVG/icon elements ── */
section[data-testid="stSidebar"] {
    background: #0f172a !important;
}
/* Only target paragraph/span text, not icons */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stCaption p {
    color: #94a3b8 !important;
}
/* Radio button labels */
section[data-testid="stSidebar"] .stRadio label p,
section[data-testid="stSidebar"] .stRadio span {
    color: #e2e8f0 !important;
    font-size: 14px !important;
}
/* Sidebar button text */
section[data-testid="stSidebar"] .stButton button {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border: 1px solid #334155 !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #334155 !important;
    border-color: #475569 !important;
}
section[data-testid="stSidebar"] hr { border-color: #1e293b !important; }
/* Sidebar selectbox label */
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] label {
    color: #94a3b8 !important;
    font-size: 12px !important;
}
/* Keep radio circle indicators visible */
section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    color: #e2e8f0 !important;
    font-size: 14px !important;
}

/* ── Top-bar ── */
.topbar {
    background: linear-gradient(100deg,#0f172a 0%,#1e3a5f 60%,#1e40af 100%);
    border-radius: 14px;
    padding: 20px 28px;
    color: #fff;
    margin-bottom: 22px;
    border: 1px solid rgba(255,255,255,0.08);
    display: flex;
    align-items: center;
    gap: 18px;
}
.topbar-icon { font-size: 36px; }
.topbar-title { font-size: 22px; font-weight: 700; letter-spacing:-0.4px; }
.topbar-sub   { font-size: 13px; color: #94a3b8; margin-top: 2px; }

/* ── Role pill ── */
.role-pill {
    display:inline-flex; align-items:center; gap:6px;
    padding:6px 14px; border-radius:9999px;
    font-size:13px; font-weight:600;
    margin-bottom:10px;
}

/* ── Stat card ── */
.stat-card {
    background:#fff;
    border:1px solid #e2e8f0;
    border-radius:12px;
    padding:18px 20px;
    height:100%;
    transition: box-shadow .2s;
}
.stat-card:hover { box-shadow: 0 4px 14px rgba(0,0,0,.08); }
.stat-icon  { font-size:28px; margin-bottom:8px; }
.stat-label { font-size:11px; font-weight:600; text-transform:uppercase;
               letter-spacing:.6px; color:#64748b; margin-bottom:4px; }
.stat-value { font-size:26px; font-weight:700; color:#0f172a; }
.stat-sub   { font-size:12px; color:#22c55e; font-weight:500; margin-top:3px; }

/* ── Package card ── */
.pkg-card {
    background:#fff;
    border:1px solid #e2e8f0;
    border-radius:14px;
    padding:20px;
    margin-bottom:14px;
    transition: box-shadow .2s, transform .15s;
}
.pkg-card:hover { box-shadow:0 6px 20px rgba(0,0,0,.09); transform:translateY(-2px); }
.pkg-name { font-size:16px; font-weight:700; color:#0f172a; }
.pkg-dest { font-size:13px; color:#64748b; margin-top:2px; }
.pkg-price { font-size:20px; font-weight:700; color:#0ea5e9; }
.pkg-price small { font-size:12px; font-weight:400; color:#94a3b8; }

/* ── Departure card ── */
.dep-card {
    background:#fff;
    border:1px solid #e2e8f0;
    border-radius:14px;
    padding:18px 20px;
    margin-bottom:12px;
    border-left: 4px solid #6366f1;
}

/* ── Info row ── */
.info-row {
    display:flex; gap:24px; flex-wrap:wrap;
    margin: 8px 0;
    font-size:13px; color:#475569;
}
.info-row span { display:flex; align-items:center; gap:4px; }

/* ── Section header ── */
.section-header {
    font-size:15px; font-weight:700; color:#0f172a;
    margin:18px 0 10px; border-bottom:2px solid #f1f5f9; padding-bottom:6px;
}

/* ── Itinerary step ── */
.itin-step {
    display:flex; gap:12px; align-items:flex-start;
    padding: 10px 14px; background:#f8fafc;
    border-radius:10px; margin-bottom:6px;
}
.itin-day {
    min-width:42px; height:42px; border-radius:10px;
    background:#6366f1; color:#fff; display:flex;
    align-items:center; justify-content:center;
    font-size:12px; font-weight:700; flex-shrink:0;
}
.itin-text { font-size:13px; color:#334155; padding-top:2px; line-height:1.5; }

/* ── Capacity bar ── */
.cap-bar-wrap { background:#f1f5f9; border-radius:9999px; height:8px;
                overflow:hidden; margin-top:4px; }
.cap-bar-fill { height:8px; border-radius:9999px;
                background:linear-gradient(90deg,#6366f1,#0ea5e9); }

/* ── Booking card ── */
.booking-card {
    background:#fff; border:1px solid #e2e8f0; border-radius:14px;
    padding:20px; margin-bottom:14px;
}

/* ── Manifest row ── */
.manifest-row {
    display:flex; align-items:center; gap:12px;
    padding:10px 14px; border-radius:10px; background:#f8fafc;
    margin-bottom:6px; font-size:13px;
}
.manifest-avatar {
    width:34px; height:34px; border-radius:9999px;
    background:linear-gradient(135deg,#6366f1,#0ea5e9);
    color:#fff; display:flex; align-items:center; justify-content:center;
    font-weight:700; font-size:13px; flex-shrink:0;
}

/* ── Integrity box ── */
.integrity-panel {
    background:#fef9c3;
    border:1px solid #fde68a;
    border-radius:10px;
    padding:12px 16px;
    font-size:13px; color:#78350f;
    margin-top:6px;
}

/* ── Empty state ── */
.empty-state {
    text-align:center; padding:48px 24px; color:#94a3b8;
}
.empty-state-icon { font-size:42px; margin-bottom:12px; }
.empty-state-text { font-size:15px; font-weight:500; }
.empty-state-sub  { font-size:13px; margin-top:4px; }

/* ── Tab clean-up ── */
button[data-baseweb="tab"] { font-size:13px !important; font-weight:500 !important; }

/* ── Form inputs ── */
.stTextInput input, .stSelectbox select, .stNumberInput input, .stTextArea textarea {
    border-radius: 8px !important;
}
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stFormSubmitButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:12px 0 8px;">
        <div style="font-size:22px;font-weight:700;color:#fff;letter-spacing:-0.5px;">✈️ Wanderlust</div>
        <div style="font-size:11px;color:#64748b;margin-top:2px;">Tourism Booking DBMS v1.0</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<hr style="margin:8px 0 16px;">', unsafe_allow_html=True)

    st.markdown('<div style="font-size:11px;font-weight:600;color:#64748b;letter-spacing:.6px;text-transform:uppercase;margin-bottom:8px;">Switch Role</div>', unsafe_allow_html=True)
    role = st.radio(
        "role",
        list(ROLE_CONFIG.keys()),
        label_visibility="collapsed",
        format_func=lambda r: f"{ROLE_CONFIG[r]['icon']}  {ROLE_CONFIG[r]['label']}"
    )
    rc = ROLE_CONFIG[role]
    st.markdown(f"""
    <div class="role-pill" style="background:{rc['bg']};color:{rc['color']};margin-top:4px;">
        {rc['icon']} Active: {rc['label']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr style="margin:16px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:11px;font-weight:600;color:#64748b;letter-spacing:.6px;text-transform:uppercase;margin-bottom:10px;">🛡️ Integrity Tests</div>', unsafe_allow_html=True)

    if st.button("🚫 Trigger Overbooking", use_container_width=True):
        can, bk, mc, av, msg = db.check_capacity_available(6, 5)
        if not can:
            st.error(f"**Blocked:** {msg}")
        else:
            st.success("Seats available.")

    if st.button("👤 Guide Conflict Test", use_container_width=True):
        has_c, cfls = db.check_guide_conflict(1, "2026-11-02", "2026-11-06")
        if has_c:
            c = cfls[0]
            st.error(f"**Blocked:** Jean-Luc already on Departure #{c['Depart_ID']} — {c['Start_Date']} → {c['End_Date']}")

    if st.button("🚌 Transport Conflict Test", use_container_width=True):
        has_c, cfls = db.check_transport_conflict(3, "2026-11-04", "2026-11-08")
        if has_c:
            c = cfls[0]
            st.error(f"**Blocked:** {c['Transport_Type']} in use on Departure #{c['Depart_ID']} — {c['Start_Date']} → {c['End_Date']}")

    if st.button("💸 Financial Integrity Test", use_container_width=True):
        valid, paid, ref, mx, err = db.check_refund_integrity(1, 4000.0)
        if not valid:
            st.error(f"**Blocked:** {err}")

    st.markdown('<hr style="margin:16px 0;">', unsafe_allow_html=True)
    if st.button("🔄 Reset Database", use_container_width=True, help="Wipe & reseed all 13 tables"):
        db.init_db(force_reset=True)
        st.success("✅ Database reset to seed state!")
        st.rerun()

    st.markdown("""
    <div style="font-size:11px;color:#475569;margin-top:16px;line-height:1.6;">
        <b style="color:#94a3b8;">13 Core Entities</b> in 3NF<br>
        ACID transactions • FK constraints<br>
        Capacity, conflict & financial guards
    </div>
    """, unsafe_allow_html=True)


# ─── Top Bar ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
    <div class="topbar-icon">✈️</div>
    <div>
        <div class="topbar-title">Wanderlust Tourism & Travel Booking DBMS</div>
        <div class="topbar-sub">3NF Relational Simulator &nbsp;|&nbsp; SQLite 3 Backend &nbsp;|&nbsp;
            Active Role: <b style="color:#fff;">{rc['icon']} {rc['label']}</b>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# ROLE 1: ADMINISTRATOR
# ════════════════════════════════════════════════════════════════════════════
if role == "Administrator (Travel Agent)":

    tabs = st.tabs(["📊 Dashboard", "🗓️ Departures", "📦 Packages", "🏛️ Assets", "💼 Bookings & Refunds", "🗄️ SQL Console"])
    adm1, adm2, adm3, adm4, adm5, adm6 = tabs

    # ── Dashboard ───────────────────────────────────────────────────────────
    with adm1:
        kpis = db.get_kpi_summary()

        # KPI row
        kpi_data = [
            ("📋", "Total Bookings", kpis["total_bookings"], f"{kpis['active_bookings']} confirmed"),
            ("💰", "Gross Revenue",  f"${kpis['gross_revenue']:,.0f}", f"Net ${kpis['net_revenue']:,.0f}"),
            ("👥", "Travellers",     kpis["total_travellers"],          "across all tours"),
            ("🚌", "Active Tours",   kpis["active_departures"],          f"{kpis['utilization_pct']}% seat fill"),
        ]
        cols = st.columns(4)
        for col, (icon, label, val, sub) in zip(cols, kpi_data):
            with col:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">{icon}</div>
                    <div class="stat-label">{label}</div>
                    <div class="stat-value">{val}</div>
                    <div class="stat-sub">{sub}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("")

        # Charts
        ch1, ch2 = st.columns(2)
        with ch1:
            conn = db.get_connection()
            rev_df = pd.read_sql_query("""
                SELECT p.Name as Package_Name,
                       COALESCE(SUM(pm.Amount),0) as Revenue
                FROM Package p
                LEFT JOIN Departure d ON p.Package_ID=d.Package_ID
                LEFT JOIN Booking b ON d.Depart_ID=b.Depart_ID AND b.Status!='Cancelled'
                LEFT JOIN Payment pm ON b.Booking_ID=pm.Booking_ID
                GROUP BY p.Package_ID ORDER BY Revenue DESC
            """, conn)
            conn.close()
            fig = px.bar(rev_df, x="Revenue", y="Package_Name", orientation="h",
                         color="Revenue", color_continuous_scale="Blues",
                         title="💰 Revenue by Package",
                         labels={"Revenue":"Collected ($)","Package_Name":""})
            fig.update_layout(showlegend=False, margin=dict(l=0,r=0,t=40,b=0),
                               height=260, paper_bgcolor="#fff", plot_bgcolor="#fff",
                               font_family="Inter", title_font_size=14)
            fig.update_traces(text=rev_df["Revenue"].apply(lambda x: f"${x:,.0f}"),
                               textposition="inside")
            st.plotly_chart(fig, width="stretch")

        with ch2:
            deps = db.get_all_departures()
            if deps:
                dep_df = pd.DataFrame(deps)
                fig2 = px.bar(dep_df, x="Depart_ID",
                               y=["Booked_Seats","Available_Seats"],
                               title="🚌 Departure Seat Allocation",
                               barmode="stack",
                               color_discrete_map={"Booked_Seats":"#6366f1","Available_Seats":"#e2e8f0"},
                               labels={"value":"Seats","Depart_ID":"Departure #","variable":"Type"})
                fig2.update_layout(margin=dict(l=0,r=0,t=40,b=0), height=260,
                                    paper_bgcolor="#fff", plot_bgcolor="#fff",
                                    font_family="Inter", title_font_size=14)
                st.plotly_chart(fig2, width="stretch")

        # Departure table
        st.markdown('<div class="section-header">📋 Active Departures Overview</div>', unsafe_allow_html=True)
        if deps:
            for d in deps:
                pct = int(d["Booked_Seats"] / max(d["Max_Capacity"],1) * 100)
                fill_color = "#22c55e" if pct < 70 else ("#f59e0b" if pct < 95 else "#ef4444")
                st.markdown(f"""
                <div class="dep-card" style="border-left-color:{fill_color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                        <div>
                            <span style="font-weight:700;font-size:14px;color:#0f172a;">#{d['Depart_ID']} &nbsp;{d['Package_Name']}</span>
                            <span style="margin-left:10px;">{badge_html(d['Status'])}</span>
                        </div>
                        <div style="font-size:13px;color:#64748b;">📍 {d['Dest_Name']}, {d['Country']}</div>
                    </div>
                    <div class="info-row" style="margin-top:8px;">
                        <span>📅 {d['Start_Date']} → {d['End_Date']}</span>
                        <span>🧭 {d['Guide_Name']}</span>
                        <span>🚌 {d['Transport_Type']}</span>
                        <span>💺 {d['Booked_Seats']}/{d['Max_Capacity']} seats ({pct}% full)</span>
                    </div>
                    <div class="cap-bar-wrap" style="margin-top:8px;">
                        <div class="cap-bar-fill" style="width:{pct}%;background:{'linear-gradient(90deg,#22c55e,#16a34a)' if pct<70 else ('linear-gradient(90deg,#f59e0b,#d97706)' if pct<95 else 'linear-gradient(90deg,#ef4444,#dc2626)')}"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Departures ──────────────────────────────────────────────────────────
    with adm2:
        st.markdown('<div class="section-header">🗓️ Schedule New Departure</div>', unsafe_allow_html=True)

        packages   = db.get_all_packages()
        guides     = db.get_all_guides()
        transports = db.get_all_transports()

        with st.form("schedule_form", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                pkg_map = {f"{p['Package_ID']} · {p['Name']}  ({p['Duration_Days']}d, ${p['Base_Price']:,.0f}/pp)": p for p in packages}
                sel_pkg = st.selectbox("📦 Package", list(pkg_map.keys()))
                chosen_pkg = pkg_map[sel_pkg]
                start_d = st.date_input("📅 Start Date", min_value=date.today(), value=date.today()+timedelta(days=14))
                calc_end = start_d + timedelta(days=chosen_pkg["Duration_Days"])
                st.info(f"📅 Auto End Date: **{calc_end}**  ({chosen_pkg['Duration_Days']} days)")

            with c2:
                guide_map = {f"🧭 {g['Guide_ID']} · {g['Name']}  ({g['Language']})": g["Guide_ID"] for g in guides}
                sel_guide = st.selectbox("Tour Guide", list(guide_map.keys()))
                sel_guide_id = guide_map[sel_guide]

                trans_map = {f"🚌 {t['Transport_ID']} · {t['Type']}  (max {t['Capacity']} seats)": t for t in transports}
                sel_trans_str = st.selectbox("Transport", list(trans_map.keys()))
                sel_trans = trans_map[sel_trans_str]

                max_cap = st.number_input("Max Passengers", min_value=1,
                                           max_value=sel_trans["Capacity"],
                                           value=min(12, sel_trans["Capacity"]),
                                           help=f"Vehicle max capacity: {sel_trans['Capacity']}")

            submitted = st.form_submit_button("🚀 Validate & Schedule Departure", use_container_width=True)

        if submitted:
            ok, msg = db.schedule_departure(
                chosen_pkg["Package_ID"], sel_guide_id, sel_trans["Transport_ID"],
                start_d.strftime("%Y-%m-%d"), calc_end.strftime("%Y-%m-%d"), max_cap
            )
            if ok:
                st.success(f"✅ {msg}")
                st.rerun()
            else:
                st.error(f"❌ {msg}")

        st.markdown('<div class="section-header">🔄 Update Departure Status</div>', unsafe_allow_html=True)
        all_deps = db.get_all_departures()
        if all_deps:
            dep_labels = {f"#{d['Depart_ID']} · {d['Package_Name']}  ({d['Start_Date']})  [{d['Status']}]": d["Depart_ID"] for d in all_deps}
            uc1, uc2, uc3 = st.columns([3, 2, 1.2])
            with uc1:
                sel_dep_label = st.selectbox("Select Departure", list(dep_labels.keys()), label_visibility="collapsed")
            with uc2:
                new_status = st.selectbox("New Status", ["Scheduled","In Progress","Completed","Cancelled"], label_visibility="collapsed")
            with uc3:
                if st.button("Update", use_container_width=True):
                    ok, msg = db.update_departure_status(dep_labels[sel_dep_label], new_status)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # ── Packages ─────────────────────────────────────────────────────────────
    with adm3:
        st.markdown('<div class="section-header">📦 Tour Packages Catalog</div>', unsafe_allow_html=True)
        packages = db.get_all_packages()
        if packages:
            pkg_cols = st.columns(2)
            for idx, pkg in enumerate(packages):
                with pkg_cols[idx % 2]:
                    dep_count = len(db.get_all_departures(filter_package_id=pkg["Package_ID"]))
                    st.markdown(f"""
                    <div class="pkg-card">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                            <div>
                                <div class="pkg-name">{pkg['Name']}</div>
                                <div class="pkg-dest">📍 {pkg['Dest_Name']}, {pkg['Country']} &nbsp;·&nbsp; ⏱️ {pkg['Duration_Days']} days &nbsp;·&nbsp; 🗓️ {dep_count} departure(s)</div>
                            </div>
                            <div>
                                <div class="pkg-price">${pkg['Base_Price']:,.0f}<small>/person</small></div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">➕ Add New Package</div>', unsafe_allow_html=True)
        dests = db.get_all_destinations()
        dest_map = {f"{d['Name']}, {d['Country']}": d["Dest_ID"] for d in dests}

        with st.form("add_pkg_form"):
            fc1, fc2 = st.columns(2)
            with fc1:
                sel_dest  = st.selectbox("Destination", list(dest_map.keys()))
                pkg_name  = st.text_input("Package Name", placeholder="e.g. Kyoto Cultural Deep Dive")
            with fc2:
                pkg_days  = st.number_input("Duration (days)", min_value=1, max_value=30, value=5)
                pkg_price = st.number_input("Base Price per Person (USD)", min_value=100.0, value=1200.0, step=50.0)
            if st.form_submit_button("Create Package", use_container_width=True):
                if pkg_name.strip():
                    ok, msg = db.add_package(dest_map[sel_dest], pkg_name, pkg_days, pkg_price)
                    st.success(msg) if ok else st.error(msg)
                    if ok: st.rerun()
                else:
                    st.warning("Please enter a package name.")

        # Itinerary adder
        with st.expander("📅 Add Itinerary Day to a Package"):
            pkg_map_itin = {f"{p['Package_ID']} · {p['Name']}": p["Package_ID"] for p in db.get_all_packages()}
            with st.form("itin_form"):
                ic1, ic2 = st.columns([2, 1])
                with ic1:
                    sel_itin_pkg = st.selectbox("Package", list(pkg_map_itin.keys()))
                with ic2:
                    day_num = st.number_input("Day Number", min_value=1, value=1)
                activity = st.text_area("Activity Description", placeholder="Describe the day's activities in detail…")
                if st.form_submit_button("Add Day", use_container_width=True):
                    if activity.strip():
                        ok, msg = db.add_itinerary_day(pkg_map_itin[sel_itin_pkg], day_num, activity)
                        st.success(msg) if ok else st.error(msg)
                    else:
                        st.warning("Activity description cannot be empty.")

    # ── Assets ────────────────────────────────────────────────────────────────
    with adm4:
        asset_tab1, asset_tab2, asset_tab3, asset_tab4 = st.tabs(["🌍 Destinations", "🏨 Hotels", "🚌 Transport", "🧭 Guides"])

        with asset_tab1:
            dests = db.get_all_destinations()
            d_cols = st.columns(2)
            for i, d in enumerate(dests):
                with d_cols[i % 2]:
                    st.markdown(f"""
                    <div class="pkg-card" style="padding:14px 18px;">
                        <div style="font-weight:700;color:#0f172a;">{d['Name']}</div>
                        <div style="font-size:12px;color:#64748b;margin-top:2px;">🌍 {d['Country']}</div>
                        <div style="font-size:12px;color:#475569;margin-top:6px;line-height:1.5;">{d['Description'][:120]}…</div>
                    </div>
                    """, unsafe_allow_html=True)

            with st.expander("➕ Add Destination"):
                with st.form("add_dest"):
                    nd1, nd2 = st.columns(2)
                    with nd1: dest_name = st.text_input("City / Region")
                    with nd2: dest_country = st.text_input("Country")
                    dest_desc = st.text_area("Description")
                    if st.form_submit_button("Save Destination", use_container_width=True):
                        if dest_name and dest_country and dest_desc:
                            ok, msg = db.add_destination(dest_name, dest_country, dest_desc)
                            st.success(msg) if ok else st.error(msg)
                            if ok: st.rerun()

        with asset_tab2:
            hotels = db.get_all_hotels()
            hotel_df = pd.DataFrame(hotels)[["Hotel_ID","Name","Dest_Name","Star_Rating"]]
            hotel_df["Star_Rating"] = hotel_df["Star_Rating"].apply(lambda r: "★"*r)
            st.dataframe(hotel_df, width="stretch", hide_index=True,
                          column_config={"Hotel_ID":"ID","Star_Rating":"Stars","Dest_Name":"Destination"})

            with st.expander("➕ Add Hotel"):
                dests = db.get_all_destinations()
                dest_map = {f"{d['Name']}, {d['Country']}": d["Dest_ID"] for d in dests}
                with st.form("add_hotel"):
                    hc1, hc2, hc3 = st.columns([2,2,1])
                    with hc1: hotel_dest = st.selectbox("Destination", list(dest_map.keys()))
                    with hc2: hotel_name = st.text_input("Hotel Name")
                    with hc3: hotel_stars = st.select_slider("Stars", options=[1,2,3,4,5], value=4)
                    if st.form_submit_button("Add Hotel", use_container_width=True):
                        if hotel_name:
                            ok, msg = db.add_hotel(dest_map[hotel_dest], hotel_name, hotel_stars)
                            st.success(msg) if ok else st.error(msg)
                            if ok: st.rerun()

        with asset_tab3:
            trans = db.get_all_transports()
            st.dataframe(pd.DataFrame(trans), width="stretch", hide_index=True,
                          column_config={"Transport_ID":"ID","Type":"Vehicle Model","Capacity":"Max Seats"})

            with st.expander("➕ Register Transport Vehicle"):
                with st.form("add_trans"):
                    tc1, tc2 = st.columns(2)
                    with tc1: t_type = st.text_input("Vehicle Model / Description", placeholder="e.g. Volvo 9700 Luxury Coach")
                    with tc2: t_cap  = st.number_input("Passenger Capacity", min_value=1, max_value=100, value=20)
                    if st.form_submit_button("Register Vehicle", use_container_width=True):
                        if t_type:
                            ok, msg = db.add_transport(t_type, t_cap)
                            st.success(msg) if ok else st.error(msg)
                            if ok: st.rerun()

        with asset_tab4:
            guides = db.get_all_guides()
            st.dataframe(pd.DataFrame(guides), width="stretch", hide_index=True,
                          column_config={"Guide_ID":"ID","Name":"Guide Name","Contact":"Phone","Language":"Languages Spoken"})

            with st.expander("➕ Onboard New Guide"):
                with st.form("add_guide"):
                    gc1, gc2, gc3 = st.columns(3)
                    with gc1: g_name    = st.text_input("Full Name")
                    with gc2: g_contact = st.text_input("Phone Number")
                    with gc3: g_lang    = st.text_input("Languages", placeholder="English, French…")
                    if st.form_submit_button("Onboard Guide", use_container_width=True):
                        if g_name and g_contact and g_lang:
                            ok, msg = db.add_guide(g_name, g_contact, g_lang)
                            st.success(msg) if ok else st.error(msg)
                            if ok: st.rerun()

    # ── Bookings & Refunds ────────────────────────────────────────────────────
    with adm5:
        b_tab1, b_tab2 = st.tabs(["📋 All Bookings", "💸 Refund Queue"])

        with b_tab1:
            all_b = db.get_all_bookings_admin()
            if all_b:
                df = pd.DataFrame(all_b)
                display = df[["Booking_ID","Customer_Name","Package_Name","Start_Date","End_Date",
                               "Traveller_Count","Total_Amount","Paid_Amount","Booking_Status"]]
                display.columns = ["ID","Customer","Package","Start","End","Travellers","Total ($)","Paid ($)","Status"]
                display["Total ($)"] = display["Total ($)"].apply(lambda x: f"${x:,.2f}")
                display["Paid ($)"]  = display["Paid ($)"].apply(lambda x: f"${x:,.2f}")
                st.dataframe(display, width="stretch", hide_index=True)
            else:
                st.markdown('<div class="empty-state"><div class="empty-state-icon">📋</div><div class="empty-state-text">No bookings yet</div></div>', unsafe_allow_html=True)

        with b_tab2:
            st.info("**Rule:** Total approved refunds cannot exceed total payments collected for a booking.")
            refunds = db.get_all_refunds_admin()
            if refunds:
                for r in refunds:
                    pct = round(r["Refund_Amount"] / max(r["Paid_Amount"], 0.01) * 100)
                    st.markdown(f"""
                    <div class="booking-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                            <div>
                                <span style="font-weight:700;">Refund #{r['Refund_ID']}</span>
                                &nbsp;{badge_html(r['Refund_Status'])}&nbsp;
                                <span style="font-size:13px;color:#64748b;">Booking #{r['Booking_ID']} · {r['Customer_Name']}</span>
                            </div>
                            <div style="font-size:18px;font-weight:700;color:#6366f1;">${r['Refund_Amount']:,.2f}</div>
                        </div>
                        <div class="info-row" style="margin-top:8px;">
                            <span>📦 {r['Package_Name']}</span>
                            <span>💳 Paid: ${r['Paid_Amount']:,.2f}</span>
                            <span>📅 Cancelled: {r['Cancel_Date']}</span>
                            <span>💬 {r['Cancel_Reason'][:60]}{'…' if len(r['Cancel_Reason'])>60 else ''}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('<div class="section-header">⚖️ Adjudicate Refund</div>', unsafe_allow_html=True)
                rc1, rc2, rc3 = st.columns([3,2,1.2])
                with rc1:
                    ref_opts = {f"Refund #{r['Refund_ID']} — {r['Customer_Name']} ${r['Refund_Amount']:,.2f} [{r['Refund_Status']}]": r["Refund_ID"] for r in refunds}
                    sel_ref = st.selectbox("Select Refund", list(ref_opts.keys()), label_visibility="collapsed")
                with rc2:
                    ref_decision = st.selectbox("Decision", ["Approved","Processed","Rejected"], label_visibility="collapsed")
                with rc3:
                    if st.button("Apply", use_container_width=True):
                        ok, msg = db.update_refund_status(ref_opts[sel_ref], ref_decision)
                        if ok: st.success(msg); st.rerun()
                        else: st.error(msg)
            else:
                st.markdown('<div class="empty-state"><div class="empty-state-icon">💸</div><div class="empty-state-text">No refund requests</div><div class="empty-state-sub">Refunds appear when customers cancel bookings</div></div>', unsafe_allow_html=True)

    # ── SQL Console ───────────────────────────────────────────────────────────
    with adm6:
        sc1, sc2 = st.columns([1, 2])

        with sc1:
            st.markdown('<div class="section-header">🗄️ 3NF Schema Browser</div>', unsafe_allow_html=True)
            schema = db.get_schema_tables_info()
            sel_table = st.selectbox("Inspect Table:", list(schema.keys()))
            t_info = schema[sel_table]
            st.caption(f"{t_info['row_count']} rows")

            cols_df = pd.DataFrame(t_info["columns"])[["name","type","notnull","pk"]]
            cols_df.columns = ["Column","Type","NOT NULL","PK"]
            cols_df["PK"] = cols_df["PK"].apply(lambda x: "🔑" if x else "")
            cols_df["NOT NULL"] = cols_df["NOT NULL"].apply(lambda x: "✓" if x else "")
            st.dataframe(cols_df, width="stretch", hide_index=True)

            if t_info["foreign_keys"]:
                st.caption("Foreign Keys:")
                fk_df = pd.DataFrame(t_info["foreign_keys"])[["from","table","to"]]
                fk_df.columns = ["Column","→ Table","→ Column"]
                st.dataframe(fk_df, width="stretch", hide_index=True)

        with sc2:
            st.markdown('<div class="section-header">⚡ SQL Query Executor</div>', unsafe_allow_html=True)
            presets = {
                "Browse selected table":     f"SELECT * FROM {sel_table} LIMIT 25;",
                "Departure capacity audit":  """SELECT d.Depart_ID, p.Name, d.Start_Date,
       d.Max_Capacity,
       COUNT(t.Traveller_ID) as Booked,
       d.Max_Capacity - COUNT(t.Traveller_ID) as Available
FROM Departure d
JOIN Package p ON d.Package_ID=p.Package_ID
LEFT JOIN Booking b ON d.Depart_ID=b.Depart_ID AND b.Status!='Cancelled'
LEFT JOIN Traveller t ON b.Booking_ID=t.Booking_ID
GROUP BY d.Depart_ID;""",
                "Revenue vs refunds by customer": """SELECT c.Name, c.Email,
       COALESCE(SUM(pm.Amount),0) as Total_Paid,
       COALESCE(SUM(CASE WHEN r.Status IN('Approved','Processed') THEN r.Amount END),0) as Refunded
FROM Customer c
LEFT JOIN Booking b ON c.Cust_ID=b.Cust_ID
LEFT JOIN Payment pm ON b.Booking_ID=pm.Booking_ID
LEFT JOIN Cancellation cn ON b.Booking_ID=cn.Booking_ID
LEFT JOIN Refund r ON cn.Cancel_ID=r.Cancel_ID
GROUP BY c.Cust_ID;""",
                "Guide schedule summary": """SELECT g.Name, g.Language,
       COUNT(d.Depart_ID) as Assigned_Tours,
       MIN(d.Start_Date) as Next_Departure
FROM Guide g
LEFT JOIN Departure d ON g.Guide_ID=d.Guide_ID AND d.Status IN('Scheduled','In Progress')
GROUP BY g.Guide_ID;""",
            }
            preset_choice = st.selectbox("Sample Queries:", list(presets.keys()))
            query = st.text_area("SQL:", value=presets[preset_choice], height=140)

            if st.button("▶️ Run Query", use_container_width=True):
                ok, cols, rows, msg = db.run_raw_sql(query)
                if ok:
                    st.success(msg)
                    if cols:
                        st.dataframe(pd.DataFrame(rows, columns=cols), width="stretch")
                else:
                    st.error(msg)


# ════════════════════════════════════════════════════════════════════════════
# ROLE 2: CUSTOMER
# ════════════════════════════════════════════════════════════════════════════
elif role == "Customer (Lead Traveller)":

    # Customer selector at top
    customers = db.get_all_customers()
    cust_map  = {f"{c['Name']}  ·  {c['Email']}": c for c in customers}

    cl1, cl2 = st.columns([3, 1])
    with cl1:
        sel_cust_label = st.selectbox("Active Customer Profile:", list(cust_map.keys()), label_visibility="collapsed")
        active_cust = cust_map[sel_cust_label]
    with cl2:
        with st.expander("+ New Customer"):
            with st.form("reg_cust"):
                nc_name  = st.text_input("Full Name")
                nc_email = st.text_input("Email Address")
                if st.form_submit_button("Register"):
                    if nc_name and nc_email:
                        ok, nid, msg = db.add_customer(nc_name, nc_email)
                        if ok: st.success(msg); st.rerun()
                        else: st.error(msg)

    st.markdown(f"""
    <div style="background:#e0f2fe;border-radius:10px;padding:10px 16px;font-size:13px;color:#0369a1;margin-bottom:10px;">
        👤 Signed in as <b>{active_cust['Name']}</b> &nbsp;·&nbsp; {active_cust['Email']}
    </div>
    """, unsafe_allow_html=True)

    ct1, ct2, ct3 = st.tabs(["🌍 Explore Packages", "🎟️ Book a Tour", "📋 My Bookings"])

    # ── Explore ─────────────────────────────────────────────────────────────
    with ct1:
        packages = db.get_all_packages()
        for pkg in packages:
            det = db.get_package_details(pkg["Package_ID"])
            deps_for_pkg = db.get_all_departures(filter_package_id=pkg["Package_ID"], status_filter="Scheduled")
            avail_seats  = sum(d["Available_Seats"] for d in deps_for_pkg)

            with st.container():
                st.markdown(f"""
                <div class="pkg-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;">
                        <div style="flex:1;">
                            <div class="pkg-name">{pkg['Name']}</div>
                            <div class="pkg-dest">📍 {pkg['Dest_Name']}, {pkg['Country']} &nbsp;·&nbsp; ⏱️ {pkg['Duration_Days']} Days</div>
                        </div>
                        <div style="text-align:right;">
                            <div class="pkg-price">${pkg['Base_Price']:,.0f}<small>/person</small></div>
                            <div style="font-size:12px;color:{'#22c55e' if avail_seats>0 else '#ef4444'};font-weight:600;">
                                {'💺 '+str(avail_seats)+' seats available' if avail_seats>0 else '⛔ Sold out'}
                            </div>
                        </div>
                    </div>
                    <p style="font-size:13px;color:#475569;margin:10px 0 0;">{det['Dest_Description']}</p>
                </div>
                """, unsafe_allow_html=True)

                ex_col1, ex_col2 = st.columns(2)
                with ex_col1:
                    with st.expander(f"📅 View {pkg['Duration_Days']}-Day Itinerary"):
                        for day in det["itinerary"]:
                            st.markdown(f"""
                            <div class="itin-step">
                                <div class="itin-day">D{day['Day_Number']}</div>
                                <div class="itin-text">{day['Activity']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                with ex_col2:
                    with st.expander(f"🏨 Partner Hotels ({len(det['hotels'])} options)"):
                        for h in det["hotels"]:
                            stars = "★" * h["Star_Rating"]
                            st.markdown(f"**{h['Name']}** — {stars}")

    # ── Book ─────────────────────────────────────────────────────────────────
    with ct2:
        open_deps = db.get_all_departures(status_filter="Scheduled")
        if not open_deps:
            st.markdown('<div class="empty-state"><div class="empty-state-icon">🗓️</div><div class="empty-state-text">No open departures</div><div class="empty-state-sub">Check back soon for new tour dates</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-header">🗓️ Select a Departure</div>', unsafe_allow_html=True)

            # Departure cards
            dep_selection = {}
            for d in open_deps:
                pct = int(d["Booked_Seats"] / max(d["Max_Capacity"],1) * 100)
                is_available = d["Available_Seats"] > 0
                dep_selection[d["Depart_ID"]] = d

                status_txt = f"💺 {d['Available_Seats']} seats left" if is_available else "⛔ Fully booked"
                status_col = "#22c55e" if is_available else "#ef4444"
                st.markdown(f"""
                <div class="dep-card" style="border-left-color:{'#0ea5e9' if is_available else '#94a3b8'};">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                        <div>
                            <span style="font-weight:700;font-size:14px;">#{d['Depart_ID']} &nbsp;{d['Package_Name']}</span>
                            <span style="margin-left:8px;font-size:13px;color:#64748b;">📍 {d['Dest_Name']}</span>
                        </div>
                        <span style="color:{status_col};font-weight:600;font-size:13px;">{status_txt}</span>
                    </div>
                    <div class="info-row" style="margin-top:8px;">
                        <span>📅 {d['Start_Date']} → {d['End_Date']}</span>
                        <span>🧭 {d['Guide_Name']}</span>
                        <span>🚌 {d['Transport_Type']}</span>
                        <span>💰 ${d['Base_Price']:,.0f}/person</span>
                    </div>
                    <div class="cap-bar-wrap" style="margin-top:8px;">
                        <div class="cap-bar-fill" style="width:{pct}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="section-header">✍️ Booking Form</div>', unsafe_allow_html=True)

            avail_dep_opts = {
                f"#{d['Depart_ID']} · {d['Package_Name']}  ({d['Start_Date']})  — {d['Available_Seats']} seats left": d
                for d in open_deps if d["Available_Seats"] > 0
            }

            if not avail_dep_opts:
                st.warning("All departures are currently fully booked.")
            else:
                sel_dep_book = st.selectbox("Choose Departure:", list(avail_dep_opts.keys()))
                chosen_dep = avail_dep_opts[sel_dep_book]

                num_t = st.number_input(
                    "Number of Travellers (including yourself):",
                    min_value=1, max_value=chosen_dep["Available_Seats"],
                    value=min(2, chosen_dep["Available_Seats"])
                )
                total = chosen_dep["Base_Price"] * num_t
                st.markdown(f"""
                <div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;
                            padding:12px 16px;font-size:14px;color:#0369a1;margin:10px 0;">
                    💰 <b>Total: ${total:,.2f}</b> ({num_t} × ${chosen_dep['Base_Price']:,.2f})
                </div>
                """, unsafe_allow_html=True)

                traveller_data = []
                st.markdown("**👥 Traveller Details:**")
                for i in range(num_t):
                    tc1, tc2 = st.columns([3, 1])
                    with tc1:
                        name = st.text_input(f"Traveller {i+1} Name:",
                                              value=active_cust["Name"] if i==0 else "",
                                              key=f"tn_{i}")
                    with tc2:
                        age = st.number_input(f"Age:", min_value=0, max_value=120, value=30, key=f"ta_{i}")
                    traveller_data.append({"name": name, "age": age})

                if st.button("✅ Confirm Booking", use_container_width=True, type="primary"):
                    if any(not t["name"].strip() for t in traveller_data):
                        st.error("Please enter names for all travellers.")
                    else:
                        ok, msg, bid = db.create_booking_with_travellers(
                            active_cust["Cust_ID"], chosen_dep["Depart_ID"],
                            date.today().strftime("%Y-%m-%d"), traveller_data
                        )
                        if ok:
                            st.success(f"🎉 {msg}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")

    # ── My Bookings ──────────────────────────────────────────────────────────
    with ct3:
        my_bookings = db.get_customer_bookings(active_cust["Cust_ID"])
        if not my_bookings:
            st.markdown('<div class="empty-state"><div class="empty-state-icon">🎟️</div><div class="empty-state-text">No bookings yet</div><div class="empty-state-sub">Head to "Book a Tour" to reserve your first trip!</div></div>', unsafe_allow_html=True)
        else:
            for b in my_bookings:
                paid   = b["Total_Paid"]
                owed   = max(0.0, b["Total_Amount"] - paid)

                st.markdown(f"""
                <div class="booking-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                        <div>
                            <span style="font-weight:700;font-size:15px;">#{b['Booking_ID']} &nbsp;{b['Package_Name']}</span>
                            &nbsp;&nbsp;{badge_html(b['Status'])}
                        </div>
                        <div style="font-size:18px;font-weight:700;color:#0ea5e9;">${b['Total_Amount']:,.2f}</div>
                    </div>
                    <div class="info-row" style="margin-top:8px;">
                        <span>📍 {b['Dest_Name']}, {b['Country']}</span>
                        <span>📅 {b['Start_Date']} → {b['End_Date']}</span>
                        <span>🧭 {b['Guide_Name']}</span>
                        <span>💳 Paid: ${paid:,.2f} | Owed: ${owed:,.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Travellers & Payments inline
                bc1, bc2 = st.columns(2)
                with bc1:
                    st.markdown("**👥 Travellers**")
                    for t in b["travellers"]:
                        st.markdown(f"""
                        <div class="manifest-row">
                            <div class="manifest-avatar">{t['Name'][0].upper()}</div>
                            <div>{t['Name']} &nbsp;<span style="color:#94a3b8;font-size:12px;">{t['Age']} yrs</span></div>
                        </div>
                        """, unsafe_allow_html=True)

                with bc2:
                    st.markdown("**💳 Payments**")
                    if b["payments"]:
                        for p in b["payments"]:
                            st.markdown(f"- ${p['Amount']:,.2f}  ·  {p['Payment_Date']}")
                    else:
                        st.caption("No payments recorded.")

                # Action row
                if b["Status"] not in ("Cancelled",):
                    ac1, ac2 = st.columns(2)
                    with ac1:
                        with st.expander(f"💳 Add Payment"):
                            pay_amt = st.number_input("Amount ($):", min_value=1.0,
                                                       max_value=max(1.0, b["Total_Amount"]),
                                                       value=max(1.0, owed) if owed > 0 else 100.0,
                                                       key=f"payamt_{b['Booking_ID']}")
                            if st.button(f"Pay ${pay_amt:,.2f}", key=f"paybtn_{b['Booking_ID']}"):
                                ok, msg = db.record_payment(b["Booking_ID"], pay_amt, date.today().strftime("%Y-%m-%d"))
                                if ok: st.success(msg); st.rerun()
                                else: st.error(msg)

                    with ac2:
                        with st.expander("⚠️ Cancel Booking"):
                            st.warning("This will release your seats and submit a refund request.")
                            c_reason = st.text_area("Reason:", key=f"creason_{b['Booking_ID']}")
                            if st.button("Confirm Cancellation", key=f"cbtn_{b['Booking_ID']}"):
                                if not c_reason.strip():
                                    st.error("Please provide a cancellation reason.")
                                else:
                                    ok, msg = db.cancel_booking_and_request_refund(
                                        b["Booking_ID"], date.today().strftime("%Y-%m-%d"), c_reason
                                    )
                                    if ok: st.success(msg); st.rerun()
                                    else: st.error(msg)
                else:
                    st.markdown(f"""
                    <div class="integrity-panel">
                        ❌ <b>Cancelled</b> on {b['Cancel_Date']} — {b['Cancel_Reason']}<br>
                        Refund: <b>{b['Refund_Status'] or '—'}</b>
                        {f"  ·  ${b['Refund_Amount']:,.2f}" if b['Refund_Amount'] else ""}
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")


# ════════════════════════════════════════════════════════════════════════════
# ROLE 3: TOUR GUIDE
# ════════════════════════════════════════════════════════════════════════════
elif role == "Tour Guide":
    guides    = db.get_all_guides()
    guide_map = {f"{g['Name']}  ({g['Language']})": g for g in guides}

    gl1, gl2 = st.columns([3, 1])
    with gl1:
        sel_guide_label = st.selectbox("🧭 Select Your Guide Profile:", list(guide_map.keys()))
        active_guide = guide_map[sel_guide_label]
    with gl2:
        st.markdown(f"""
        <div style="background:#d1fae5;border-radius:10px;padding:10px 14px;font-size:13px;color:#065f46;margin-top:26px;">
            📞 {active_guide['Contact']}
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#d1fae5;border-radius:10px;padding:10px 16px;font-size:13px;color:#065f46;margin-bottom:12px;">
        🧭 <b>{active_guide['Name']}</b> &nbsp;·&nbsp; Languages: {active_guide['Language']}
        &nbsp;·&nbsp; Read-only access
    </div>
    """, unsafe_allow_html=True)

    departures = db.get_guide_roster(active_guide["Guide_ID"])

    if not departures:
        st.markdown('<div class="empty-state"><div class="empty-state-icon">🗓️</div><div class="empty-state-text">No assigned departures</div><div class="empty-state-sub">You have no upcoming or active tours at this time.</div></div>', unsafe_allow_html=True)
    else:
        # Summary stats
        gs1, gs2, gs3 = st.columns(3)
        with gs1:
            st.markdown(f"""<div class="stat-card">
                <div class="stat-icon">🗓️</div>
                <div class="stat-label">Assigned Tours</div>
                <div class="stat-value">{len(departures)}</div>
            </div>""", unsafe_allow_html=True)
        with gs2:
            total_pax = sum(len(d["manifest"]) for d in departures)
            st.markdown(f"""<div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-label">Total Passengers</div>
                <div class="stat-value">{total_pax}</div>
            </div>""", unsafe_allow_html=True)
        with gs3:
            active_count = sum(1 for d in departures if d["Status"] in ("In Progress","Scheduled"))
            st.markdown(f"""<div class="stat-card">
                <div class="stat-icon">🟢</div>
                <div class="stat-label">Active / Upcoming</div>
                <div class="stat-value">{active_count}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")

        # Departure selector
        dep_options = {
            f"#{d['Depart_ID']} · {d['Package_Name']}  ({d['Start_Date']} → {d['End_Date']})  [{d['Status']}]": d
            for d in departures
        }
        sel_dep_label = st.selectbox("📋 Select Tour to Inspect:", list(dep_options.keys()))
        insp = dep_options[sel_dep_label]

        # Header card
        pct = int(len(insp["manifest"]) / max(insp["Max_Capacity"],1) * 100)
        st.markdown(f"""
        <div class="dep-card" style="border-left-color:#10b981;">
            <div style="font-weight:700;font-size:15px;color:#0f172a;">
                {insp['Package_Name']} &nbsp;{badge_html(insp['Status'])}
            </div>
            <div class="info-row" style="margin-top:8px;">
                <span>📍 {insp['Dest_Name']}</span>
                <span>📅 {insp['Start_Date']} → {insp['End_Date']}</span>
                <span>🚌 {insp['Transport_Type']} ({insp['Transport_Capacity']} seats)</span>
                <span>💺 {len(insp['manifest'])} / {insp['Max_Capacity']} confirmed</span>
            </div>
            <div class="cap-bar-wrap" style="margin-top:8px;">
                <div class="cap-bar-fill" style="width:{pct}%;background:linear-gradient(90deg,#10b981,#059669);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        gt1, gt2 = st.tabs(["👥 Passenger Manifest", "📅 Tour Itinerary"])

        with gt1:
            if insp["manifest"]:
                for m in insp["manifest"]:
                    initials = "".join(w[0].upper() for w in m["Traveller_Name"].split()[:2])
                    st.markdown(f"""
                    <div class="manifest-row">
                        <div class="manifest-avatar">{initials}</div>
                        <div style="flex:1;">
                            <div style="font-weight:600;color:#0f172a;">{m['Traveller_Name']}</div>
                            <div style="font-size:12px;color:#64748b;">Age {m['Age']} &nbsp;·&nbsp; Booking #{m['Booking_ID']} &nbsp;·&nbsp; Lead: {m['Lead_Customer']}</div>
                        </div>
                        <div style="font-size:12px;color:#0ea5e9;">{m['Contact_Email']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="empty-state"><div class="empty-state-icon">👥</div><div class="empty-state-text">No passengers yet</div></div>', unsafe_allow_html=True)

        with gt2:
            if insp["itinerary"]:
                for item in insp["itinerary"]:
                    st.markdown(f"""
                    <div class="itin-step">
                        <div class="itin-day" style="background:#10b981;">D{item['Day_Number']}</div>
                        <div class="itin-text">{item['Activity']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="empty-state"><div class="empty-state-icon">📅</div><div class="empty-state-text">No itinerary recorded</div></div>', unsafe_allow_html=True)
