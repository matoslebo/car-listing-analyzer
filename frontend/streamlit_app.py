
import os
import pandas as pd
import requests
import streamlit as st


# Backend URL — different for local vs Docker
# In Docker compose, services talk via service name on internal network
API_URL = os.getenv("API_URL", "http://localhost:8000")


def main():
    st.title("🚗 Car Listing Analyzer")
    st.write("AI-powered analysis of used car listings")
    
    # Form for car input
    st.subheader("Enter car details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        make = st.text_input("Make", value="BMW")
        model = st.text_input("Model", value="320d")
        year = st.number_input("Year", min_value=1900, max_value=2026, value=2018)
    
    with col2:
        km = st.number_input("Kilometers", min_value=0, value=150000, step=1000)
        price = st.number_input("Price (EUR)", min_value=0, value=12000, step=100)
    
    # Submit button
    if st.button("Analyze", type="primary"):
        with st.spinner("Analyzing..."):
            # Call API
            response = requests.post(
                f"{API_URL}/listings/analyze",
                json={
                    "make": make,
                    "model": model,
                    "year": int(year),
                    "km": int(km),
                    "price": int(price),
                },
            )
            
            if response.status_code == 200:

                data = response.json()

                # 1. Deal quality badge
                quality = data["deal_quality"]
                if quality in ["excellent", "good"]:
                    st.success(f"Deal Quality: {quality.upper()}")
                elif quality == "fair":
                    st.info(f"Deal Quality: {quality.upper()}")
                else:  # poor, overpriced
                    st.warning(f"Deal Quality: {quality.upper()}")

                # 2. Pricing metrics in 3 columns
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Fair Price", f"{data['fair_price']:,} EUR")
                with col2:
                    st.metric("Min (10th %)", f"{data['fair_price_min']:,} EUR")
                with col3:
                    st.metric("Max (90th %)", f"{data['fair_price_max']:,} EUR")

                st.divider()

                # 3. LLM recommendation
                llm = data["llm_recommendation"]
                st.subheader(f"AI Recommendation: {llm['recommendation'].upper().replace('_', ' ')}")
                st.markdown(llm["summary"])

                # Positives + Concerns in 2 columns
                col_pos, col_con = st.columns(2)
                with col_pos:
                    st.markdown("**✓ Positives**")
                    for p in llm["key_positives"]:
                        st.markdown(f"- {p}")
                with col_con:
                    st.markdown("**⚠ Concerns**")
                    for c in llm["key_concerns"]:
                        st.markdown(f"- {c}")

                st.divider()

                # 4. Risks
                if data["risks"]:
                    st.subheader(f"⚠ Risks ({len(data['risks'])})")
                    for risk in data["risks"]:
                        severity = risk["severity"].upper()
                        st.markdown(f"**[{severity}]** {risk['type']}: {risk['message']}")
                else:
                    st.success("No risks detected")

                st.divider()

                # 5. Similar listings table
                st.subheader("Similar listings")
                similar_df = pd.DataFrame(data["similar_listings"])
                # Round similarity for display
                similar_df["similarity_score"] = similar_df["similarity_score"].round(2)
                st.dataframe(similar_df, width="stretch")



if __name__ == "__main__":
    main()