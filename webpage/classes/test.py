import pandas as pd

# Define the data as a list of dictionaries
data = [
    {
        "start_date": "2023-01-01",
        "end_date": "2023-03-01",
        "diet": 178.18295000000003,
        "transportation": 39.599999999999994,
        "car": 0.0,
        "bustrain": 39.599999999999994,
        "plane": 0.0,
        "housing": 79.64999999999999,
        "consumption": 477.6575342465754,
        "shopping_profile": 0.0,
        "refurbished": 0.0,
        "waste": 19.972712328767123,
        "plastic": 1.0,
        "glass": 1.0,
        "paper": 1.0,
        "aluminium": 1.0,
        "number_of_days": 59,
        "average_per_day": 13.475647399582076,
        "total": 795.0631965753425
    },
    {
        "start_date": "2023-03-01",
        "end_date": "2023-05-01",
        "diet": 190.92207000000002,
        "transportation": 26.4,
        "car": 0.0,
        "bustrain": 26.4,
        "plane": 0.0,
        "housing": 82.35,
        "consumption": 493.8493150684932,
        "shopping_profile": 0.0,
        "refurbished": 0.0,
        "waste": 20.649753424657533,
        "plastic": 1.0,
        "glass": 1.0,
        "paper": 1.0,
        "aluminium": 1.0,
        "number_of_days": 61,
        "average_per_day": 13.347067844150011,
        "total": 814.1711384931507
    },
    {
        "start_date": "2023-05-02",
        "end_date": "2023-06-01",
        "diet": 98.53095144694535,
        "transportation": 15.470739549839227,
        "car": 0.0,
        "bustrain": 15.470739549839227,
        "plane": 0.0,
        "housing": 41.654662379421225,
        "consumption": 245.61005153503947,
        "shopping_profile": 0.16666666666666666,
        "refurbished": 0.16666666666666666,
        "waste": 10.805512927806898,
        "plastic": 0.8333333333333334,
        "glass": 0.8333333333333334,
        "paper": 0.8333333333333334,
        "aluminium": 0.8333333333333334,
        "number_of_days": 30,
        "average_per_day": 13.735730594635072,
        "total": 412.07191783905216
    },
    {
        "start_date": "2023-06-02",
        "end_date": "2023-06-09",
        "diet": 89.88938000000002,
        "transportation": 0.0,
        "car": 0.0,
        "bustrain": 0.0,
        "plane": 0.0,
        "housing": 21.42,
        "consumption": 85.00684931506851,
        "shopping_profile": 1.0,
        "refurbished": 0.0,
        "waste": 9.10690410958904,
        "plastic": 0.0,
        "glass": 0.0,
        "paper": 0.0,
        "aluminium": 0.0,
        "number_of_days": 7,
        "average_per_day": 29.346161917808224,
        "total": 205.42313342465758
    },
    {
        "start_date": "2023-06-10",
        "end_date": "2023-06-30",
        "diet": 65.68730096463024,
        "transportation": 10.313826366559484,
        "car": 0.0,
        "bustrain": 10.313826366559484,
        "plane": 0.0,
        "housing": 27.76977491961415,
        "consumption": 163.74003435669297,
        "shopping_profile": 0.16666666666666666,
        "refurbished": 0.16666666666666666,
        "waste": 7.203675285204598,
        "plastic": 0.8333333333333334,
        "glass": 0.8333333333333334,
        "paper": 0.8333333333333334,
        "aluminium": 0.8333333333333334,
        "number_of_days": 20,
        "average_per_day": 13.735730594635072,
        "total": 274.71461189270144
    },
    {
        "start_date": "2023-07-01",
        "end_date": "2023-09-01",
        "diet": 190.64752000000001,
        "transportation": 32.99999999999999,
        "car": 0.0,
        "bustrain": 32.99999999999999,
        "plane": 0.0,
        "housing": 83.69999999999999,
        "consumption": 501.9452054794521,
        "shopping_profile": 0.0,
        "refurbished": 1.0,
        "waste": 20.98827397260274,
        "plastic": 1.0,
        "glass": 1.0,
        "paper": 1.0,
        "aluminium": 1.0,
        "number_of_days": 62,
        "average_per_day": 13.391629023420242,
        "total": 830.280999452055
    },
    {
        "start_date": "2023-09-01",
        "end_date": "2023-11-01",
        "diet": 189.24731500000001,
        "transportation": 29.699999999999996,
        "car": 0.0,
        "bustrain": 29.699999999999996,
        "plane": 0.0,
        "housing": 82.35,
        "consumption": 493.8493150684932,
        "shopping_profile": 0.0,
        "refurbished": 0.0,
        "waste": 20.649753424657533,
        "plastic": 1.0,
        "glass": 1.0,
        "paper": 1.0,
        "aluminium": 1.0,
        "number_of_days": 61,
        "average_per_day": 13.347067844150011,
        "total": 814.1711384931507
    }
]

# Create the DataFrame
df = pd.DataFrame(data)

# Select the desired columns
selected_columns = ["end_date", "diet", "transportation", "housing", "consumption", "waste", "total", "number_of_days"]
df = df[selected_columns]

# Display the new DataFrame
print(df)

new_df = df.copy()

# Initialize an empty list to store the exploded rows
exploded_rows = []

    
# Concatenate the exploded rows to create the new DataFrame
new_df = pd.concat(exploded_rows).reset_index(drop=True)

print(new_df)
