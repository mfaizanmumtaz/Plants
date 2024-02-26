from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import streamlit as st
import pandas as pd,os

st.set_page_config(page_title="Plant Information Extractor", page_icon=":herb:", layout="wide")

# Name Description Care Requriements Growth Habbits Uses
def main():
    class Extraction(BaseModel):
        """Give the following detailed information about a specific plant."""
        name: str = Field(description="Full name of the plant.")
        description: str = Field(description="Please give the detail Description of the plant.")
        care_requirements: str = Field(description="Please give Care requirements for this plant.")
        growth_habits: str = Field(description="Please Details about the growth habits of this plant.")
        uses: str = Field(description="Please provide details about the uses of this plant.")

    tagging_functions = [convert_pydantic_to_openai_function(Extraction)]

    prompt = ChatPromptTemplate.from_messages([
        ("system", ""),
        ("user", "{input}")
    ])
    os.environ["OPENAI_API_KEY"] = st.session_state["api_key"]
    model = ChatOpenAI(model="gpt-3.5-turbo")

    model_with_functions = model.bind(
        functions=tagging_functions,
        function_call={"name": "Extraction"})

    tagging_chain = prompt | model_with_functions | JsonOutputFunctionsParser()

    def format_data(data):
        name = []
        description = []
        care_requirements = []
        growth_habits = []
        uses = []

        for item in data:
            for key,value in item.items():
                if key == "name":
                    name.append(value)

                elif key == "description":
                    description.append(value)
                
                elif key == "care_requirements":
                    care_requirements.append(value)

                elif key == "growth_habits":
                    growth_habits.append(value)

                elif key == "uses":
                    uses.append(value)
            
        return {"Name":name,"Description":description,"Care Requirements":care_requirements,"Growth Habits":growth_habits,"Uses":uses}

    chain = RunnablePassthrough() | tagging_chain.map() | format_data

    st.info("Please make sure your input file should look like this.")

    df = pd.DataFrame({"Plant Name":["Shrub","Moss","Fern","Palm","Tree"]})

    st.dataframe(df)

    uploaded_file = st.file_uploader("Upload your file here",type=['xlsx'])

    if st.button("Submit"):
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
            if "Plant Name" in df.columns:
                names = list(df.get("Plant Name"))
                with st.spinner("Please wait while we process your data."):
                    try:
                        output = chain.invoke([{"input":plant} for plant in names])
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")
                        st.stop()

                st.success("Your output is ready.")
                st.dataframe(output)

            else:
                st.error("Please make sure your input file should look like this.")
                st.dataframe(df)

from get_key import get_api_key
get_api_key()

if 'api_key' not in st.session_state:
    st.info("Please Enter Your OpenAI API Key To Continue.")
    
if 'api_key' in st.session_state:
    main()