import requests
import random
import json
from hashlib import md5

def trans(query:str):
    # Set your own appid/appkey.
    appid = "20240106001933058" 
    appkey = "OTbadpRuk_JdzYQ97MEa"

    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    from_lang = 'zh'
    to_lang =  'jp'

    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    # Generate salt and sign
    def make_md5(s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()

    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()

    # Show response
    trans_list = result["trans_result"]
    res = '\n'.join(trans_list[i]["dst"] for i in range(len(trans_list)))
    return res