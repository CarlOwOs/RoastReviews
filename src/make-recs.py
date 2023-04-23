import cohere
import json
import numpy as np
import subprocess
import ast
import time

if __name__ == "__main__":
    key = "w4G2aPmfzrV9m9MVulXp98hvqRDXLacPPCBS1d97"
    co = cohere.Client(key)
    
    url_business = "yelp_dataset/yelp_academic_dataset_business.json"
    url_review = 'yelp_dataset/yelp_academic_dataset_review.json'
    
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
    N = 5 # save the first N reviews for each business
    with open(url_review) as f:
        for line in f.readlines():
            review = json.loads(line)
            if review['business_id'] in aux:
                dict_review[review["business_id"]].append(review)
                if len (dict_review[review["business_id"]]) == N:
                    aux = [business for business in aux if business != review['business_id']]
                if len(aux) == 0:
                    break
                

    recs = {business: set() for business in business_id}
    
    prompt_template = f"""Based on the following restaurant review, does the user recommend any food or beverages in particular? If they do, say only the product. If not, just say 'no': """

    i = 0
    for business in business_id:
        for review in dict_review[business]:
            prompt =f"{prompt_template} \nReview: {review['text']}"
            response = co.generate(
                prompt=prompt,
                model="command-xlarge-nightly",
                max_tokens=100,
            )
            rec = response[0].strip(' .\n').lower()
            if rec != "no":
                recs[business].add(rec)
            i += 1
            if i == 5:
                i = 0
                print("sleeping...")
                time.sleep(60)

    # convert set recs to list
    recs = {business: list(recs) for business, recs in recs.items()}

    print("recommendations:", recs)

    with open("data/recs.json", "w") as f:
        json.dump(recs, f)
    
    