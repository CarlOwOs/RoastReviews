import cohere
import json
import numpy as np
import subprocess
import ast
import time

if __name__ == "__main__":
    # res = subprocess.run("co key create hack", shell=True, capture_output=True) 
    # key = res.stdout.decode().strip("\n")
    key = "w4G2aPmfzrV9m9MVulXp98hvqRDXLacPPCBS1d97"
    co = cohere.Client(key)
    
    url_business = "data/yelp_dataset/yelp_academic_dataset_business.json"
    url_review = 'data/yelp_dataset/yelp_academic_dataset_review.json'
    
    with open(url_business) as f:
        dict_business = [json.loads(line) for line in f.readlines()]

    M = 3
    business_id = []
    for business in dict_business:
        try:
            if 'Coffee & Tea' in business['categories']:
                business_id.append(business['business_id'])
        except:
            pass
    business_id = business_id[:5]
    
    aux = business_id.copy()
    dict_review = {business: [] for business in business_id}
    N = 20 # save the first N reviews for each business
    with open(url_review) as f:
        for line in f.readlines():
            review = json.loads(line)
            if review['business_id'] in aux:
                dict_review[review["business_id"]].append(review)
                if len (dict_review[review["business_id"]]) == N:
                    aux = [business for business in aux if business != review['business_id']]
                if len(aux) == 0:
                    break
                
    categories = ["studying", "atmosphere", "music", "wifi", "price", "staff", "food", "coffee"]
    dict_responses = {business: {category: [] for category in categories} for business in business_id}
    
    prompt_template = f"""Based on the following restaurant review, what does the user think about the following categories: {categories}. The options for the sentiments are "very good", good", "neutral", "bad", "very bad". Give output in a json where the keys are the categories and the values the sentiment."""

    i = 0
    for business in business_id:
        for review in dict_review[business]:
            prompt =f"{prompt_template} \nReview: {review['text']}"
            response = co.generate(
                prompt=prompt,
                model="command-xlarge-nightly",
                max_tokens=100,
            )
            i += 1
            if i == 5:
                i = 0
                print("sleeping...")
                time.sleep(60)
            try:
                response_dict = ast.literal_eval(response[0])

                cat_val = {"very bad": 1, "bad": 2, "neutral": 3, "good": 4, "very good": 5}
                response_dict = {category: cat_val[response_dict[category]] for category in response_dict}

                for category in response_dict:
                    if response_dict[category] != 3:
                        dict_responses[business][category].append(response_dict[category])
            except:
                print(response[0])
                pass
    
    for business in dict_responses:
        for category in dict_responses[business]:
            dict_responses[business][category] = np.mean(dict_responses[business][category])
    
    print("tag values:", dict_responses)
    
    # save result_json in data/review_summary.json
    with open("data/review_summary_.json", "w") as f:
        json.dump(dict_responses, f)
    
    
    