import json
import yendata

yen = yendata.YenData()
print(json.dumps(yen.get_array()))