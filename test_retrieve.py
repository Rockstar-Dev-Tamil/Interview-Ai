import json
from person2.pipeline import retrieve_question

state = {
    "competency_map": {"1": "Strong", "2": "Weak"},
    "covered_days": [1]
}

q = retrieve_question(state)
print(q)
