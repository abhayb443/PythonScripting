from PIL import Image
import imagehash
import os
import redis
import pickle


def redis_get(img1hash, img2hash):
    try:
        r = redis.StrictRedis(host='redis-14143.c240.us-east-1-3.ec2.cloud.redislabs.com', port=14143, password='87Isk94dtapaSj9rBvoqQ2Yg08BOJOKf')
        dict_ = '{}_{}'.format(img1hash, img2hash)
        res = {}

        if r.exists(dict_):
            res[True] = r.lrange(dict_, 0, 2)
            return res
        else:
            res[False] = 'Image hash does not exist..'
            return res

    except Exception as e:
        print(type(e).__name__, __file__, e.__traceback__.tb_lineno)


def redis_post(img1hash, img2hash, resp):
    try:
        r = redis.StrictRedis(host='redis-14143.c240.us-east-1-3.ec2.cloud.redislabs.com', port=14143, password='87Isk94dtapaSj9rBvoqQ2Yg08BOJOKf')
        dict_ = '{}_{}'.format(img1hash, img2hash)
        r.lpush(dict_, str(img1hash))
        r.lpush(dict_, str(img2hash))
        r.lpush(dict_, resp)

        res = r.lrange(dict_, 0, 2)
        print(res)
        r.flushdb()

    except Exception as e:
        print(type(e).__name__, __file__, e.__traceback__.tb_lineno)


if __name__ == '__main__':
    File_dir = os.path.dirname(__file__)

    image1 = os.path.join(File_dir, 'figures/ab_selfie.jpeg')
    image2 = os.path.join(File_dir, 'figures/aadhaar_front.jpg')
    image3 = os.path.join(File_dir, 'figures/cropped.png')
    image4 = os.path.join(File_dir, 'figures/cropped-1.png')
    image5 = os.path.join(File_dir, 'figures/cropped-2.jpg')
    image6 = os.path.join(File_dir, 'figures/cropped-4-en.jpg')

    hash = imagehash.average_hash(Image.open(image1))
    otherhash = imagehash.average_hash(Image.open(image2))

    response = '{"ok": Succeeded}'
    redis_post(hash, otherhash, response)

    thirdhash = imagehash.average_hash(Image.open(image3))
    fourthhash = imagehash.average_hash(Image.open(image4))

    redis_post(thirdhash, fourthhash, response)

    fifthhash = imagehash.average_hash(Image.open(image5))
    Sixthhash = imagehash.average_hash(Image.open(image6))

    print(redis_get(hash, otherhash))
    print(redis_get(fifthhash, Sixthhash))
