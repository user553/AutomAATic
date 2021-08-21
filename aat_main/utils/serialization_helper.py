from ast import literal_eval
from typing import List


class SerializationHelper:

    @staticmethod
    def model_to_list(models):
        list_data = []
        for model in models:
            dict_data = {}
            for k, v in model.__dict__.items():
                if not k.startswith('_sa_instance_state'):
                    dict_data[k] = v
            list_data.append(dict_data)
        return list_data

    @staticmethod
    def join_model_to_list(join_models):
        list_data = []
        for obj1, obj2 in join_models:
            dict_data = {}
            for k1, v1 in obj1.__dict__.items():
                if not k1.startswith('_sa_instance_state'):
                    if not k1 in dict_data:
                        dict_data[k1] = v1
            for k2, v2 in obj2.__dict__.items():
                if not k2.startswith('_sa_instance_state'):
                    if not k2 in dict_data:
                        dict_data[k2] = v2
            list_data.append(dict_data)
        return list_data

    @staticmethod
    def decode(reviews: List, responses: dict) -> List[dict]:
        """
        This produces a list of the form
        [
            {
                'statement': statement1
                'responses': {
                    'Strongly disagree': x
                    ...
                    'Strongly agree': y
            },
            {
                'statement': statement2
                'responses': {
                    'Strongly disagree': w
                    ...
                    'Strongly agree': z
            }
        ]
        """
        # reference 30 march. https://stackoverflow.com/questions/988228/convert-a-string-representation-of-a-dictionary-to-a-dictionary
        statement_responses = [literal_eval(review.statement_response_map) for review in reviews]
        statement_counts = []
        for statement_response in statement_responses:
            for statement, response in statement_response.items():
                if not any(s['statement'] == statement for s in statement_counts):
                    statement_counts.append({
                        'statement': statement,
                        # 'responses': {r: 1 if r == responses[response] else 0 for r in responses.values()}
                        'responses': {r: 0 for r in responses.values()}
                    })
                for sc in statement_counts:
                    if sc['statement'] == statement:
                        response = responses[response]
                        sc['responses'][response] += 1
        return statement_counts
