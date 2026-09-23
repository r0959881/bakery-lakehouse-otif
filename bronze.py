

import pandas as pd

Bronze_dir="data/bronze"


mes_df=pd.read_csv(f"{Bronze_dir}/mes_export.csv")
erp_df=pd.read_csv(f"{Bronze_dir}/erp_export.csv")
wms_df=pd.read_csv(f"{Bronze_dir}/wms_export.csv")

print("MES shape:",mes_df.shape)
print("ERP shap:",erp_df.shape)
print("WMS shape:",wms_df.shape)

print()

print("MES shape:",mes_df)
print("ERP shap:",erp_df)
print("WMS shape:",wms_df)

print("MES column types:\n",mes_df.dtypes)

print("ERP column types:\n",erp_df.dtypes)

print("WMS column types:\n",wms_df.dtypes)

print("\n--- PIECE 2: fixing date columns ---\n")

mes_df["start_time"] = pd.to_datetime(mes_df["start_time"])
mes_df["end_time"] = pd.to_datetime(mes_df["end_time"])

erp_df["order_date"] = pd.to_datetime(erp_df["order_date"])
erp_df["promised_delivery_date"] = pd.to_datetime(erp_df["promised_delivery_date"])

wms_df["timestamp"] = pd.to_datetime(wms_df["timestamp"])

mes_df["duration_hours"]=(mes_df["end_time"]-mes_df["start_time"]).dt.total_seconds() /3600



print("start_time dtype is now:", mes_df["start_time"].dtype)
print("\nFirst 3 batch durations (hours):")
print(mes_df[["batch_id", "start_time", "end_time", "duration_hours"]].head(3))





# 1 check the duplicates



print("Duplicate in MES:\n",mes_df.duplicated().sum())
print("Duplicate in ERP:\n",erp_df.duplicated().sum())
print("Duplicate in WMS:\n",wms_df.duplicated().sum())

#2 check the missing values

print("\nMissing values in MES:\n",mes_df.isnull().sum())
print("\nMissing values in ERP:\n",erp_df.isnull().sum())
print("\nMissing values in WMS:\n",wms_df.isnull().sum())

# 3 fix the duplicate in MES

mes_df=mes_df.drop_duplicates()

print("\nDuplicate in MES after dropping:\n", len(mes_df))


# 4 fix the missing values in MES

mes_df["downtime_minutes"]=mes_df["downtime_minutes"].fillna(0)

print("\nMissing values in Mes after fixing :\n",mes_df.isnull().sum())


real_batch_ids=set(mes_df["batch_id"].unique())

wms_inbound=wms_df[wms_df["movement_type"]=="INBOUND"].copy()


wms_inbound["batch_exists_in_mes"]=wms_inbound["batch_id"].isin(real_batch_ids)

broken_links=wms_inbound[wms_inbound["batch_exists_in_mes"]==False]

print(f"\nFound {len(broken_links)} WMS row(s) with batch_id not in MES")
print(broken_links[["movement_type","batch_id", "quantity"]])



# 6 remove the broken WMS row, then save everything to the silver folder


wms_df_clean=wms_df[wms_df["batch_id"] != "Batch_9999"].copy()
print("\nWMS ROW COUNT AFTER REMOVING BROKEN LINKS:",len(wms_df_clean))

# --- save the cleaned files as your Silver layer ---

import os

silver_dir="data/silver"
os.makedirs(silver_dir, exist_ok=True)

mes_df.to_csv(f"{silver_dir}/mes_silver.csv", index=False)
erp_df.to_csv(f"{silver_dir}/erp_silver.csv", index=False)
wms_df_clean.to_csv(f"{silver_dir}/wms_silver.csv", index=False)

print("\nSilver files saved to :", silver_dir)

