# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import snowflake.connector
import requests
import pandas
 

# Write directly to the app
st.title("Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!""")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

##session = get_active_session()
#cnx = st.connection("snowflake", 
#    connection_args={
#        "insecure_mode": True  # TEMPORARILY disable SSL certificate check
#    }
#)
#session = cnx.session()
# Use Streamlit secrets for credentials
conn = snowflake.connector.connect(
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    account=st.secrets["snowflake"]["account"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"],
    role=st.secrets["snowflake"].get("role", "PUBLIC")  # Default to PUBLIC role
)

# Create a session
session = conn.cursor()
#my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# replaced the above with what's below as part of the move to SniS
my_dataframe = session.execute("SELECT FRUIT_NAME, SEARCH_ON FROM smoothies.public.fruit_options")
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#Convert the my_dataframe to a pandas dataframe.
pd_df=my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredents'
    , my_dataframe
    , max_selections=5
)

if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order +"""')"""

    #st.write(my_insert_stmt)
    #st.stop()
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        #Changes due to SniS migration.  It's a difference between using snowflake.connector (SniS) vs. Snowpark (SiS)
        #session.sql(my_insert_stmt).collect()
        session.execute(my_insert_stmt)

        st.success('Your Smoothie is ordered!', icon="✅")
