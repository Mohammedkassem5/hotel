import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv("hotels.csv")
    df = df.drop(columns=["name", "email", "phone-number", "credit_card"], errors="ignore")
    df.fillna({'children': 0, 'country': 'Unknown'}, inplace=True)
    return df

df = load_data()

st.set_page_config(page_title="Hotel Analytics Dashboard", layout="wide")

st.markdown("<h1 style='text-align:center;'>🏨 Hotel Booking Analytics Dashboard</h1>", unsafe_allow_html=True)

years = ["All"] + sorted(df["arrival_date_year"].unique().tolist())
hotels = ["All"] + sorted(df["hotel"].unique().tolist())
countries = ["All"] + sorted(df["country"].unique().tolist())
customers = ["All"] + sorted(df["customer_type"].unique().tolist())

with st.sidebar:
    st.header("Filters")
    year = st.selectbox("Year", years)
    hotel_type = st.selectbox("Hotel Type", hotels)
    country = st.selectbox("Country", countries)
    customer_type = st.selectbox("Customer Type", customers)

df_filtered = df.copy()
if year != "All":
    df_filtered = df_filtered[df_filtered["arrival_date_year"] == year]
if hotel_type != "All":
    df_filtered = df_filtered[df_filtered["hotel"] == hotel_type]
if country != "All":
    df_filtered = df_filtered[df_filtered["country"] == country]
if customer_type != "All":
    df_filtered = df_filtered[df_filtered["customer_type"] == customer_type]

total_bookings = len(df_filtered)
canceled = df_filtered["is_canceled"].sum()
cancellation_rate = round((canceled / total_bookings) * 100, 2) if total_bookings > 0 else 0
adr = round(df_filtered["adr"].mean(), 2)
repeated_guests = df_filtered["is_repeated_guest"].sum()
lead_time = round(df_filtered["lead_time"].mean(), 1)

tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Charts", "🌍 Map", "📄 Data"])

with tab1:
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Bookings", total_bookings)
    k2.metric("Cancellation Rate", f"{cancellation_rate}%")
    k3.metric("Average ADR", f"${adr}")
    k4.metric("Repeated Guests", repeated_guests)
    k5.metric("Avg Lead Time", f"{lead_time} days")

    st.markdown("### Quick Insights")
    if cancellation_rate > 30:
        st.warning("⚠️ High cancellation rate observed.")
    if adr > 150:
        st.info("💡 High ADR indicates premium pricing strategy.")
    if repeated_guests > 50:
        st.success("🎉 Good customer loyalty observed.")

with tab2:
    fig1 = px.pie(df_filtered, names="hotel", title="Bookings Distribution by Hotel Type",
                  hole=0.4)
    fig1.update_traces(textposition="inside", textinfo="percent+label")

    monthly_cancel = df_filtered.groupby("arrival_date_month")["is_canceled"].mean().reset_index()
    fig2 = px.line(monthly_cancel, x="arrival_date_month", y="is_canceled",
                   title="Monthly Cancellation Trend", markers=True)
    fig2.update_yaxes(title="Cancellation Rate")

    top_countries = df_filtered["country"].value_counts().nlargest(10).reset_index()
    top_countries.columns = ["country", "bookings"]
    fig3 = px.bar(top_countries, x="bookings", y="country", orientation="h",
                  title="Top 10 Countries by Bookings", text="bookings")
    fig3.update_traces(texttemplate='%{text}', textposition='outside')

    fig4 = px.box(df_filtered, x="hotel", y="adr", color="hotel", title="ADR Distribution by Hotel Type")

    c1, c2 = st.columns(2)
    c1.plotly_chart(fig1, use_container_width=True)
    c2.plotly_chart(fig2, use_container_width=True)
    c1.plotly_chart(fig3, use_container_width=True)
    c2.plotly_chart(fig4, use_container_width=True)

with tab3:
    country_geo = df_filtered["country"].value_counts().reset_index()
    country_geo.columns = ["country", "bookings"]
    fig5 = px.choropleth(country_geo, locations="country", locationmode="country names", color="bookings",
                         title="Bookings Geographical Distribution", color_continuous_scale="Blues")
    st.plotly_chart(fig5, use_container_width=True)

with tab4:
    st.dataframe(df_filtered.head(100))
