import mysql.connector
import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
# Connect to MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="MySQL@0406",
    database="local_food_wastage"
)
cursor = conn.cursor(dictionary=True)

# Page setup
st.set_page_config(page_title="Food Management System", layout="wide")

# Gradient header
st.markdown("""
    <div style="background: linear-gradient(to right, #00c6ff, #0072ff); padding: 1.5rem; border-radius: 12px; text-align: center; margin-bottom: 50px;">
        <h2 style="color: white;">🍽️ <b>Food Management System Dashboard</b></h2>
    </div>
""", unsafe_allow_html=True)

# Fetch counts from database
cursor.execute("SELECT COUNT(*) AS total FROM providers_data_cleaned")
total_providers = cursor.fetchone()["total"]

cursor.execute("SELECT COUNT(*) AS total FROM receivers_data_cleaned")
total_receivers = cursor.fetchone()["total"]

cursor.execute("SELECT COUNT(*) AS total FROM food_listings_data_cleaned")
total_listings = cursor.fetchone()["total"]

cursor.execute("SELECT COUNT(*) AS total FROM claims_data_cleaned")
total_claims = cursor.fetchone()["total"]

# Bubble-style metric card template with better contrast
bubble_template = """
    <div style="
        background: radial-gradient(circle at top left, #c471f5, #f64f59);
        width: 190px;
        height: 190px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
        margin: auto;
    ">
        <h4 style="color: #ffffff; margin: 0; font-weight: 600; font-size: 20px;">{}</h4>
        <h2 style="color: #ffffff; margin: 0; font-size: 34px;">{}</h2>
    </div>
"""

# Layout with spacing
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    st.markdown(bubble_template.format("Total Providers", total_providers), unsafe_allow_html=True)

with col2:
    st.markdown(bubble_template.format("Total Receivers", total_receivers), unsafe_allow_html=True)

with col3:
    st.markdown(bubble_template.format("Food Listings", total_listings), unsafe_allow_html=True)

with col4:
    st.markdown(bubble_template.format("Total Claims", total_claims), unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("👋😊 Welcome!")
section = st.sidebar.radio("Choose a section:", ["CRUD Operations", "SQL Queries", "Data Visualizations", "Data Explorer"])

# CRUD Operations Section
if section == "CRUD Operations":
    st.title("🛠️ Manage Food Listings")

    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add", "❌ Delete", "🔄 Update", "👁️ View"])

    # ---------------- ADD TAB ----------------
    with tab1:
        st.subheader("Add New Food Listing")
        with st.form("Add Food Listing"):
            food_name = st.text_input("Food Name")
            quantity = st.number_input("Quantity", min_value=1)
            expiry = st.date_input("Expiry Date", value=date.today())
            provider_id = st.number_input("Provider ID", min_value=1, step=1)
            location = st.text_input("Location")
            food_type = st.text_input("Food Type")
            meal_type = st.text_input("Meal Type")
            submitted = st.form_submit_button("Add")

            if submitted:
                cursor.execute("""
                    INSERT INTO food_listings_data_cleaned
                    (Food_Name, Quantity, Expiry_Date, Provider_ID, Location, Food_Type, Meal_Type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    food_name,
                    quantity,
                    expiry.strftime("%Y-%m-%d"),
                    int(provider_id),
                    location,
                    food_type,
                    meal_type
                ))
                conn.commit()
                st.success("✅ Food listing added successfully!")

    # ---------------- DELETE TAB ----------------
    with tab2:
        st.subheader("Delete Food Listing")

        def get_food_items():
            cursor.execute("SELECT Food_ID, Food_Name FROM food_listings_data_cleaned")
            return cursor.fetchall()

        food_items = get_food_items()

        if food_items:
            # ✅ Filter out items with None or NULL Food_ID
            valid_food_items = [item for item in food_items if item['Food_ID'] is not None]

            if valid_food_items:
                # ✅ Build dropdown map only from valid items
                food_map = {f"{item['Food_ID']} - {item['Food_Name']}": item['Food_ID'] for item in valid_food_items}
                selected_food = st.selectbox("Select Food to Delete", list(food_map.keys()))

                if st.button("Delete"):
                    cursor.execute("DELETE FROM food_listings_data_cleaned WHERE Food_ID = %s", (food_map[selected_food],))
                    conn.commit()
                    st.success("✅ Food listing deleted.")
                    st.rerun()
            else:
                st.info("No valid food listings available to delete.")
        else:
            st.info("No food listings available to delete.")

    # Update Tab
    with tab3:
        st.subheader("Update Food Listing")
        cursor.execute("SELECT * FROM food_listings_data_cleaned")
        food_items = cursor.fetchall()

        if food_items:
            food_map = {f"{item['Food_ID']} - {item['Food_Name']}": item for item in food_items}
            selected_food = st.selectbox("Select Food to Update", list(food_map.keys()))
            food = food_map[selected_food]

            try:
                expiry_date = (
                    food['Expiry_Date']
                    if isinstance(food['Expiry_Date'], date)
                    else datetime.strptime(str(food['Expiry_Date']), "%Y-%m-%d").date()
                )
            except Exception:
                expiry_date = date.today()

            with st.form("Update Food Listing"):
                new_name = st.text_input("Food Name", value=food['Food_Name'])
                new_quantity = st.number_input("Quantity", min_value=1, value=food['Quantity'])
                new_expiry = st.date_input("Expiry Date", value=expiry_date)
                new_provider_id = st.number_input("Provider ID", min_value=1, value=food['Provider_ID'])
                new_location = st.text_input("Location", value=food['Location'])
                new_food_type = st.text_input("Food Type", value=food['Food_Type'])
                new_meal_type = st.text_input("Meal Type", value=food['Meal_Type'])
                update_submit = st.form_submit_button("Update")

                if update_submit:
                    cursor.execute("""
                        UPDATE food_listings_data_cleaned
                        SET Food_Name = %s, Quantity = %s, Expiry_Date = %s,
                            Provider_ID = %s, Location = %s, Food_Type = %s, Meal_Type = %s
                        WHERE Food_ID = %s
                    """, (
                        new_name, new_quantity, new_expiry.strftime("%Y-%m-%d"),
                        int(new_provider_id), new_location,
                        new_food_type, new_meal_type,
                        food['Food_ID']
                    ))
                    conn.commit()
                    st.success("✅ Food listing updated.")
        else:
            st.info("No food listings available to update.")

    # View Tab
    with tab4:
        st.subheader("View All Food Listings")

        def fetch_all_food():
            cursor.execute("SELECT * FROM food_listings_data_cleaned")
            return cursor.fetchall()

        all_food = fetch_all_food()
        if all_food:
            st.dataframe(all_food)
        else:
            st.warning("No food listings found.")

# Queries
if section == "SQL Queries":
    st.markdown("## 🧮 SQL Query Interface")

    # 📚 All 15 Queries
    predefined_queries = {
        "1️⃣ Providers & Receivers by City": """
            SELECT City, 
                   COUNT(DISTINCT Provider_ID) AS Total_Providers,
                   COUNT(DISTINCT Receiver_ID) AS Total_Receivers
            FROM (
                SELECT City, Provider_ID, NULL AS Receiver_ID FROM providers_data_cleaned
                UNION ALL
                SELECT City, NULL, Receiver_ID FROM receivers_data_cleaned
            ) combined
            GROUP BY City;
        """,
        "2️⃣ Top Provider Type by Quantity": """
            SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
            FROM food_listings_data_cleaned
            GROUP BY Provider_Type
            ORDER BY Total_Quantity DESC
            LIMIT 1;
        """,
        "3️⃣ Provider Contacts in 'New Jessica'": """
            SELECT Name, Type, Address, Contact
            FROM providers_data_cleaned
            WHERE City = 'New Jessica';
        """,
        "4️⃣ Top 5 Receivers by Claims": """
            SELECT r.Name, r.City, COUNT(c.Claim_ID) AS Total_Claims
            FROM claims_data_cleaned c
            JOIN receivers_data_cleaned r ON c.Receiver_ID = r.Receiver_ID
            GROUP BY r.Name, r.City
            ORDER BY Total_Claims DESC
            LIMIT 5;
        """,
        "5️⃣ Total Food Quantity Available": """
            SELECT SUM(Quantity) AS Total_Food_Quantity
            FROM food_listings_data_cleaned;
        """,
        "6️⃣ Top Cities by Listings": """
            SELECT p.City, COUNT(f.Food_ID) AS Total_Listings
            FROM food_listings_data_cleaned f
            JOIN providers_data_cleaned p ON f.Provider_ID = p.Provider_ID
            GROUP BY p.City
            ORDER BY Total_Listings DESC
            LIMIT 5;
        """,
        "7️⃣ Most Common Food Types": """
            SELECT Food_Type, COUNT(Food_ID) AS Count_Food
            FROM food_listings_data_cleaned
            GROUP BY Food_Type
            ORDER BY Count_Food DESC;
        """,
        "8️⃣ Claims per Food Item": """
            SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
            FROM claims_data_cleaned c
            JOIN food_listings_data_cleaned f ON c.Food_ID = f.Food_ID
            GROUP BY f.Food_Name
            ORDER BY Total_Claims DESC;
        """,
        "9️⃣ Top Providers by Successful Claims": """
            SELECT p.Name, COUNT(c.Claim_ID) AS Successful_Claims
            FROM claims_data_cleaned c
            JOIN food_listings_data_cleaned f ON c.Food_ID = f.Food_ID
            JOIN providers_data_cleaned p ON f.Provider_ID = p.Provider_ID
            WHERE c.Status = 'Completed'
            GROUP BY p.Name
            ORDER BY Successful_Claims DESC
            LIMIT 2;
        """,
        "🔟 Claim Status Percentages": """
            SELECT Status,
                   COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims_data_cleaned) AS Percentage
            FROM claims_data_cleaned
            GROUP BY Status;
        """,
        "1️⃣1️⃣ Avg Quantity Claimed per Receiver": """
            SELECT r.Name, AVG(f.Quantity) AS Avg_Quantity_Claimed
            FROM claims_data_cleaned c
            JOIN receivers_data_cleaned r ON c.Receiver_ID = r.Receiver_ID
            JOIN food_listings_data_cleaned f ON c.Food_ID = f.Food_ID
            GROUP BY r.Name
            ORDER BY Avg_Quantity_Claimed DESC;
        """,
        "1️⃣2️⃣ Most Claimed Meal Type": """
            SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
            FROM claims_data_cleaned c
            JOIN food_listings_data_cleaned f ON c.Food_ID = f.Food_ID
            GROUP BY f.Meal_Type
            ORDER BY Total_Claims DESC;
        """,
        "1️⃣3️⃣ Total Quantity Donated per Provider": """
            SELECT p.Name, SUM(f.Quantity) AS Total_Donated
            FROM food_listings_data_cleaned f
            JOIN providers_data_cleaned p ON f.Provider_ID = p.Provider_ID
            GROUP BY p.Name
            ORDER BY Total_Donated DESC;
        """,
        "1️⃣4️⃣ Total Quantity Donated per Provider": """
            SELECT Food_Name, SUM(Quantity) AS Total_Quantity
            FROM food_listings_data_cleaned
            GROUP BY Food_Name
            ORDER BY Total_Quantity DESC
            LIMIT 10;
        """,
        "1️⃣5️⃣ Expiring Soon (Within 30 Days)": """
            SELECT Food_Name, Quantity, Expiry_Date, Location
            FROM food_listings_data_cleaned
            WHERE Expiry_Date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
            ORDER BY Expiry_Date ASC;
        """
    }

    # 📌 Layout
    col1, col2 = st.columns(2)

    # 🧠 Predefined Query Selector
    with col1:
        selected_query_name = st.selectbox("Select a predefined query:", list(predefined_queries.keys()))
        if st.button("Run Selected Query"):
            query = predefined_queries[selected_query_name]
            try:
                cursor.execute(query)
                result = cursor.fetchall()
                st.success(f"✅ Query executed: {selected_query_name}")
                st.dataframe(result)
            except Exception as e:
                st.error(f"❌ Error: {e}")

    # 📝 Custom Query Input
    with col2:
        custom_query = st.text_area("Enter your custom SQL query:", height=180)
        if st.button("Run Custom Query"):
            try:
                cursor.execute(custom_query)
                result = cursor.fetchall()
                st.success("✅ Custom query executed successfully!")
                st.dataframe(result)
            except Exception as e:
                st.error(f"❌ Error: {e}")
            
# Data Visualizations
if section == "Data Visualizations":
    st.header("📊 Data Visualization Dashboard")

    chart_options = [
        "📦 Food Listings by Type",
        "🧮 Quantity Distribution",
        "🔝 Top 10 Quantity by Location",
        "🔝 Top 10 Receivers by Claims",
        "🍩 Top 10 Food by Quantity"
    ]

    selected_chart = st.selectbox("Choose a chart to display:", chart_options)
    show_chart = st.button("Show Chart")

    if show_chart:
        if selected_chart == "📦 Food Listings by Type":
            # Chart 1 code here
            cursor.execute("SELECT Food_Type, Meal_Type, COUNT(*) AS Count FROM food_listings_data_cleaned GROUP BY Food_Type, Meal_Type")
            data = cursor.fetchall()
            df = pd.DataFrame(data)

            fig = px.bar(df, x="Food_Type", y="Count", color="Meal_Type", barmode="group",
             title="Food Listings by Type and Meal",
             labels={"Food_Type": "Food Type", "Count": "Number of Listings"})
            st.plotly_chart(fig, use_container_width=True)

        elif selected_chart == "🧮 Quantity Distribution":
            # Chart 4 code here
            cursor.execute("SELECT Quantity, Food_Type FROM food_listings_data_cleaned WHERE Food_ID IS NOT NULL")
            data = cursor.fetchall()
            df = pd.DataFrame(data)

            fig = px.box(df, x="Food_Type", y="Quantity", title="Quantity Distribution by Food Type",
             labels={"Food_Type": "Food Type", "Quantity": "Quantity"})
            st.plotly_chart(fig, use_container_width=True)

        elif selected_chart == "🔝 Top 10 Quantity by Location":
            # Chart 5 code here
            cursor.execute("SELECT Location, SUM(Quantity) AS Total_Quantity FROM food_listings_data_cleaned GROUP BY Location ORDER BY Total_Quantity DESC LIMIT 10")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=["Location", "Total_Quantity"])

            fig = px.bar(df, x="Location", y="Total_Quantity", title="🔝 Top 10 Quantity by Location", color="Total_Quantity", color_continuous_scale="viridis")
            st.plotly_chart(fig, use_container_width=True)

        elif selected_chart == "🔝 Top 10 Receivers by Claims":
            # Chart 7 code here
            cursor.execute("SELECT Receiver_ID, COUNT(*) AS Claims FROM claims_data_cleaned GROUP BY Receiver_ID ORDER BY Claims DESC LIMIT 10")
            data = cursor.fetchall()
            df = pd.DataFrame(data)

            fig = px.bar(df, x="Receiver_ID", y="Claims", title="Top 10 Receivers by Claims")
            st.plotly_chart(fig, use_container_width=True)

        elif selected_chart == "🍩 Top 10 Food by Quantity":
            # Chart 11 code here
            cursor.execute("SELECT Food_Name, SUM(Quantity) AS Total_Quantity FROM food_listings_data_cleaned GROUP BY Food_Name ORDER BY Total_Quantity DESC LIMIT 10")
            data = cursor.fetchall()
            df = pd.DataFrame(data)

            fig = px.pie(df, names="Food_Name", values="Total_Quantity", hole=0.4, title="Top 10 Food by Quantity")
            st.plotly_chart(fig, use_container_width=True)

# Data Explorer
if section == "Data Explorer":
    st.markdown("## 🔍 Data Explorer")

    # Dropdown to choose table
    table_choice = st.selectbox("Select a dataset to explore:", [
        "Providers",
        "Receivers",
        "Claims",
        "Food Listings"
    ])

    # Fetch and display data
    if table_choice == "Providers":
        cursor.execute("SELECT * FROM providers_data_cleaned")
        data = cursor.fetchall()
        st.dataframe(data)

    elif table_choice == "Receivers":
        cursor.execute("SELECT * FROM receivers_data_cleaned")
        data = cursor.fetchall()
        st.dataframe(data)

    elif table_choice == "Claims":
        cursor.execute("SELECT * FROM claims_data_cleaned")
        data = cursor.fetchall()
        st.dataframe(data)

    elif table_choice == "Food Listings":
        cursor.execute("SELECT * FROM food_listings_data_cleaned")
        data = cursor.fetchall()
        st.dataframe(data)
