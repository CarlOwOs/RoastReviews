import pandas as pd
import ast 
import altair as alt

if __name__ == "__main__":
    json = {'rest1': {'studying': None, 'atmosphere': 4.0, 'music': None, 'wifi': None, 'price': None, 'staff': 4.333333333333333, 'food': 4.0, 'coffee': None}, 'rest2': {'studying': None, 'atmosphere': 3.75, 'music': 1.0, 'wifi': None, 'price': 2.0, 'staff': 4.333333333333333, 'food': 4.333333333333333, 'coffee': 4.333333333333333}, 'rest3': {'studying': 4.0, 'atmosphere': 4.0, 'music': None, 'wifi': 4.0, 'price': None, 'staff': 4.0, 'food': None, 'coffee': 4.0}, 'rest4': {'studying': None, 'atmosphere': 4.0, 'music': None, 'wifi': None, 'price': 4.0, 'staff': 4.5, 'food': 4.666666666666667, 'coffee': None}, 'rest5': {'studying': None, 'atmosphere': 4.0, 'music': None, 'wifi': None, 'price': 4.0, 'staff': 4.333333333333333, 'food': 4.333333333333333, 'coffee': 4.25}}

    for restaurant in json:
        for category in json[restaurant]:
            if json[restaurant][category] != None:
                json[restaurant][category] -= 3
    
    # convert to dataframe with 3 columns: restaurant, category, value
    df = pd.DataFrame(columns=["restaurant", "category", "value"])
    for restaurant in json:
        for category in json[restaurant]:
            df = df._append({"restaurant": restaurant, "category": category, "value": json[restaurant][category]}, ignore_index=True)
    
    # plot an altair chart such that each plot corresponds to a restaurant
    # don't add columns for categories that are NaN
    charts = []
    for restaurant in json:
        df_restaurant = df[df["restaurant"] == restaurant]
        # remove NaN rows
        df_restaurant = df_restaurant.dropna()

        chart = alt.Chart(df_restaurant).mark_bar().encode(
            x=alt.X('value:Q', scale=alt.Scale(domain=[-2.5, 2.5]), axis=None),
            y=alt.Y('category:N'),
            #column='restaurant',
            color=alt.condition(alt.datum.value > 0, alt.value("#2BCC41"), alt.value("#F89A23"))
        ).properties(title=restaurant)
        charts.append(chart)
    chart = alt.vconcat(*charts)
    chart.save("visualization/chart.html")