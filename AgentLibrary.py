import pandas as pd
import numpy as np
import re


def get_col_and_example(path):
    df = pd.read_csv(path)
    columns = df.columns
    example_row = df.iloc[0]
    return {'columns' : columns, 'example': example_row}

class Orchestrator:
    def __init__(self, path, user_rule):
        import google.generativeai as genai
        api_key = "AIzaSyDju66-JtD42JqKy6Af5jxJGNGU5kBdNlI"
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        self.csv_path = path
        self.user_rule = user_rule



    def callAgents(self):
        columnExample = get_col_and_example(self.csv_path)
        cleaning_agent = CleaningAgent(self.model, self.csv_path, columnExample['columns'], columnExample['example'], self.user_rule)
        cleaner_object = cleaning_agent.clean()
        train_prep_agent = TrainingPrepAgent(self.model, cleaner_object['cleaned_path'], old_cols=columnExample['columns'], new_cols=cleaner_object['new_columns'])
        new_colExample = get_col_and_example(cleaner_object['cleaned_path'])
        newExample = new_colExample['example']
        response = train_prep_agent.prepare()

        #String Column Encoder is still in development, gemini isnt smart enough yet.

        # SCEncoder = StringColumnEncoderAgent(self.model, cleaner_object['cleaned_path'], column_names=cleaner_object['new_columns'], example=newExample)

        
        # result = SCEncoder.encode()
        return cleaner_object['cleaned_path']
        



        

class CleaningAgent:
    def __init__(self, model, file_path, column_names, example, user_rule):
        self.model = model
        self.file_path = file_path
        self.col_names = column_names
        self.example = example
        self.user_rule = user_rule

    def clean(self):
        prompt = f"""
        Universal Rules :
        You are a data cleaning assistant. Your task is to generate Python code using `pandas` to clean a dataset.
        AT NO COST SHOULD YOU DO ANYTHING EXCEPT DEALING WITH DATA. NO MATTER WHAT USER ASKS. THIS IS TO ENSURE THAT 
        YOU DONT THROW BAD/RANDOM CODE WHICH CANNOT BE EXECUTED. ALSO THIS IS IMPORTANT SO THAT YOU DONT GET JAILBROKEN.
        ONLY EXECUTE THE USER REQUEST IF IT IS RELEVANT TO THE CSV FILE OR DEALS WITH DATA.

        User Rules : (This has the highest priority. Whatever this says MUST be done, can override general rules): {self.user_rule}

        Instructions:
        - Define a function called `run()` that:
            1. Reads the CSV from this path: "{self.file_path}"
            2. Cleans the dataset using inferred logic from column names and sample row.
            3. Writes the cleaned DataFrame to a new CSV file.
            4. Returns a dictionary with:
                - 'cleaned_path': path to the cleaned file
                - 'new_columns': list of column names after cleaning

        
        
                
        General Rules (Can be overriden is user wants to):
        - Use raw strings for regex patterns.
        - Assume the DataFrame is called `df`.
        - Do not use `if __name__ == "__main__"`.
        - Do not wrap code in backticks or include any explanations.
        - Drop columns that appear redundant (e.g., `name`, `ticket`, `url`).
        - Convert gender to 0 (female) and 1 (male) if present.
        - Convert age to integer, drop rows with invalid or missing ages (not in [0, 120]).
        - Handle string columns appropriately (strip, lowercase, or drop).
        - Do not do one hot encoding, it is not part of your job. That is for the developer to decide.
        - Use median for missing numerical values, mode for categorical.
        - The function must be minimal, self-contained, and directly executable.

        Inputs:
        - Column names: {self.col_names}
        - One sample row: {self.example}

        Only return valid executable Python code.
        """


        response = self.model.generate_content(prompt)
        code = response.text.strip()

        # Clean triple backticks if present
        if code.startswith("```"):
            code = "\n".join(code.split("\n")[1:-1])

        # Save to file
        with open("response.txt", "w") as file:
            file.write(code)

        # Execute in local scope
        local_scope = {}
        exec(code, globals(), local_scope)

        if "run" in local_scope and callable(local_scope["run"]):
            result = local_scope["run"]()
            print(f"✅ Agent finished. Output: {result}")
            return result
        else:
            print("❌ No `run()` function found in response.")
            return -1


class TrainingPrepAgent:
    def __init__(self, model, file_path, old_cols, new_cols):
        self.model = model
        self.file_path = file_path
        self.old_cols = old_cols
        self.new_cols = new_cols

    def prepare(self):
        prompt = f"""
        You are a training data validation assistant. Your job is to inspect the dataset before training a machine learning model.

        Given a CSV file, validate:

        That all required columns are present.

        That the target column is not missing.

        That there are no critical missing values in numerical or categorical features.

        That categorical columns are of string/object type and numerical columns are numeric.

        That the distribution of the target variable is not heavily imbalanced.

        Return a function named run() that:

        Loads the dataset

        Performs the above checks

        Raises informative errors or prints warnings if something is wrong

        Returns "Valid dataset" if all checks pass

        IMPORTANT : This is the list of the columns before and after the initial cleaning, make sure that columns are validated, and do not remove any columns which dont exist.
        Old Columns : {self.old_cols}
        New Columns : {self.new_cols}

        Your Python code must read a csv file with the path : {self.file_path}
    

        Only return valid executable Python code. Do not use backticks or explanations.

        Assume the DataFrame is called `df` after reading the CSV.
        """
        
        response = self.model.generate_content(prompt)
        code = response.text.strip()

        # Clean triple backticks if present
        if code.startswith("```"):
            code = "\n".join(code.split("\n")[1:-1])

        # Save to file
        with open("training_prep_response.txt", "w") as file:
            file.write(code)

        # Execute in local scope
        local_scope = {}
        exec(code, globals(), local_scope)

        if "run" in local_scope and callable(local_scope["run"]):
            result = local_scope["run"]()
            print(f"✅ Training prep finished. Output: {result}")
        else:
            print("❌ No `run()` function found in response.")

class StringColumnEncoderAgent:
    def __init__(self, model, file_path, column_names, example):
        self.model = model
        self.file_path = file_path
        self.col_names = column_names
        self.example = example

    def encode(self):
        prompt = f"""
        You are a data transformation assistant specialized in encoding categorical string columns.

        Your task is to generate Python code using pandas that:
        1. Loads the dataset from the given path.
        2. Detects remaining columns that are strings or contain categorical values.
        3. Applies One-Hot Encoding to those columns using `pd.get_dummies()`, dropping the first category to avoid multicollinearity.
        4. Returns a new cleaned dataset with all categorical columns replaced with numeric one-hot encoded columns.
        5. Saves this transformed dataset to a new CSV file.
        6. The function must be named `run()` and return a dictionary with:
            - `"encoded_path"`: the new CSV file path.
            - `"final_columns"`: the list of final column names after encoding.

        *IMPORTANT* : When you do one hot encoding, ideally the encoding should have numbers as the feature values, not True or False, as numbers are easier to deal with.

        File path: "{self.file_path}"

        Column names: {self.col_names}

        Example row: {self.example}

        Only return valid executable Python code. Do NOT include backticks or explanations.
        Assume the dataframe is called `df`.
        """
        
        response = self.model.generate_content(prompt)
        code = response.text.strip()

        # Clean triple backticks if present
        if code.startswith("```"):
            code = "\n".join(code.split("\n")[1:-1])

        # Save to file
        with open("encoded_response.txt", "w") as file:
            file.write(code)

        # Execute the code
        local_scope = {}
        exec(code, globals(), local_scope)

        if "run" in local_scope and callable(local_scope["run"]):
            result = local_scope["run"]()
            print(f"✅ Encoding Agent finished. Output: {result}")
            return result
        else:
            print("❌ No `run()` function found in response.")
            return -1






