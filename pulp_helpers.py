import pandas as pd
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpConstraint, LpStatus
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



def add_constraint(df, problem, tup, foods, food_vars):
    if tup[1] == -1:
        con = (
        lpSum([food_vars[i] * df[tup[0]][i] for i in foods]) <= tup[2]
        )
    elif tup[1] == 0:
        con = (
        lpSum([food_vars[i] * df[tup[0]][i] for i in foods]) == tup[2]
        )
    else:
        con = (
        lpSum([food_vars[i] * df[tup[0]][i] for i in foods]) >= tup[2]
        )
    problem += con
    

def default_problem(df, add_constraints = []):
    sol = ""
    
    index_to_description = {i: description for i, description in enumerate(df["description"])}

    # Create the LP problem
    problem = LpProblem("Food Selection", LpMinimize)

    # Create the decision variables (amount of each food item to select)
    foods = df.index  # Assume the index of the dataframe represents food items
    food_vars = LpVariable.dicts("Food", foods, lowBound=0, cat="Continuous")

    # Define the objective function to minimize the sum of total calories
    objective = (
        lpSum([food_vars[i] * df.loc[i, "Energy (KCAL)"] for i in foods])
    )
    problem += objective

    
    
    # Add the constraints for nutrient requirements
    for nutrient, min_amount in nutrients_dict.items():
        
        if nutrient in df and df[nutrient].gt(0).any():
            nutrient_values = df[nutrient]
            nutrient_total = (
                lpSum([food_vars[i] * nutrient_values[i] for i in foods])
            )
            problem += (nutrient_total >= min_amount)
            
        else:
            sol += f'{nutrient} NOT INCLUDED\n'
    for constraint in add_constraints:
        add_constraint(df, problem, constraint, foods, food_vars)
    
    
    
    problem.solve()
    

    
    
    if problem.status == 1:
        mass_total = 0

        # Print the optimal solution
        for food in foods:
            if food_vars[food].varValue is not None and food_vars[food].varValue > 0:
                mass_total += (food_vars[food].varValue * 100)
                sol += f"-{index_to_description[food]}: {round(food_vars[food].varValue * 100, 2)} g\n"

        sol += f"Total Calories: {round(problem.objective.value(), 1)}\n"
        sol += f"Total Mass: {round(mass_total)} g ({round(mass_total/453.59237, 1)} lbs)"
    
    else:
        sol += "Problem is undefined with the given constraints."
        
    return sol
    
    
    

def prob_with_set_foods(df, add_constraints = [], foods_df):
    sol = ""
    
    index_to_description = {i: description for i, description in enumerate(df["description"])}

    # Create the LP problem
    problem = LpProblem("Food Selection", LpMinimize)

    # Create the decision variables (amount of each food item to select)
    foods = df.index  # Assume the index of the dataframe represents food items
    food_vars = LpVariable.dicts("Food", foods, lowBound=0, cat="Continuous")

    # Define the objective function to minimize the sum of total calories
    objective = (
        lpSum([food_vars[i] * df.loc[i, "Energy (KCAL)"] for i in foods])
    )
    problem += objective

    
    
    # Add the constraints for nutrient requirements
    for nutrient, min_amount in nutrients_dict.items():
        
        if nutrient in df and df[nutrient].gt(0).any():
            nutrient_values = df[nutrient]
            nutrient_total = (
                lpSum([food_vars[i] * nutrient_values[i] for i in foods])
            )
            problem += (nutrient_total >= min_amount)
            
        else:
            sol += f'{nutrient} NOT INCLUDED\n'
    for constraint in add_constraints:
        add_constraint(df, problem, constraint, foods, food_vars)
    
    
    
    problem.solve()
    

    
    
    if problem.status == 1:
        mass_total = 0

        # Print the optimal solution
        for food in foods:
            if food_vars[food].varValue is not None and food_vars[food].varValue > 0:
                mass_total += (food_vars[food].varValue * 100)
                sol += f"-{index_to_description[food]}: {round(food_vars[food].varValue * 100, 2)} g\n"

        sol += f"Total Calories: {round(problem.objective.value(), 1)}\n"
        sol += f"Total Mass: {round(mass_total)} g ({round(mass_total/453.59237, 1)} lbs)"
    
    else:
        sol += "Problem is undefined with the given constraints."
        
    return sol
    
    
    
