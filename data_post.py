import os
import redis
import pickle
from flask import Flask, request, jsonify
import json


app = Flask(__name__)


@app.route('/', methods=['GET'])
def redis_get():
    try:
        r = redis.StrictRedis(host='redis-14143.c240.us-east-1-3.ec2.cloud.redislabs.com', port=14143, password='87Isk94dtapaSj9rBvoqQ2Yg08BOJOKf')
        res = {}
        result = []
        if r.exists('Json'):
            temp = r.smembers('Json')
            for i in temp:
                i = str(i).strip().replace("\'", "").replace("b'", "'").replace('\"', '').replace("\\", '').replace('"b', '"')
                result.append(i)

            print(result)
            res[True] = result
            return res
        else:
            res[False] = 'No Data exist..'
            return res

    except Exception as e:
        print(type(e).__name__, __file__, e.__traceback__.tb_lineno)


@app.route('/', methods=['POST'])
def redis_post():
    try:
        r = redis.StrictRedis(host='redis-14143.c240.us-east-1-3.ec2.cloud.redislabs.com', port=14143, password='87Isk94dtapaSj9rBvoqQ2Yg08BOJOKf')
        # content = request.args.get('data')
        content = request.args.get('data')
        print(content)
        content = content.strip()
        print(content)
        # content = json.dumps(content)
        r.sadd('Json', content)
        return "Data Added Successfully"

    except Exception as e:
        print(type(e).__name__, __file__, e.__traceback__.tb_lineno)


if __name__ == '__main__':
    app.run(debug=True)

