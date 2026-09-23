import pandas as pd

silver_dir="data/silver"

erp_df=pd.read_csv(f"{silver_dir}/erp_silver.csv")
wms_df=pd.read_csv(f"{silver_dir}/wms_silver.csv")



erp_df["order_date"]=pd.to_datetime(erp_df["order_date"])
erp_df["promised_delivery_date"]=pd.to_datetime(erp_df["promised_delivery_date"])

wms_df["timestamp"]=pd.to_datetime(wms_df["timestamp"])

print("ERP rows:", len(erp_df))
print("WMS rows:", len(wms_df))



wms_outbound=wms_df[wms_df["movement_type"]=="OUTBOUND"].copy()

# .merge() joins two tables together, like a VLOOKUP in Excel, matching
# rows where order_id is the same in both. how="left" means: keep every
# ERP order, even ones that haven't shipped yet (no WMS match).

otif_df = erp_df.merge(
    wms_outbound[["order_id", "quantity", "timestamp"]],
    on="order_id",
    how="left",
    suffixes=("_ordered", "_shipped")
)

print(otif_df[["order_id", "quantity_ordered", "quantity", "promised_delivery_date", "timestamp"]].head(5))



# --- ON TIME ---
# True if it shipped on or before the promised date. An order with NaT
# (not shipped yet) will correctly come out False here -- you can't be
# "on time" if you haven't shipped.

otif_df["on_time"]=otif_df["timestamp"]<=otif_df["promised_delivery_date"]

# --- IN FULL ---
# True if the shipped quantity meets or exceeds what was ordered.


otif_df["in_full"]=otif_df["quantity"]>=otif_df["quantity_ordered"]


# --- OTIF: both conditions must be true ---
# The & symbol means "and" when comparing two True/False columns.

otif_df["otif"]=otif_df["on_time"] & otif_df["in_full"]


print(otif_df[["order_id", "quantity_ordered", "quantity", "on_time", "in_full", "otif"]].head(10))



# --- overall OTIF percentage ---
# True/False acts like 1/0 in pandas, so .mean() on a True/False column
# directly gives you "percentage that are True".$


otif_percentage=otif_df["otif"].mean()*100

print(f"\nOverall OTIF percentage: {otif_percentage:.1f}%")





# .groupby() splits the table into groups (one group per customer_id),
# then .mean() calculates the OTIF % WITHIN each group, same trick as
# before (True/False averages into a percentage).
otif_by_customer = otif_df.groupby("customer_id")["otif"].mean().reset_index()

# Turn the 0-1 decimal into an actual percentage, rounded for readability.
otif_by_customer["otif_pct"] = (otif_by_customer["otif"] * 100).round(1)

print(otif_by_customer[["customer_id", "otif_pct"]])



# .dt.isocalendar().week extracts just the week number (1-52) from a
# full date -- so "2026-09-03" becomes week 36, for example. This lets
# us group orders that happened in the same week together.


otif_df["order_week"]=otif_df["order_date"].dt.isocalendar().week

otif_by_week=otif_df.groupby("order_week")["otif"].mean().reset_index()
otif_by_week["otif_pct"]=(otif_by_week["otif"]*100).round(1)

print(otif_by_week[["order_week","otif_pct"]])



import os
gold_dir = "data/gold"
os.makedirs(gold_dir, exist_ok=True)

otif_by_customer[["customer_id", "otif_pct"]].to_csv(f"{gold_dir}/otif_by_customer.csv", index=False)
otif_by_week[["order_week", "otif_pct"]].to_csv(f"{gold_dir}/otif_by_week.csv", index=False)

print("\nGold OTIF tables saved to:", gold_dir)