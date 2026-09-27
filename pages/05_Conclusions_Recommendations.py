import streamlit as st
import os
from analytics.data_loader import load_analytical_data, apply_global_filters
from analytics.sales import get_executive_kpis, get_top_states_by_revenue, get_state_revenue_statistics
from analytics.customers import get_customer_kpis, get_customers_by_order_frequency, get_order_frequency_statistics
from analytics.delivery import get_delivery_kpis, get_seller_volume_vs_ontime, get_carrier_handoff_heatmap
from analytics.reviews import get_review_kpis
from analytics.insights import generate_strategic_recommendations
from components.header import render_header
from components.kpi_cards import render_kpi_cards
from components.insight_cards import render_summary_banner
from utils.formatting import format_currency, format_number

PRIORITY_STYLE = {
    "High": ("alert", "🔴 HIGH PRIORITY"),
    "Medium": ("warning", "🟡 MEDIUM PRIORITY"),
    "Low": ("default", "🟢 LOW PRIORITY")
}

def render_recommendation_card(rec):
    """
    Renders one strategic recommendation using the same insight-card visual
    language as Pages 1-4, so this page feels like a continuation of the
    dashboard rather than a bolted-on afterthought.
    """
    card_type, priority_label = PRIORITY_STYLE.get(rec["priority"], ("default", rec["priority"].upper()))

    card_html = f"""
    <div class="insight-card-wrapper {card_type}">
        <div class="insight-header">
            <span class="insight-tag">
                <span>🎯</span> {rec['pillar']}
            </span>
            <span style="font-size: 0.7rem; color: #64748b; font-weight: 700;">{priority_label}</span>
        </div>
        <div style="font-size: 0.68rem; font-weight: 700; color: #818cf8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.2rem;">💡 Finding</div>
        <div class="insight-finding">
            {rec['headline']}
        </div>
        <div class="insight-evidence">
            <strong style="color: #38bdf8;">📌 EVIDENCE:</strong> {rec['evidence']}
        </div>
        <div class="insight-grid">
            <div>
                <div class="insight-block-label">✅ Recommended Action</div>
                <div class="insight-block-content">{rec['recommendation']}</div>
            </div>
            <div>
                <div class="insight-block-label">📈 Expected Impact</div>
                <div class="insight-block-content">{rec['expected_impact']}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_page_5():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'style.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Load Master Data
    orders_master, items_master, payments_master = load_analytical_data()
    filters = st.session_state.get('filters', {})

    # Filter Data
    orders_df, items_df, payments_df = apply_global_filters(
        orders_master, items_master, payments_master, filters
    )

    render_header(
        page_title="Conclusions & Strategic Recommendations",
        page_subtitle="Closing synthesis answering: Having seen sales, customers, delivery, and reviews separately — what should the business actually do?",
        active_filters=filters
    )

    with st.expander("🎯 Closing Story • Tying Four Pages Into One Decision", expanded=True):
        st.markdown("""
        <div style="font-size: 0.9rem; color: #cbd5e1; line-height: 1.6;">
            <p style="margin-bottom: 0.5rem; font-weight: 600; color: #f8fafc;">
                "We've now looked at business performance, customer and product intelligence, delivery
                operations, and customer sentiment as four separate questions. This page closes the loop:
                what does the evidence, taken together, actually recommend doing next?"
            </p>
            <p style="margin: 0; color: #94a3b8;">
                Every finding below is computed from the same filtered data shown on the previous four pages —
                nothing here is a separate, hardcoded claim.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Recompute the cross-page KPIs needed for the synthesis (same calls Pages 1-4 already make)
    exec_kpis = get_executive_kpis(orders_df, items_df, payments_df)
    cust_kpis = get_customer_kpis(orders_df, items_df)
    deliv_kpis = get_delivery_kpis(orders_df)
    rev_kpis = get_review_kpis(orders_df)

    state_df = get_top_states_by_revenue(orders_df, top_n=10)
    state_stats = get_state_revenue_statistics(state_df, total_revenue=exec_kpis.get('total_revenue'))

    freq_df = get_customers_by_order_frequency(orders_df)
    freq_stats = get_order_frequency_statistics(freq_df)

    seller_df = get_seller_volume_vs_ontime(items_df, min_orders=5)
    heatmap_df = get_carrier_handoff_heatmap(orders_df)

    # Headline KPI strip spanning all four pillars
    render_kpi_cards([
        {
            'label': 'Total Revenue',
            'value': format_currency(exec_kpis['total_revenue']),
            'sub': f"{format_number(exec_kpis['total_orders'])} orders",
            'icon': '💳',
            'color': '#10B981'
        },
        {
            'label': 'Repeat Customer Rate',
            'value': f"{cust_kpis['repeat_rate']:.1f}%",
            'sub': 'Of unique buyers',
            'icon': '🔄',
            'color': '#6366F1'
        },
        {
            'label': 'On-Time Delivery',
            'value': f"{deliv_kpis['ontime_pct']:.1f}%",
            'sub': f"{deliv_kpis['late_delivery_pct']:.1f}% late",
            'icon': '🚚',
            'color': '#38BDF8'
        },
        {
            'label': 'Avg Review Score',
            'value': f"{rev_kpis['avg_review_score']:.2f}",
            'sub': 'Scale of 1.0 to 5.0',
            'icon': '⭐',
            'color': '#F59E0B'
        },
        {
            'label': 'Sentiment Cliff',
            'value': f"-{rev_kpis['rating_gap']:.2f}",
            'sub': 'On-time vs 8+ days late',
            'icon': '📉',
            'color': '#F43F5E'
        }
    ])

    # Build the cross-page synthesis and prioritized recommendations
    synthesis_data = generate_strategic_recommendations(
        exec_kpis, cust_kpis, deliv_kpis, rev_kpis,
        state_stats, freq_stats, seller_df, heatmap_df
    )

    render_summary_banner(
        title="📋 Executive Synthesis — What the Four Pages Add Up To",
        text=synthesis_data['synthesis'],
        icon="🧭",
        variant="default"
    )

    st.markdown("""
    <div class="chart-header" style="margin-top: 1.25rem;">
        <h3 class="chart-title">Prioritized Strategic Recommendations</h3>
        <div class="chart-subtitle">Ranked by urgency, each tied directly to a finding from Pages 1-4.</div>
    </div>
    """, unsafe_allow_html=True)

    for rec in synthesis_data['recommendations']:
        render_recommendation_card(rec)

    st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # Transition to Work Distribution
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(16, 185, 129, 0.08) 100%); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 12px; padding: 1.35rem;">
        <div style="font-size: 1.05rem; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 0.5rem;">
            <span>➡️</span> From Recommendations to Project Governance
        </div>
        <div style="font-size: 0.82rem; color: #cbd5e1; margin-top: 0.35rem; line-height: 1.5;">
            That completes the analytical narrative: business performance, customer and product intelligence, delivery
            operations, customer experience, and now the recommendations tying them together.
            The final page documents how this project itself was built and divided.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
    if st.button("Continue to Work Distribution →", use_container_width=True, type="primary"):
        st.switch_page("pages/06_Work_Distribution.py")

render_page_5()
