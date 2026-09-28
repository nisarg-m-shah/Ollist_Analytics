import streamlit as st
import os
from components.header import render_header

def metric_block(label, value, sub=""):
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 0.9rem 1rem;">
        <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">{label}</div>
        <div style="font-size: 1.4rem; font-weight: 800; color: #f8fafc; margin-top: 0.15rem;">{value}</div>
        <div style="font-size: 0.72rem; color: #64748b; margin-top: 0.1rem;">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

def step_card(number, title, why, how):
    st.markdown(f"""
    <div class="insight-card-wrapper default" style="margin-bottom: 0.75rem;">
        <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
            <div style="background: #6366F1; color: white; font-weight: 800; border-radius: 50%; width: 28px; height: 28px; min-width: 28px; display: flex; align-items: center; justify-content: center; font-size: 0.85rem;">{number}</div>
            <div>
                <div style="font-weight: 800; color: #f8fafc; font-size: 0.95rem;">{title}</div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.3rem;"><strong style="color:#818cf8;">Why:</strong> {why}</div>
                <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 0.25rem;"><strong style="color:#38bdf8;">How:</strong> {how}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def limitation_item(icon, title, text):
    st.markdown(f"""
    <div style="border-left: 3px solid #F59E0B; background: rgba(245, 158, 11, 0.06); border-radius: 0 8px 8px 0; padding: 0.7rem 1rem; margin-bottom: 0.6rem;">
        <div style="font-weight: 700; color: #f8fafc; font-size: 0.85rem;">{icon} {title}</div>
        <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 0.2rem; line-height: 1.5;">{text}</div>
    </div>
    """, unsafe_allow_html=True)

def render_page_data_prep():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'style.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    filters = st.session_state.get('filters', {})
    render_header(
        page_title="Data Preparation, Feature Engineering & Limitations",
        page_subtitle="What the raw Olist data looked like, what was done to it before any chart was built, and where the analysis should be read with caution.",
        active_filters=filters
    )

    st.info(
        "This page documents the fixed preparation pipeline (`preprocess.py`) that runs once, before any chart on "
        "the other pages is built. It describes the full raw dataset and does not respond to the sidebar filters — "
        "filtering happens after this pipeline has already run.",
        icon="ℹ️"
    )

    # ---------------------------------------------------------------
    # SECTION 1 — Raw data, as received
    # ---------------------------------------------------------------
    st.markdown("""
    <div class="chart-header">
        <h3 class="chart-title">1. The Raw Data</h3>
        <div class="chart-subtitle">Nine linked CSVs from the public Olist Brazilian E-Commerce dataset, September 2016 – October 2018.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_block("Orders", "99,441", "olist_orders_dataset")
    with c2: metric_block("Order Line Items", "112,650", "olist_order_items_dataset")
    with c3: metric_block("Payments", "103,886", "olist_order_payments_dataset")
    with c4: metric_block("Reviews", "99,224", "olist_order_reviews_dataset")
    c5, c6, c7, c8 = st.columns(4)
    with c5: metric_block("Products", "32,951", "olist_products_dataset")
    with c6: metric_block("Sellers", "3,095", "olist_sellers_dataset")
    with c7: metric_block("Customers", "99,441 rows", "96,096 unique people")
    with c8: metric_block("Raw Categories", "73", "+ 610 products with none")

    st.markdown("<div style='margin-top: 0.9rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 0.85rem; color: #94a3b8; line-height: 1.6;">
        Each customer row is actually an <em>order-specific</em> identity — the same person gets a new
        <code>customer_id</code> per order, which is why 99,441 customer rows collapse to 96,096 unique
        people once grouped by <code>customer_unique_id</code>. Left uncorrected, this alone would make
        every customer look like a one-time buyer.
        The bundled dataset intentionally excludes <code>olist_geolocation_dataset</code> (1M+ raw lat/long
        pings) — every map and region view in this app works at the city/state level, not coordinate precision.
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------------
    # SECTION 2 — Data quality issues found before cleaning
    # ---------------------------------------------------------------
    st.markdown("""
    <div class="chart-header" style="margin-top: 1.5rem;">
        <h3 class="chart-title">2. Data Quality Issues Identified</h3>
        <div class="chart-subtitle">What was actually wrong with the raw files, found before deciding how to clean them.</div>
    </div>
    """, unsafe_allow_html=True)

    dq1, dq2, dq3 = st.columns(3)
    with dq1:
        metric_block("Missing Delivery Dates", "2,965 orders", "no order_delivered_customer_date")
        metric_block("Multi-Payment Orders", "2,961 orders", "split across 2+ payment rows")
    with dq2:
        metric_block("Products Missing Category", "610 products", "1,603 line items affected")
        metric_block("Orders With No Review", "768 orders", "0.8% of all orders")
    with dq3:
        metric_block("Untranslated Categories", "2 of 73", "pc_gamer, portateis_cozinha...")
        metric_block("Multi-Seller Orders", "1,278 orders", "1.3% ship from 2+ sellers")

    st.markdown("<div style='margin-top: 0.6rem; font-size: 0.8rem; color: #94a3b8;'>Also found: 547 orders carry more than one review, and 8 orders are marked <code>delivered</code> yet have no delivery-date timestamp at all — a genuine data-entry inconsistency in the source files, not something introduced during cleaning.</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------------
    # SECTION 3 — Cleaning & feature engineering steps
    # ---------------------------------------------------------------
    st.markdown("""
    <div class="chart-header" style="margin-top: 1.5rem;">
        <h3 class="chart-title">3. Cleaning & Feature Engineering Pipeline</h3>
        <div class="chart-subtitle">Runs once in preprocess.py and is cached to Parquet — every chart in the app reads the already-cleaned output, never the raw CSVs.</div>
    </div>
    """, unsafe_allow_html=True)

    step_card(1, "Parse five raw date columns into calendar features",
        "Weekday and time-of-day patterns (Page: Delivery Analytics) don't exist in a raw timestamp string; they have to be derived once.",
        "order_purchase_timestamp → year, quarter, month, sortable year_month, weekday name, purchase hour, and a 4-hour time window.")
    step_card(2, "Compute delivery outcome from estimate vs. actual date",
        "Every delivery and review chart needs one consistent definition of 'late' — computing it differently per chart is a classic dashboard bug.",
        "cal_late_days = calendar-day gap between delivered and estimated date → is_delivered, is_late, delivery_outcome (On time / Late / Not delivered), delay_bucket (On time or early / 1-3 / 4-7 / 8+ days late).")
    step_card(3, "Map 27 customer/seller states to 5 macro-regions",
        "State-level charts are too granular for a Sankey or a region-level heatmap; Brazil's own 5 official regions are the natural aggregation.",
        "A hand-built STATE_TO_REGION lookup applied to both customers and sellers.")
    step_card(4, "Translate category names, with a fallback instead of a drop",
        "2 of 73 categories and 610 products have no translation or category at all — dropping them would silently understate category totals.",
        "clean_category_name(): use the English translation where it exists; otherwise title-case the original Portuguese name; otherwise label 'Other / Uncategorized'.")
    step_card(5, "Collapse split payments to one row per order",
        "An order can have several payment rows (installments, gift card + card); charting payments directly would double-count orders.",
        "Aggregate to a total paid, an installment count, and a 'dominant' payment type — the one contributing the largest share of that order's value.")
    step_card(6, "Average review scores per order",
        "547 orders carry more than one review; without averaging first, those orders would be counted twice in every review statistic.",
        "Mean review_score grouped by order_id, before joining back onto orders.")
    step_card(7, "Build three grain-specific master tables",
        "A category filter needs to reach line-item-level revenue, not just order totals — using the wrong grain was the root cause of a real bug caught in an earlier, non-Python version of this project (Power BI's category filter not propagating to revenue).",
        "orders_master (one row per order), items_master (one row per line item, order-level fields merged in), payments_master (one row per payment) — each chart reads whichever grain its question actually needs.")

    # ---------------------------------------------------------------
    # SECTION 4 — Data limitations
    # ---------------------------------------------------------------
    st.markdown("""
    <div class="chart-header" style="margin-top: 1.5rem;">
        <h3 class="chart-title">4. Data Limitations</h3>
        <div class="chart-subtitle">What the dataset itself cannot tell you, regardless of how it's analyzed.</div>
    </div>
    """, unsafe_allow_html=True)

    limitation_item("📅", "\"Late\" is relative to Olist's own estimate, not an absolute speed benchmark",
        "order_estimated_delivery_date is the promise Olist showed the customer at checkout, not an independent standard. A 20-day delivery estimated at 25 days is 'on time' here — the app is measuring promise-keeping, not raw delivery speed.")
    limitation_item("🚫", "2,965 orders have no delivery date at all",
        "These are treated as 'Not Delivered' throughout the app, including 8 rows whose status is literally 'delivered' but the timestamp is missing — a source data-entry gap that cannot be reconstructed, only excluded.")
    limitation_item("👥", "Reviews can reflect the seller or courier, not just the product",
        "The dataset cannot separate whether a low score was about the item itself, the seller's packaging, or the delivery experience — Page 4's delay-vs-rating analysis assumes delivery timing is a major driver, which the data supports strongly, but it isn't the only possible cause.")
    limitation_item("📦", "Multi-seller orders (1.3%) are attributed to a single seller/region",
        "Where an order ships from two sellers, seller- and region-level views (the Sankey, the seller scatter) use only the first line item's seller — a simplification, not an error, but one worth stating out loud.")
    limitation_item("💰", "No cost, margin, or marketing-spend data exists",
        "Every 'impact' claim in this app is about revenue and customer satisfaction, not profitability — a recommendation to invest in a region says nothing about whether that investment would be profitable, only that it targets real revenue and real dissatisfaction.")
    limitation_item("🗺️", "No coordinate-level geolocation data",
        "This build works at the city/state level; it cannot show delivery-route distances or true last-mile geography, only which state or city an order is associated with.")
    limitation_item("🕰️", "The dataset is frozen at October 2018",
        "None of this reflects Olist's current carrier network, seller base, or pricing — it's a historical snapshot, useful for the analytical method demonstrated, not for operating a 2026 business decision without new data.")

    # ---------------------------------------------------------------
    # SECTION 5 — Visual / methodological limitations
    # ---------------------------------------------------------------
    st.markdown("""
    <div class="chart-header" style="margin-top: 1.5rem;">
        <h3 class="chart-title">5. Visual & Methodological Limitations</h3>
        <div class="chart-subtitle">Choices made while building the charts themselves, worth knowing before quoting a number from them.</div>
    </div>
    """, unsafe_allow_html=True)

    limitation_item("📈", "Every delay-vs-rating relationship is an association, not a proven cause",
        "The delay-bucket rating collapse, the monthly late-rate/review-score chart, and the root-cause decomposition tree all show strong, consistent patterns — but the dataset alone cannot rule out other explanations happening at the same time.")
    limitation_item("🎯", "The seller scatter's 'meaningful sample' threshold is a judgment call",
        "Sellers are only compared once they have 5+ delivered orders; a stricter or looser threshold would change exactly which sellers appear as outliers, though the overall 'volume doesn't predict reliability' finding is stable across reasonable thresholds.")
    limitation_item("⭐", "The treemap's category color is a simple average, not a confidence-weighted one",
        "A category with a handful of reviews and a category with thousands both get a single average-rating color; the treemap already filters to categories with 30+ items sold to reduce this risk, but small-sample noise isn't eliminated entirely.")

    st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 1.5rem 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(16, 185, 129, 0.08) 100%); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 12px; padding: 1.35rem;">
        <div style="font-size: 1.05rem; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 0.5rem;">
            <span>➡️</span> From Preparation to Performance
        </div>
        <div style="font-size: 0.82rem; color: #cbd5e1; margin-top: 0.35rem; line-height: 1.5;">
            With the data understood and its limits stated up front, the next page starts the actual analysis:
            how is the business performing?
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
    if st.button("Continue to Executive Overview →", use_container_width=True, type="primary"):
        st.switch_page("pages/02_Executive_Overview.py")

render_page_data_prep()