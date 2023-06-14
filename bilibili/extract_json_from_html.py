import json
import re
with open('bili.html', 'r', encoding='U8') as f:
    html_text = f.read()

we_need_json = re.search('<script>window.__playinfo__=(.*?)</script>', html_text).group(1)
with open('base_json_from_html.json', 'w+') as f:
    json.dump(json.loads(we_need_json), f, ensure_ascii=False, indent=4)
