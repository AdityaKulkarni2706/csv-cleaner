
import pandas as pd
import numpy as np

def clean_titanic_data(df):
    """
    Cleans the Titanic dataset based on predefined rules.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The cleaned DataFrame.
    """

    # 1. PassengerId: No cleaning needed (assuming it's a unique identifier)

    # 2. Survived: Convert to integer type
    df['Survived'] = df['Survived'].astype(int)

    # 3. Pclass: Convert to integer type
    df['Pclass'] = df['Pclass'].astype(int)

    # 4. Name: Strip whitespace
    df['Name'] = df['Name'].str.strip()

    # 5. Sex: Convert to lowercase and strip whitespace
    df['Sex'] = df['Sex'].str.lower().str.strip()

    # 6. Age: Impute missing values with the median
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    df['Age'] = df['Age'].fillna(df['Age'].median())

    # 7. SibSp: Convert to integer type
    df['SibSp'] = df['SibSp'].astype(int)

    # 8. Parch: Convert to integer type
    df['Parch'] = df['Parch'].astype(int)

    # 9. Ticket: Strip whitespace
    df['Ticket'] = df['Ticket'].str.strip()

    # 10. Fare: Impute missing values with the median, remove outliers by capping the value at 99th percentile
    df['Fare'] = pd.to_numeric(df['Fare'], errors='coerce')
    df['Fare'] = df['Fare'].fillna(df['Fare'].median())
    fare_threshold = df['Fare'].quantile(0.99)
    df['Fare'] = df['Fare'].clip(upper=fare_threshold)


    # 11. Cabin: Fill missing values with 'Unknown' and strip whitespace
    df['Cabin'] = df['Cabin'].fillna('Unknown').str.strip()

    # 12. Embarked: Fill missing values with the mode, convert to lowercase and strip whitespace
    df['Embarked'] = df['Embarked'].fillna(df['Embarked'].mode()[0]).str.lower().str.strip()

    return df

if __name__ == '__main__':
    # Sample usage:
    
    df = pd.read_csv("train.csv")
    

    cleaned_df = clean_titanic_data(df)
    cleaned_df.to_csv('cleaned_titanic.csv', index=False)
    print("Cleaned data written to cleaned_titanic.csv")

