import json
import pandas as pd
with open('products_1.json', 'r') as file:
    data = json.load(file)
    
# Convert data to a DataFrame for easier processing
df = pd.DataFrame(data)

# List all unique currencies in the JSON data
unique_currencies = df['rating']

# Display the unique currencies
print(unique_currencies)
