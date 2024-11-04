import streamlit as st
from test_data_and_functions import cleaning_output
import pandas as pd
import matplotlib.pyplot as plt
from utility import check_password

if not check_password():  
    st.stop()

st.title("Validation Test Set")
st.write("This page displays the validation test set for the classification model. "
         "The test set was consonlidated from CRM feedback from 2021 and some manually categorised CSS feedback for categories that did not exist in 2021."
         "This page may take 5 min to load as it calls the LLM to classify the test set, do not click away in the meantime.")

if 'test_data' not in st.session_state:
    st.session_state.test_data = pd.read_csv("test_data_and_functions/Composite test set for all categories.csv", 
                                            usecols=["Category","Sub Category","Cleaned Text"]).dropna()

if 'validation_subcat' not in st.session_state:
    # st.session_state.validation_subcat, st.session_state.validation_cat = cleaning_output.validate(st.session_state.test_data)
    st.session_state.validation_subcat = pd.read_csv("test_data_and_functions/validation_results.csv")
    st.session_state.validation_cat = st.session_state.validation_subcat.drop_duplicates(["Cleaned Text", "Category", "correct_cat_flag"])

if st.session_state.test_data is not None and not st.session_state.test_data.empty:
    # Display the data in an interactive table
    st.dataframe(st.session_state.test_data)
    total_count = st.session_state.test_data.shape[0]
else: 
    st.write("No test data available")

if st.session_state.validation_subcat is not None and not st.session_state.validation_subcat.empty:
    st.subheader("Validation Summary")
    
    # createing pie charts
    labels = 'Same', 'Different'
    sizes = [st.session_state.validation_cat["correct_cat_flag"].sum(), total_count-st.session_state.validation_cat["correct_cat_flag"].sum()]
    labels2 = 'Same', 'Different'
    sizes2 = [st.session_state.validation_subcat["correct_sub_cat_flag"].sum(), total_count-st.session_state.validation_subcat["correct_sub_cat_flag"].sum()]
    explode = (0.1, 0)  # only "explode" the 1st slice

    fig1, (ax1, ax2) = plt.subplots(1,2)
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',textprops={'color':"w"},
            shadow=False, startangle=90, colors = ["mediumseagreen", "slategrey"])
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    # recall for categories: number of correctly classified categories out of test set
    ax1.set_title(f"Number of identical categories: \n {st.session_state.validation_cat["correct_cat_flag"].sum()} of {total_count}",
                fontsize = 10, color = "ghostwhite")
        
    ax2.pie(sizes2, explode=explode, labels=labels2, autopct='%1.1f%%',textprops={'color':"w"},
                shadow=False, startangle=90, colors = ["dodgerblue", "slategrey"])
    ax2.axis('equal')  
    ax2.set_title(f"Number of identical sub-categorisations:\n{st.session_state.validation_subcat["correct_sub_cat_flag"].sum()} of {total_count}",
                fontsize = 10, color = "ghostwhite")
    fig1.set_facecolor(color = ('lightgrey',0.0))
    st.pyplot(fig1)

    different_cat_df = st.session_state.validation_subcat.loc[~st.session_state.validation_subcat.correct_sub_cat_flag,
                                              ["Cleaned Text","Category","Sub Category","category",
                                               "subcategory","keywords"]]
    different_cat_df.columns = ["Feedback/Enquiry", "CRM_Category", "CRM_SubCategory", 
                                "LLM_Category", "LLM_SubCategory", "LLM_Keywords"]
    st.write("Table of Feedback Categorised Differently:")
    st.dataframe(different_cat_df)

else:
    st.write("No validation results available.")