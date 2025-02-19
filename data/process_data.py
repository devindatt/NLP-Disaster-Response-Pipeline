# import libraries
import os
import pandas as pd
import numpy as np
import sys
from sqlalchemy import create_engine


def load_data(messages_filepath, categories_filepath):

    '''
    Input:
        messages_filepath: File path of messages data
        categories_filepath: File path of categories data
    Output:
        df: Merged dataset from messages and categories
    '''

    # load messages dataset
    messages = pd.read_csv(messages_filepath)

    # load categories dataset
    categories = pd.read_csv(categories_filepath)

    # merge datasets
    df = messages.merge(categories, how='outer', on=['id'])

    return df


def clean_data(df):

    '''
    Input:
        df: Merged dataset from messages and categories
    Output:
        df2: A complete cleaned dataset
    '''
    # create a dataframe of the 36 individual category columns
    categories = df['categories'].str.split(';', expand=True)

    # select the first row of the categories dataframe
    row = categories.loc[0].values

    # extract a list of new column names for categories that takes everything 
    # up to the second to last character of each string with slicing
    category_colnames = list(map(lambda x: x[:-2], row))

    # rename the columns of `categories`
    categories.columns = category_colnames

    #Convert category values to just numbers 0 or 1
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].apply(lambda x: x[-1])
        # convert column from string to numeric
        categories[column] = pd.Series(categories[column], dtype='int8')

    # drop the original categories column from `df`
    messages = df.drop('categories', axis=1)

    # concatenate the original dataframe with the new `categories` dataframe
    df2 = pd.concat([messages, categories], axis=1)

    # drop duplicates
    df2 = df2.drop_duplicates()

    return df2



def save_data(df, database_filename):
    '''
    Input:
        df: cleaned dataset
        database_filename: database name, e.g. DisasterResponse.db
    Output: 
        A SQLite database
    '''

    # Save df into sqlite database
    engine = create_engine('sqlite:///'+database_filename)
    df.to_sql('disaster_texts', con=engine, index=False)

    
def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df2 = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df2, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()