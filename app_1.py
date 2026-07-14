import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & THEME SETUP
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SaaS & Subscription Retention Suite",

    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom SaaS Branding (Clean, Corporate, Colorful)
st.markdown("""
    <style>
    .main-header { font-size: 36px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .sub-header { font-size: 16px; color: #6B7280; margin-bottom: 25px; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA UTILITIES & CACHING
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_and_preprocess_data():
    # Adjust filename to match your exact upload string
    possible_files=["Telco_Customer_Churn_Cleaned.xlsx","Telco_Customer_Churn_Cleaned.csv","WA_Fn-UseC_-Telco-Customer-Churn.csv"]
    df=None
    for file_path in possible_files:
        try:
            if file_path.endswith(".xlsx"):
                df=pd.read_excel(file_path)
            else:
                df=pd.read_csv(file_path)
            break
        except Exception:
            continue
    if df is None:
        st.error(" Dataset not found. Place the dataset beside app.py.")
        st.stop()
        

    required_columns=["Churn","MonthlyCharges","TotalCharges","tenure","Contract","InternetService","PaperlessBilling","PaymentMethod"]
    missing=[c for c in required_columns if c not in df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}")
        st.stop()
    df["Churn"]=df["Churn"].astype(str).str.strip().str.title()
    df["MonthlyCharges"]=pd.to_numeric(df["MonthlyCharges"],errors="coerce").fillna(0)

    # Standardize data structures for advanced analytical layers
    df['Churn_Numeric'] = df['Churn'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0)
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(df['MonthlyCharges'])
    df['tenure'] = pd.to_numeric(df['tenure'], errors='coerce').fillna(0)
    
    # Segment tenure into standard SaaS lifecycle cohorts
    def get_cohort(months):
        if months <= 6: return "0-6 Months (Onboarding Risk)"
        elif months <= 12: return "7-12 Months (Early Stage)"
        elif months <= 24: return "1-2 Years (Mid-Tier)"
        else: return "2+ Years (Mature Growth)"
    
    df['Lifecycle_Cohort'] = df['tenure'].apply(get_cohort)
    return df

df = load_and_preprocess_data()

# -----------------------------------------------------------------------------
# 3. GLOBAL CONTROLS (SIDEBAR)
# -----------------------------------------------------------------------------

st.sidebar.title("Strategic Filters")
st.sidebar.markdown("Slice customer portfolios across key commercial dimensions:")

# Executive Filters
contract_filter = st.sidebar.multiselect("Contract Architecture", options=df['Contract'].unique(), default=df['Contract'].unique())
internet_filter = st.sidebar.multiselect("Core Infrastructure Mix", options=df['InternetService'].unique(), default=df['InternetService'].unique())
billing_filter = st.sidebar.multiselect("Paperless Invoicing", options=df['PaperlessBilling'].unique(), default=df['PaperlessBilling'].unique())

# Querying Data
filtered_df = df[
    (df['Contract'].isin(contract_filter)) &
    (df['InternetService'].isin(internet_filter)) &
    (df['PaperlessBilling'].isin(billing_filter))
]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# -----------------------------------------------------------------------------
# 4. EXECUTIVE HERO BANNER & KPls
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">SaaS Executive Retention & Churn Intelligence Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Live diagnostic advisory platform for tracking revenue churn drivers, customer lifetime health, and active save-playbooks.</div>', unsafe_allow_html=True)

# Strategic Metric Card Computations
total_subscribers = len(filtered_df)
churn_events = filtered_df['Churn_Numeric'].sum()
churn_rate = (churn_events / total_subscribers * 100) if total_subscribers > 0 else 0
mrr_at_risk = filtered_df[filtered_df['Churn'] == 'Yes']['MonthlyCharges'].sum() if churn_events > 0 else 0
avg_lifetime_value = filtered_df['TotalCharges'].mean()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'''
        <div class="metric-card">
            <h5>Active Subscriptions</h5>
            <h2 style="color: #000000 !important;">{total_subscribers:,}</h2>
            <p>Total Account Coverage</p>
        </div>
    ''', unsafe_allow_html=True)

with col2:
    # Set dynamic alert color: red for high-risk churn, green for healthy baseline
    churn_color = "#DC2626" if churn_rate > 20 else "#16A34A"
    st.markdown(f'''
        <div class="metric-card">
            <h5>Gross Churn Rate</h5>
            <h2 style="color: {churn_color} !important;">{churn_rate:.2f}%</h2>
            <p>Target Baseline: &lt; 5.0%</p>
        </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
        <div class="metric-card">
            <h5>MRR Leaking At Risk</h5>
            <h2 style="color: #DC2626 !important;">${mrr_at_risk:,.2f}</h2>
            <p>Monthly Charges on Churned Accounts</p>
        </div>
    ''', unsafe_allow_html=True)

with col4:
    st.markdown(f'''
        <div class="metric-card">
            <h5>Average LTV</h5>
            <h2 style="color: #16A34A !important;">${avg_lifetime_value:,.2f}</h2>
            <p>Realized Contract Lifetime Value</p>
        </div>
    ''', unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. CORE DIAGNOSTIC TABS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    " Churn Drivers & Segment Risk",
    "Lifecycle Cohorts & Longevity",
    " Financial Health Matrix",
    "Automated Advisory Playbook"
])

# -----------------------------------------------------------------------------
# TAB 1: CHURN DRIVERS & SEGMENT RISK
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("High-Risk Structural Vectors")
    st.markdown("Identify which systemic dimensions have structurally high user exit rates.")
    
    c1, c2 = st.columns(2)
    
    with c1:
        # Contract Structure vs Churn Risk
        contract_churn = filtered_df.groupby('Contract')['Churn_Numeric'].mean().reset_index()
        contract_churn['Churn_Numeric'] *= 100
        
        fig_contract = px.bar(
            contract_churn, x='Contract', y='Churn_Numeric',
            title='Churn Probability by Commitment Model',
            labels={'Churn_Numeric': 'Churn Probability (%)', 'Contract': 'Contract Architecture'},
            color='Contract', color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_contract.update_layout(showlegend=False, yaxis_ticksuffix="%")
        st.plotly_chart(fig_contract, use_container_width=True)
        
    with c2:
        # Tech Infrastructure vs Churn Risk
        tech_churn = filtered_df.groupby('InternetService')['Churn_Numeric'].mean().reset_index()
        tech_churn['Churn_Numeric'] *= 100
        
        fig_tech = px.bar(
            tech_churn, x='InternetService', y='Churn_Numeric',
            title='Churn Probability by Infrastructure Core',
            labels={'Churn_Numeric': 'Churn Probability (%)', 'InternetService': 'Tech Ecosystem'},
            color='InternetService', color_discrete_sequence=px.colors.sequential.Viridis
        )
        fig_tech.update_layout(showlegend=False, yaxis_ticksuffix="%")
        st.plotly_chart(fig_tech, use_container_width=True)

    st.markdown("Feature Matrix Drill-Down")
    # Multivariable Heatmap style matrix using boxplots or breakdown metrics
    feature_select = st.selectbox("Isolate Auxiliary Feature for Deep-Dive Analysis:", 
                                  options=['PaymentMethod', 'OnlineSecurity', 'TechSupport', 'PaperlessBilling', 'SeniorCitizen'])
    
    feat_df = filtered_df.groupby(feature_select)['Churn_Numeric'].agg(['count', 'mean']).reset_index()
    feat_df['mean'] *= 100
    feat_df.columns = [feature_select, 'Total Accounts', 'Churn Rate (%)']
    
    fig_feat = px.bar(
        feat_df, x=feature_select, y='Churn Rate (%)', text=feat_df['Churn Rate (%)'].apply(lambda x: f"{x:.1f}%"),
        title=f"Granular Churn Signature Across: {feature_select}",
        color='Churn Rate (%)', color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_feat, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: LIFECYCLE COHORTS & LONGEVITY
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("Account Age Distribution and Decay Profile")
    st.markdown("SaaS valuation and Unit Economics live or die by user distribution curves. Review the structural longevity metrics below.")

    # Tenure Over Time Curve
    fig_density = px.histogram(
        filtered_df,
        x="tenure",
        color="Churn",
        title="Survival Matrix: Distribution of Account Tenure Length (Months)",
        labels={
            "tenure": "Months Active on Platform",
            "count": "Subscribers"
        },
        barmode="overlay",
        color_discrete_map={
            "No": "#3B82F6",
            "Yes": "#EF4444"
        }
    )

    fig_density.update_layout(
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig_density, use_container_width=True)

    c3, c4 = st.columns([2, 1])
    with c3:
        # Cohort Segmentation
        cohort_order = ["0-6 Months (Onboarding Risk)", "7-12 Months (Early Stage)", "1-2 Years (Mid-Tier)", "2+ Years (Mature Growth)"]
        cohort_summary = filtered_df.groupby('Lifecycle_Cohort')['Churn_Numeric'].mean().reindex(cohort_order).reset_index()
        cohort_summary['Churn_Numeric'] *= 100
        
        fig_cohort = px.line(
            cohort_summary, x='Lifecycle_Cohort', y='Churn_Numeric', markers=True,
            title='Structural Hazard Curve Across Critical Lifecycle Milestones',
            labels={'Churn_Numeric': 'Churn Probability (%)', 'Lifecycle_Cohort': 'Lifecycle Bucket'}
        )
        fig_cohort.update_traces(line_color='#2563EB', line_width=4, marker=dict(size=10, color='#DC2626'))
        fig_cohort.update_layout(yaxis_ticksuffix="%")
        st.plotly_chart(fig_cohort, use_container_width=True)
    
    with c4:
        st.markdown("Key Retention Takeaway")
        st.info(
            "The Critical Cliff Pattern:\n\n"
            "Data highlights that churn concentrates heavily in the early months. Accounts surviving "
            "past month 12 transition into standard platform lifecycles where churn risks fall dramatically. "
            "Strategic Pivot:** Redirect customer-success capital into immediate post-onboarding stabilization."
        )

# -----------------------------------------------------------------------------
# TAB 3: FINANCIAL HEALTH MATRIX
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("Price-Elasticity and Revenue Leaks")
    st.markdown("Analyze how subscription tiering affects account retention profiles.")
    
    # Box plot showing Pricing distribution vs Churn
    fig_box = px.box(
        filtered_df, x="Churn", y="MonthlyCharges", color="Churn",
        title="Price Elasticity: Monthly Fees Paid vs. Attrition Outcome",
        labels={"MonthlyCharges": "Monthly Ticket Value ($)", "Churn": "Account Status"},
        color_discrete_map={"No": "#10B981", "Yes": "#EF4444"},
        notched=True
    )
    st.plotly_chart(fig_box, use_container_width=True)
    
    # Bubble Scatter Plot: LTV Dynamics
    st.markdown("High-Value Account Exposure Matrix")
    fig_scatter = px.scatter(
        filtered_df, x="tenure", y="TotalCharges", color="Churn", size="MonthlyCharges",
        hover_data=['customerID'], opacity=0.6,
        title="Realized Revenue Architecture (Bubble Scale = Monthly Contract Base)",
        labels={"tenure": "Account Age (Months)", "TotalCharges": "Cumulative Capital Extracted ($)"},
        color_discrete_map={"No": "#3B82F6", "Yes": "#EF4444"}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: AUTOMATED ADVISORY PLAYBOOK
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("Executive Action Playbook")
    st.markdown("Based on the data profile of your customer database, your customer-success teams should execute these playbooks immediately:")
    
    # Calculate conditional dynamic vectors for the playbook recommendations
    m2m_churn = df[df['Contract'] == 'Month-to-month']['Churn_Numeric'].mean() * 100
    fiber_churn = df[df['InternetService'] == 'Fiber optic']['Churn_Numeric'].mean() * 100
    nosec_churn = df[df['OnlineSecurity'] == 'No']['Churn_Numeric'].mean() * 100
    
    st.markdown(f"""
    Priority 1: Month-to-Month Contract Conversion Campaign
    *The Diagnostic: Month-to-month contracts exhibit an intense systemic churn footprint of {m2m_churn:.1f}%.
    *The Mandate: Run targeted campaigns offering small discounts (e.g., 10% off for 12 months) to move month-to-month users onto annual agreements. Locking in structural commitment reduces tactical churn risks.
    
    Priority 2: Infrastructure Diagnostics & Product Health Review
    *The Diagnostic: Fiber Optic customers show unexpectedly high attrition rates ({fiber_churn:.1f}%). This usually points to service friction, configuration issues, or competitive pricing attacks.
    *The Mandate:Launch proactive customer engineering outreach and performance audits for Fiber Optic accounts to address potential experience drops.
    
    Priority 3: Value Add-On Expansion (De-Risking Accounts)
    *The Diagnostic: Accounts missing core features like Online Security Add-ons display high churn signatures ({nosec_churn:.1f}%).
    *The Mandate: Package core security features directly into the core tier instead of selling them as standalone add-ons. Increasing product adoption and integration hardens sticky user retention loops.
    """)
    
    st.markdown("---")
    st.subheader("Raw Exception List: Operational High-Risk Pipeline")
    st.markdown("This view isolates accounts on short-term contracts with high bills who have not set up automatic payments. This is an optimal tactical save-list for customer service operations.")
    
    # Generate an operations actionable pipeline
    save_pipeline = filtered_df[
        (filtered_df['Contract'] == 'Month-to-month') & 
        (filtered_df['Churn'] == 'No') & 
        (filtered_df['MonthlyCharges'] > 75) &
        (filtered_df['PaymentMethod'].str.contains('check|Mailed', case=False, na=False))
    ][['customerID', 'Contract', 'InternetService', 'MonthlyCharges', 'tenure', 'PaymentMethod']]
    
    st.dataframe(save_pipeline, use_container_width=True)
    st.caption(f"Showing {len(save_pipeline)} active high-risk pipeline accounts matching strategic critical threat profile indicators.")

st.markdown("---")
csv=filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(" Download Filtered Dataset",csv,"filtered_customers.csv","text/csv")
st.caption("Customer Churn Intelligence Dashboard | Built with Streamlit & Plotly")
