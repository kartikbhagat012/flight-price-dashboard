import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Indian Flight Fare Dashboard", 
    page_icon="✈️", 
    layout="wide"
)

@st.cache_data
def load_flight_data():
    df = pd.read_csv("Clean_Dataset.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    return df

with st.spinner("Loading 3 Lakh+ Flight Records... Please wait! 🚀"):
    df = load_flight_data()

st.title("✈️ Indian Flight Analytics & Fare Dashboard")
st.caption("Analyze pricing trends, search flight deals, and explore statistics from Indian domestic flights.")

st.sidebar.header("🎯 Trip Planner Filters")

source_cities = sorted(df["source_city"].unique())
destination_cities = sorted(df["destination_city"].unique())

source_city = st.sidebar.selectbox("Source City", source_cities, index=source_cities.index("Delhi"))
destination_city = st.sidebar.selectbox("Destination City", destination_cities, index=destination_cities.index("Mumbai"))

if source_city == destination_city:
    st.sidebar.error("⚠️ Source and Destination cannot be the same! Please change your cities.")
    st.warning("Please select different Source and Destination cities in the sidebar to load the analytics.")
    st.stop()

all_airlines = sorted(df["airline"].unique())
selected_airlines = st.sidebar.multiselect("Select Airlines", all_airlines, default=all_airlines)

classes = sorted(df["class"].unique())
selected_classes = st.sidebar.multiselect("Travel Class", classes, default=classes)

stops_options = sorted(df["stops"].unique())
selected_stops = st.sidebar.multiselect("Stops", stops_options, default=stops_options)

min_days, max_days = int(df["days_left"].min()), int(df["days_left"].max())
days_left_range = st.sidebar.slider(
    "Days Left to Departure (Booking Window)", 
    min_days, max_days, (min_days, max_days)
)

filtered_df = df[
    (df["source_city"] == source_city) &
    (df["destination_city"] == destination_city) &
    (df["airline"].isin(selected_airlines)) &
    (df["class"].isin(selected_classes)) &
    (df["stops"].isin(selected_stops)) &
    (df["days_left"].between(days_left_range[0], days_left_range[1]))
]

if filtered_df.empty:
    st.error("❌ No flights found matching your selected filters. Try broadening your selection!")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
with c1:
    avg_price = filtered_df["price"].mean()
    st.metric("Average Ticket Price", f"₹{avg_price:,.2f}", border=True)
with c2:
    cheapest_price = filtered_df["price"].min()
    st.metric("Starting From (Cheapest)", f"₹{cheapest_price:,.2f}", border=True)
with c3:
    total_flights = len(filtered_df)
    st.metric("Available Options", f"{total_flights:,} Flights", border=True)
with c4:
    avg_duration = filtered_df["duration"].mean()
    st.metric("Avg Flight Duration", f"{avg_duration:.1f} Hours", border=True)

st.divider()

tab1, tab2, tab3 = st.tabs(["🔍 Flight Deals Search", "📈 Pricing Insights & Trends", "🔮 Smart Fare Estimator"])

with tab1:
    st.subheader("💡 Deals for Your Selected Route")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cheapest_flight = filtered_df.loc[filtered_df["price"].idxmin()]
        st.info("💰 **Cheapest Flight Option Available**")
        st.markdown(f"""
        *   **Airline:** {cheapest_flight['airline']} ({cheapest_flight['flight']})
        *   **Fare:** **₹{cheapest_flight['price']:,}**
        *   **Duration:** {cheapest_flight['duration']} Hours | Stops: {cheapest_flight['stops']}
        *   **Departure/Arrival:** {cheapest_flight['departure_time']} ➡️ {cheapest_flight['arrival_time']}
        """)
        
    with col2:
        fastest_flight = filtered_df.loc[filtered_df["duration"].idxmin()]
        st.success("⚡ **Fastest Flight Option Available**")
        st.markdown(f"""
        *   **Airline:** {fastest_flight['airline']} ({fastest_flight['flight']})
        *   **Fare:** **₹{fastest_flight['price']:,}**
        *   **Duration:** {fastest_flight['duration']} Hours | Stops: {fastest_flight['stops']}
        *   **Departure/Arrival:** {fastest_flight['departure_time']} ➡️ {fastest_flight['arrival_time']}
        """)
        
    st.subheader("📅 Price Trend by Booking Window (Days Left)")
    st.write("Does booking early save money? Find out below:")
    
    days_price = filtered_df.groupby("days_left", as_index=False)["price"].mean()
    fig_days = px.line(
        days_price, 
        x="days_left", 
        y="price", 
        title="Average Ticket Price vs. Days Left to Departure",
        labels={"days_left": "Days Left Before Departure", "price": "Average Fare (₹)"},
        markers=True
    )
    fig_days.update_traces(line_color='#2ca02c', marker=dict(size=6))
    st.plotly_chart(fig_days, use_container_width=True)

with tab2:
    st.subheader("📊 Deeper Analytics on Flight Rates")
    
    col_new1, col_new2 = st.columns(2)
    
    with col_new1:
        airline_avg_price = filtered_df.groupby("airline", as_index=False)["price"].mean().sort_values("price")
        fig_selected_avg = px.bar(
            airline_avg_price,
            x="airline",
            y="price",
            color="airline",
            title="Average Price of Your Selected Airlines",
            labels={"airline": "Airline", "price": "Average Fare (₹)"},
            text_auto=".2s"
        )
        st.plotly_chart(fig_selected_avg, use_container_width=True)
        
    with col_new2:
        class_extremes = filtered_df.groupby("class")["price"].agg(["min", "max"]).reset_index()
        class_extremes_melted = class_extremes.melt(id_vars="class", value_vars=["min", "max"], var_name="Price_Type", value_name="Fare")
        fig_extremes = px.bar(
            class_extremes_melted,
            x="class",
            y="Fare",
            color="Price_Type",
            barmode="group",
            title="Cheapest vs Expensive Price by Travel Class",
            labels={"class": "Travel Class", "Fare": "Ticket Price (₹)", "Price_Type": "Range Type"},
            color_discrete_map={"min": "#2ca02c", "max": "#d62728"},
            text_auto=".2s"
        )
        st.plotly_chart(fig_extremes, use_container_width=True)

    st.divider()
    
    st.subheader("🛩️ Specific Flight Codes Analytics")
    col_input1, col_input2 = st.columns([1, 3])
    with col_input1:
        sort_order = st.radio("Rank Flights By Price:", ["Cheapest Flights", "Most Expensive Flights"])
        top_n = st.slider("Number of Flights to Display:", min_value=5, max_value=25, value=10)
        
    with col_input2:
        # Har specific flight code ka average price nikal rahe hain
        specific_flight_fare = filtered_df.groupby(["flight", "airline"], as_index=False)["price"].mean()
        
        # Sasti ya mehangi ke hisab se sort karke data slice kar rahe hain
        if sort_order == "Cheapest Flights":
            specific_flight_fare = specific_flight_fare.sort_values("price", ascending=True).head(top_n)
            title_text = f"Top {top_n} Cheapest Specific Flights (By Code)"
        else:
            specific_flight_fare = specific_flight_fare.sort_values("price", ascending=False).head(top_n)
            title_text = f"Top {top_n} Most Expensive Specific Flights (By Code)"
            
        # Plotly Express Bar Chart Fix
        fig_specific_flights = px.bar(
            specific_flight_fare,
            x="flight",       # X-axis par string values (flight codes) explicitly jayengi
            y="price",
            color="airline",
            barmode="group",  # Bars ko alag-alag rakhne ke liye barmode fix kiya
            title=title_text,
            labels={"flight": "Flight Code", "price": "Average Fare (₹)", "airline": "Airline"},
            text_auto=".2s"
        )
        
        # X-axis par flight codes saaf dikhein, isliye unhe rotate karne ka tweak
        fig_specific_flights.update_layout(xaxis={"type": "category"})
        fig_specific_flights.update_xaxes(tickangle=45)
        
        st.plotly_chart(fig_specific_flights, use_container_width=True)

    st.divider()

    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        airline_fare = filtered_df.groupby(["airline", "class"], as_index=False)["price"].mean()
        fig_airline = px.bar(
            airline_fare, 
            x="airline", 
            y="price", 
            color="class",
            barmode="group",
            title="Average Price Split by Airline & Travel Class",
            labels={"price": "Average Fare (₹)", "airline": "Airline", "class": "Class"},
            text_auto=".2s"
        )
        st.plotly_chart(fig_airline, use_container_width=True)
        
    with col_chart2:
        fig_box = px.box(
            filtered_df, 
            x="airline", 
            y="price", 
            color="airline",
            title="Price Spread / Distribution across Airlines",
            labels={"price": "Fare (₹)", "airline": "Airline"}
        )
        st.plotly_chart(fig_box, use_container_width=True)

    st.divider()
    
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        time_fare = filtered_df.groupby("departure_time", as_index=False)["price"].mean().sort_values("price")
        fig_time = px.bar(
            time_fare, 
            x="departure_time", 
            y="price",
            title="Average Fare based on Departure Time",
            labels={"departure_time": "Departure Slot", "price": "Average Fare (₹)"},
            color_discrete_sequence=['#ff7f0e']
        )
        st.plotly_chart(fig_time, use_container_width=True)
        
    with col_chart4:
        fig_scatter = px.scatter(
            filtered_df, 
            x="duration", 
            y="price", 
            color="airline", 
            opacity=0.6,
            title="Is longer flight duration cheaper? (Duration vs Price)",
            labels={"duration": "Duration (Hours)", "price": "Fare (₹)"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.subheader("🔮 Smart Fare Predictor (Interactive Simulation)")
    st.write("Input custom parameters to get a real-time smart fare estimate based on matching historical data.")
    
    p_col1, p_col2, p_col3 = st.columns(3)
    
    with p_col1:
        est_airline = st.selectbox("Select Target Airline", df["airline"].unique())
        est_class = st.radio("Select Target Class", df["class"].unique(), horizontal=True)
        
    with p_col2:
        est_stops = st.radio("Number of Stops", df["stops"].unique(), horizontal=True)
        est_dep_time = st.selectbox("Departure Time Block", df["departure_time"].unique())
        
    with p_col3:
        est_days = st.number_input("Days Left Before Booking", min_value=1, max_value=49, value=15)
        
    if st.button("Estimate Ticket Price 💸", type="primary", use_container_width=True):
        matched_data = df[
            (df["source_city"] == source_city) &
            (df["destination_city"] == destination_city) &
            (df["airline"] == est_airline) &
            (df["class"] == est_class) &
            (df["stops"] == est_stops) &
            (df["days_left"].between(max(1, est_days - 3), min(49, est_days + 3)))
        ]
        
        if not matched_data.empty:
            predicted_price = matched_data["price"].mean()
            st.success(f"### 💰 Estimated Fare: **₹{predicted_price:,.2f}**")
            st.info(f"💡 *Note: This estimate is averaged over {len(matched_data)} matching actual records in our dataset for the given route/date range.*")
        else:
            base_price = df[(df["source_city"] == source_city) & (df["destination_city"] == destination_city) & (df["class"] == est_class)]["price"].mean()
            if pd.isna(base_price):
                base_price = 5000 if est_class == "Economy" else 25000
                
            multiplier = 1.0
            if est_stops == "one": multiplier *= 1.2
            elif est_stops == "two_or_more": multiplier *= 1.4
            if est_days < 10: multiplier *= 1.5
            
            final_est = base_price * multiplier
            st.warning(f"### 💸 Rough Estimated Fare: **₹{final_est:,.2f}**")
            st.caption("*(Showing generalized estimate because an exact combination was not found for this specific date range/airline)*")