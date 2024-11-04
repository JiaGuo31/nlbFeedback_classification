import pandas as pd
from feedback_handler import feedback_class
import json
import time
import streamlit as st

# run through model
def iterate_test_set(test_data):
    # Record the start time
    progress_bar = st.progress(0)
    start_time = time.time()
    print("Starting the function...")
    i=0
    iterations = test_data.shape[0]

    # Extract the "Cleaned Text" data
    feedback = test_data["Cleaned Text"]
    classified = []

    # Process each user message
    for user_message in feedback:
        progress_percentage = (i + 1) / iterations
        progress_bar.progress(progress_percentage)
        i += 1
        response = feedback_class.process_feedback_class(user_message) 
        try:
            # response_json = json.loads(response)
            # responses = response_json.get("feedback_data")
            for response_dict in response:
                response_dict["feedback_text"] = user_message
                classified.append(response_dict)
            
        except:
            classified.append({"category":"","subcategory":"", 
                               "keywords": "", "feedback_text":user_message})
    # Convert the list of responses to a DataFrame
    df = pd.json_normalize(classified)

    # Record the end time and calculate the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Print the elapsed time in a readable format
    print(f"Function completed in {elapsed_time:.2f} seconds.")
    
    return df, classified

def validate(test_data):
    df, classified = iterate_test_set(test_data)
    validation = test_data.merge(df, how = "left", left_on = "Cleaned Text", right_on = "feedback_text", suffixes = (None, "_output"))
    # create a combination field for category and sub category
    validation["comb_cat"] = validation["Category"] + validation["Sub Category"]
    validation["comb_cat_output"] = validation["category"] + validation["subcategory"]

    validation["correct_sub_cat_flag"] = validation["comb_cat"] == validation["comb_cat_output"] 
    validation["correct_cat_flag"]  = validation["Category"] == validation["category"] 
    # keep only unique categories for each feedback in test set
    validation_cat = validation.drop_duplicates(["Cleaned Text", "Category", "correct_cat_flag"])
    total_count = test_data.shape[0]

    # recall for categories: number of correctly classified categories out of test set
    print(f"Number of correct categories:\n{validation_cat["correct_cat_flag"].sum()} of {total_count}")
    # recall for sub-categories.
    print(f"Number of correct sub-categorisations:\n{validation["correct_sub_cat_flag"].sum()} of {total_count}")
    return validation, validation_cat

if __name__ == "__main__":
    # read test data
    test_data = pd.read_csv("test_data_and_functions/Composite test set for all categories.csv", 
                            usecols=["Category","Sub Category","Cleaned Text"]).dropna()
    validation_subcat, validation_cat = validate(test_data)
    validation_subcat.to_csv("test_data_and_functions/validation_results.csv")