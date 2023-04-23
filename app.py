import streamlit as st
import pandas as pd
import ast 
import altair as alt
import json
import pickle


def find_image(gis,restaurant_name):
    gis.search({'q': "Restaurante" + restaurant_name, 'num': 3, 'imgType': 'photo','fileType': 'jpeg'})
    return gis.results()[0].url

# read json from file
json_ = json.load(open("data/review_summary.json", "r"))
for restaurant in json_:
    for category in json_[restaurant]:
        if json_[restaurant][category] != None:
            json_[restaurant][category] -= 3
learned_ids = list(json_.keys())
        
# read business data from file
url_business = "data/yelp_dataset/yelp_academic_dataset_business.json"
with open(url_business) as f:
    dict_business = [json.loads(line) for line in f.readlines()]
    dict_business = [x for x in dict_business if x["business_id"] in learned_ids]
    dict_business = {x["business_id"]: x for x in dict_business}
id_name = {x["business_id"]: x["name"] for x in dict_business.values()}
name_id = {x["name"]: x["business_id"] for x in dict_business.values()}

# read recs from file   
url_recs = "data/recs.json"
with open(url_recs) as f:
    recs = json.load(f)

# transform data
restaurant_summary = {}
for restaurant in json_:
    restaurant_summary[id_name[restaurant]] = json_[restaurant]
df = pd.DataFrame(columns=["restaurant", "category", "value"])
for restaurant in restaurant_summary:
    for category in restaurant_summary[restaurant]:
        df = df._append({"restaurant": restaurant, "category": category, "value": restaurant_summary[restaurant][category]}, ignore_index=True)

#### Sidebar
st.sidebar.header("Filters")
# ["studying", "atmosphere", "music", "wifi", "price", "staff", "food", "coffee"]
range_atmosphere = st.sidebar.slider("Atmosphere", -2.5, 2.5, (-2.5, 2.5))
range_coffee = st.sidebar.slider("Coffee", -2.5, 2.5, (-2.5, 2.5))
range_food = st.sidebar.slider("Food", -2.5, 2.5, (-2.5, 2.5))
range_music = st.sidebar.slider("Music", -2.5, 2.5, (-2.5, 2.5))
range_price = st.sidebar.slider("Price", -2.5, 2.5, (-2.5, 2.5))
range_staff = st.sidebar.slider("Staff", -2.5, 2.5, (-2.5, 2.5))
range_studying = st.sidebar.slider("Studying", -2.5, 2.5, (-2.5, 2.5))

## Filter restaurants
df_filtered = df.dropna()
# remove all the rows of restaurants that have a value outside the range
names_to_remove = []
for restaurant in df_filtered["restaurant"].unique():
    df_restaurant = df_filtered[df_filtered["restaurant"] == restaurant]
    for category in df_restaurant["category"].unique():
        df_category = df_restaurant[df_restaurant["category"] == category]
        for index, row in df_category.iterrows():
            if (row["category"] == "atmosphere" and (row["value"] < range_atmosphere[0] or row["value"] > range_atmosphere[1]))\
                 or (row["category"] == "coffee" and (row["value"] < range_coffee[0] or row["value"] > range_coffee[1]))\
                    or (row["category"] == "food" and (row["value"] < range_food[0] or row["value"] > range_food[1]))\
                        or (row["category"] == "music" and (row["value"] < range_music[0] or row["value"] > range_music[1]))\
                            or (row["category"] == "price" and (row["value"] < range_price[0] or row["value"] > range_price[1]))\
                                or (row["category"] == "staff" and (row["value"] < range_staff[0] or row["value"] > range_staff[1]))\
                                    or (row["category"] == "studying" and (row["value"] < range_studying[0] or row["value"] > range_studying[1])):
                names_to_remove.append(restaurant)
                break
        if restaurant in names_to_remove:
            break
    
df_filtered = df_filtered[~df_filtered["restaurant"].isin(names_to_remove)]
restaurant_names = df_filtered["restaurant"].unique()

#### Main app
col1, col2, col3 = st.columns([1,6,1])

import base64
from pathlib import Path

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded
def img_to_html(img_path, width=150):
    img_html = f"<p style='text-align: center;'><img src='data:image/png;base64,{{}}' class='img-fluid' width='{width}'></p>".format(
      img_to_bytes(img_path)
    )
    return img_html

with col1:
    st.write("")
with col2:
    st.markdown(img_to_html('media/logo.png'), unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>RoastReviews</h1>", unsafe_allow_html=True)
with col3:
    st.write("")

# searchbar
rest_name = st.selectbox("Search for a restaurant", restaurant_names)

if rest_name:
    col1, col2 = st.columns([7,4])
    with col1:
        st.subheader(rest_name)
        # plot the number of stars of the restaurant, using dict_business, the element stars
        stars = dict_business[name_id[rest_name]]["stars"]
        # print the number of stars and as many stars as the number of stars
        st.write(str(dict_business[name_id[rest_name]]["stars"]), "⭐" * int(stars))
    
    style = """
        <style>
            .oval-frame {
                border: 2px solid #555;
                border-radius: 30px;
                padding: 10px;
                width: fit-content;
            }
        </style>
    """
    st.markdown(style, unsafe_allow_html=True)
    
    words = recs[name_id[rest_name]]
    # vector with the length of each word
    lengths = [len(word) for word in words]
    cols = st.columns(lengths)
    for i in range(len(words)):
        cols[i].markdown(f'<span class="oval-frame">{words[i]}</span>', unsafe_allow_html=True)
    # st.markdown(f'<p class="oval-frame">{text}</p>', unsafe_allow_html=True)
        
    with col2:
        st.markdown(img_to_html(f'media/{name_id[rest_name]}.png', 240), unsafe_allow_html=True)
    
    # plot a horizontal line of color #1C354C
    st.markdown("<hr style='border: 1px solid #1C354C;'>", unsafe_allow_html=True)
    
    df_restaurant = df_filtered[df_filtered["restaurant"] == rest_name]
    chart = alt.Chart(df_restaurant).mark_bar().encode(
        x=alt.X('value:Q', scale=alt.Scale(domain=[-2.5, 2.5]), axis=None),
        y=alt.Y('category:N', axis=alt.Axis(title="Category Ratings")),
        color=alt.condition(alt.datum.value > 0, alt.value("#4C331C"), alt.value("#1C354C"))
    ).properties(height=250)
    # add a vertical line at 0
    chart = chart + alt.Chart(pd.DataFrame({'x': [0]})).mark_rule(color="#4C331C").encode(x='x:Q')
    chart = chart.configure_axisLeft(
        labelColor='#1C354C',
        titleColor='#1C354C'
    )
    
    st.altair_chart(chart, use_container_width=True)
    
