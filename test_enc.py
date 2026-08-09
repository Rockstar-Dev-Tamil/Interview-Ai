import json
from langchain_core.messages import AIMessage

class StateEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'dict'):
            return obj.dict()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

msg = AIMessage(content='hello', additional_kwargs={'tool_calls': [{'id': '1'}]})
print(json.dumps({'msg': msg}, cls=StateEncoder))
