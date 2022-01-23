import json
import time

from linkedin_api import Linkedin

from configuration import LINKEDIN_EMAIL, LINKEDIN_PASSWORD

api = Linkedin(LINKEDIN_EMAIL, LINKEDIN_PASSWORD)
print(f'impersonating {LINKEDIN_EMAIL}')

linkedin_people_file = f"data/linkedin/people.json"
try:
    with open(linkedin_people_file) as fd:
        loaded_results = json.load(fd)
        print(f"loaded successfully {len(loaded_results)} profiles")
except:
    pass

results = api.search_people(current_company=["5947"])
print(f"queried linkedin -- and retrieved {len(results)} profiles.. consolidating")

loaded_results_dict = {result.get('public_id'): result for result in loaded_results}
for result in results:
    loaded_results_dict[result.get('public_id')] = result
results = list(loaded_results_dict.values())
print(f"consolidated {len(results)} results")

with open(linkedin_people_file, "w") as fd:
    json.dump(results, fd)


# profiles = ['bellin', 'juleshugot', 'bayarmaa-amarjargal', 'dmitry-kabrelyan-4a194b32', 'akmal-nartayev-cfa-fcca-b734082']
profiles = [result.get("public_id") for result in results]

downloads = 0
for uid in profiles:
    profile_file = f"data/linkedin/{uid}.json"
    try:
        with open(profile_file) as fd:
            profile = json.load(fd)
            print(f'loaded successfully profile {uid}')
    except:
        profile = api.get_profile(uid)
        downloads += 1
        print(f"{downloads} - {uid}")
        with open(profile_file, "w") as fd:
            json.dump(profile, fd)
        time.sleep(2.4)
    if downloads > 100:
        break
