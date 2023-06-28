import pandas as pd
import math
import numpy as np
import os

nutrients_dict = {
    'Biotin (UG)' : 30,
    'Calcium, Ca (MG)' : 1000,
    #'Chromium, Cr (UG)' : 35,
    'Choline, total (MG)' : 550,
    'Copper, Cu (MG)' : 0.9,
    'Folate, total (UG)' : 400,
    'Iodine, I (UG)' : 150,
    'Iron, Fe (MG)' : 8,
    'Magnesium, Mg (MG)' : 400,
    'Manganese, Mn (MG)' : 2.3,
    'Molybdenum, Mo (UG)' : 45,
    'Niacin (MG)' : 16,
    'Nickel, Ni (UG)' : 35,
    'Pantothenic acid (MG)' : 5,
    'Phosphorus, P (MG)' : 700,
    'Potassium, K (MG)' : 3400,
    'Riboflavin (MG)' : 1.3,
    'Selenium, Se (UG)' : 55,
    'Sodium, Na (MG)' : 1500,
    'Thiamin (MG)' : 1.2,
    'Vitamin A, RAE (UG)' : 900,
    'Vitamin B-12 (UG)' : 2.4,
    'Vitamin B-6 (MG)' : 1.3,
    'Vitamin C, total ascorbic acid (MG)' : 90,
    'Vitamin D (D2 + D3) (UG)' : 15,
    'Vitamin E (alpha-tocopherol) (MG)' : 15,
    'Vitamin K (phylloquinone) (UG)' : 120,
    'Zinc, Zn (MG)' : 11,
}


def drop_cols(df, cols):
    df.drop(cols, axis=1, inplace=True)
    
def get_foundation_foods_table():

    path = 'C:\\Users\\chris\\Desktop\\mmn data\\Foundation Foods' 
    #path = os.getcwd() + '\\data\\Foundation Foods'
    
    foods = pd.read_csv(path + '\\foundation_food.csv')

    #The descriptions of every food in this particular database
    desc = pd.read_csv(path + '\\food.csv')

    foods = pd.merge(foods, desc, on='fdc_id')

    food_cols_to_drop = ['NDB_number', 'footnote', 'data_type', 'food_category_id', 'publication_date']
    foods.drop(food_cols_to_drop, axis=1, inplace=True)
    
    #foods = pd.read_csv(path + '\\food.csv')
    
    nutrient_match = pd.read_csv(path + '\\food_nutrient.csv')
    
    #The names and units of every nutrient that's tracked
    nutrient_names = pd.read_csv(path + '\\nutrient.csv')
    nutrient_names.rename(columns={'id': 'nutrient_id'}, inplace=True)

    nutrient_match = pd.merge(nutrient_match, nutrient_names, on='nutrient_id', how='left')

    nutrient_match['nutrient_name'] = nutrient_match['name'] + ' (' + nutrient_match['unit_name'] + ')'

    nutrient_cols_to_drop = ["id", 'nutrient_id', 'data_points', 'derivation_id', 'min', 'max', 'median', 'footnote', 'min_year_acqured', "nutrient_nbr", 'rank', 'name', 'unit_name']
    nutrient_match.drop(nutrient_cols_to_drop, axis=1, inplace=True)
    
    #display(nutrient_match.head())
    
    df1 = foods
    df2 = nutrient_match


    # Merge df1 and df2 based on 'fdc_id'
    merged_df = pd.merge(df1, df2, on='fdc_id', how='right')

    # Pivot the merged DataFrame to create columns for unique nutrient_names
    pivoted_df = merged_df.pivot(index='fdc_id', columns='nutrient_name', values='amount')

    # Merge the pivoted DataFrame back to df1 based on 'fdc_id'
    pivoted_df = pd.merge(df1, pivoted_df, on='fdc_id')
    
    #First change all the rows without Total Fat.
    #Most of these are cooking oils (except salt), so I will just put 100 for those.
    pivoted_df.loc[pivoted_df['description'] == 'Salt, table, iodized', 'Total lipid (fat) (G)'] = 0
    rows_with_nan = pivoted_df[pivoted_df["Total lipid (fat) (G)"].isna()]
    pivoted_df.loc[rows_with_nan.index, "Total lipid (fat) (G)"] = 100


    #Next, Protein
    rows_with_nan = pivoted_df[pivoted_df["Protein (G)"].isna()]
    pivoted_df.loc[rows_with_nan.index, "Protein (G)"] = 0

    #Next, carbs
    oils = ['Oil, canola', 'Oil, corn', 'Oil, soybean', 'Oil, olive, extra virgin', 'Butter, stick, unsalted', 'Butter, stick, salted', 'Oil, peanut', 'Oil, sunflower', 'Oil, safflower', 'Oil, olive, extra light']
    pivoted_df.loc[pivoted_df['description'].isin(oils), 'Carbohydrate, by difference (G)'] = 0
    pivoted_df.loc[pivoted_df['description'] == 'Salt, table, iodized', 'Carbohydrate, by difference (G)'] = 0

    mask = pivoted_df['Carbohydrate, by difference (G)'].isnull()
    sum_values = pivoted_df.loc[mask, 'Fiber, total dietary (G)'].add(pivoted_df.loc[mask, 'Starch (G)'], fill_value=0)
    pivoted_df.loc[mask, 'Carbohydrate, by difference (G)'] = sum_values

    #Now calculate Calories for all rows where this is missing
    pivoted_df['Energy (KCAL)'] = pivoted_df['Energy (KCAL)'].fillna(pivoted_df['Energy (Atwater Specific Factors) (KCAL)'])
    pivoted_df['Energy (KCAL)'] = pivoted_df['Energy (KCAL)'].fillna(pivoted_df['Energy (Atwater General Factors) (KCAL)'])

    mask = pivoted_df['Energy (KCAL)'].isnull()
    new_values = 9 * pivoted_df.loc[mask, 'Total lipid (fat) (G)'] + 4 * pivoted_df.loc[mask, 'Protein (G)'] + 4 * pivoted_df.loc[mask, 'Carbohydrate, by difference (G)']
    pivoted_df.loc[mask, 'Energy (KCAL)'] = new_values
    
    
 
    drop_cols(pivoted_df, [np.nan])
    final_df = pivoted_df
    final_df['mass (G)'] = 100
    final_df.fillna(0, inplace=True)

    return final_df

def get_FNDDS_table():
    
    path = 'C:\\Users\\chris\\Desktop\\mmn data\\FNDDS' 
    
    #path = os.getcwd() + '\\data\\FNDDS'
    
    food = pd.read_csv(path + '\\food.csv')
    drop_cols(food, ['data_type', 'food_category_id', 'publication_date'])
    
    food_nutrient = pd.read_csv(path + '\\food_nutrient.csv')
    drop_cols(food_nutrient, ['id', "data_points", "derivation_id", "min", "max", "median", "footnote", "min_year_acquired"])
    
    nutrient = pd.read_csv(path + '\\nutrient.csv')
    drop_cols(nutrient, ['id', 'rank'])
    nutrient.rename(columns={'nutrient_nbr': 'nutrient_id'}, inplace=True)
    
    food_nutrient = pd.merge(food_nutrient, nutrient, on='nutrient_id', how='inner')
    
    food_nutrient['nutrient_name'] = food_nutrient['name'] + ' (' + food_nutrient['unit_name'] + ')'
    drop_cols(food_nutrient, ['nutrient_id', 'name', 'unit_name'])
    
    df1 = food
    df2 = food_nutrient
    

    pivoted_df = df2.pivot(index='fdc_id', columns='nutrient_name', values='amount')
    
    # Merge the pivoted DataFrame back to df1 based on 'fdc_id'
    merged_df = pd.merge(df1, pivoted_df, on='fdc_id')
    
    final_df = merged_df
    final_df['mass (G)'] = 100
    final_df.fillna(0, inplace=True)
    
    return final_df
    
    
def get_sr_legacy_table():

    path = 'C:\\Users\\chris\\Desktop\\mmn data\\SR Legacy' 

    #path = os.getcwd() + '\\data\\SR Legacy'
    
    food = pd.read_csv(path + '\\food.csv')
    drop_cols(food, ['data_type', 'food_category_id', 'publication_date'])
    
    food_nutrient = pd.read_csv(path + '\\food_nutrient.csv')
    drop_cols(food_nutrient, ['id', "data_points", "derivation_id", "min", "max", "median", "footnote", "min_year_acquired"])
    
    nutrient = pd.read_csv(path + '\\nutrient.csv')
    drop_cols(nutrient, ['nutrient_nbr', 'rank'])
    nutrient.rename(columns={'id': 'nutrient_id'}, inplace=True)
    
    food_nutrient = pd.merge(food_nutrient, nutrient, on='nutrient_id', how='inner')
    
    food_nutrient['nutrient_name'] = food_nutrient['name'] + ' (' + food_nutrient['unit_name'] + ')'
    drop_cols(food_nutrient, ['nutrient_id', 'name', 'unit_name'])
    
    df1 = food
    df2 = food_nutrient
    

    pivoted_df = df2.pivot(index='fdc_id', columns='nutrient_name', values='amount')
    
    # Merge the pivoted DataFrame back to df1 based on 'fdc_id'
    merged_df = pd.merge(df1, pivoted_df, on='fdc_id')
    
    final_df = merged_df
    final_df['mass (G)'] = 100
    final_df.fillna(0, inplace=True)
    
    return final_df
    
    
def get_all_databases_table():
    
    path = 'C:\\Users\\chris\\Desktop\\mmn data\\All Databases' 
    
    path = os.getcwd() + '\\data\\All Databases'
    
    cats = [1002, 1004, 1006, 1008, 1404, 1602, 1604, 1820, 1822, 2002, 2004, 2006, 2008, 2010, 2202, 2206, 2402, 2404, 2502, 2802, 2804, 4002, 4004, 4204, 4206, 4208, 4802, 4804, 6002, 6004, 6006, 6008, 6009, 6011, 6012, 6014, 6016, 6018, 6020, 6022, 6024, 6402, 6404, 6406, 6407, 6409, 6410, 6411, 6412, 6413, 6414, 6416, 6418, 6420, 6802, 8002, 8006, 8008, 8408]
    food = pd.read_csv(path + '\\food.csv')
    food = food[food['food_category_id'].isin(cats)]
    drop_cols(food, ['data_type', 'food_category_id', 'publication_date'])
    
    food_nutrient = pd.read_csv(path + '\\food_nutrient.csv')
    drop_cols(food_nutrient, ['id', "data_points", "derivation_id", "min", "max", "median", "footnote", "min_year_acquired"])
    
    nutrient = pd.read_csv(path + '\\nutrient.csv')
    drop_cols(nutrient, ['nutrient_nbr', 'rank'])
    nutrient.rename(columns={'id': 'nutrient_id'}, inplace=True)
    
    food_nutrient = pd.merge(food_nutrient, nutrient, on='nutrient_id', how='inner')
    
    food_nutrient['nutrient_name'] = food_nutrient['name'] + ' (' + food_nutrient['unit_name'] + ')'
    drop_cols(food_nutrient, ['nutrient_id', 'name', 'unit_name', 'loq'])
    food_nutrient = food_nutrient[~food_nutrient.duplicated(subset=['fdc_id', 'nutrient_name'], keep='last')]
    
    df1 = food
    df2 = food_nutrient
    
    
    pivoted_df = df2.pivot(index='fdc_id', columns='nutrient_name', values='amount')
    
    # Merge the pivoted DataFrame back to df1 based on 'fdc_id'
    merged_df = pd.merge(df1, pivoted_df, on='fdc_id')
    
    final_df = merged_df
    final_df['mass (G)'] = 100
    final_df.fillna(0, inplace=True)
    
    return final_df
    
    
def extract_tuples(input_string):
    lines = input_string.strip().split('\n')
    tuples = []
    for line in lines:
        if line.startswith('-'):
            line = line.lstrip('-').strip()
            food, number = line.split(':')
            food = food.strip()
            number = float(number.split()[0])
            tuples.append((food, number))
    return tuples


def filter_dataframe(df, tuples):
    # Extract the food names from the tuples
    foods = [t[0] for t in tuples]
    
   
    # Filter the dataframe based on the "description" column
    new_df = df[df['description'].isin(foods)]
    
    return new_df

#Returns a dataframe with only foods that the pulp function suggests
def nutrition_of_list(df, input_string):

    tuples = extract_tuples(input_string)
    
    new_df = filter_dataframe(df, tuples)  # Create a copy of the original dataframe
    
    
    keep_cols = ['Energy (KCAL)', 'mass (G)', 'description']
    
    for food, factor in tuples:
        # Multiply the numeric columns by the factor for the matching food
        mask = new_df['description'] == food
        numeric_cols = new_df.select_dtypes(include='number').columns
        new_df.loc[mask, numeric_cols] *= (factor / 100)
        
        
    columns_list = new_df.columns.tolist()
    
    for col in columns_list:
        if (col not in keep_cols) and (col not in nutrients_dict.keys()):
            drop_cols(new_df, col)
        
    
    return new_df
    
    
def find_PDV(df):
    
    string = ''
    
    for key, value in nutrients_dict.items():
        string += f'{key}: {round(df[key].sum() / value * 100, 1)  }%\n'
        
    return string