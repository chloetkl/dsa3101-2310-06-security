import pandas as pd
import requests

# reads in the users data
user_data = pd.read_csv("/data/datacsv.csv")
print("Working..\n")

# for each of the record, send a POST request to insert the value inside
for i in range(user_data.shape[0]):
    current_user = user_data.loc[i].to_dict()
    try:
        requests.post("http://web:5000/add_customer", data=current_user) 
    except:
        pass
