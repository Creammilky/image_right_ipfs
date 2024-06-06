# author: encoderlee
# https://github.com/encoderlee/eos_demo
import datetime
import eospy.cleos
import eospy.keys
import pytz
import configparser

config = configparser.ConfigParser()
config.read('CONFIG.ini')
consumer_private_key = eospy.keys.EOSKey(config.read("EOS", "key"))

ce = eospy.cleos.Cleos(url=config.read("EOS", "path"), version='v1')


def add_image(imagehash, keypoints, descriptors, author, time):
    print("add image information into EOS...")
    action = {
        "account": 'imageright',
        "name": 'addentry',
        "authorization": [
            {
                "actor": 'imageright',
                "permission": "active",
            },
        ],
        "data": {
            "imagehash": imagehash,
            "keypoints": keypoints,
            "descriptors": descriptors,
            "author": author,
            "time": time
        },
    }
    data = ce.abi_json_to_bin(action['account'], action['name'], action["data"])
    action["data"] = data["binargs"]
    tx = {
        "actions": [action],
        "expiration": str((datetime.datetime.utcnow() + datetime.timedelta(seconds=3000)).replace(tzinfo=pytz.UTC))
    }
    resp = ce.push_transaction(tx, consumer_private_key, timeout=3000)
    print(resp)


def get_entries():
    # 获取区块链上表的内容
    table_data = ce.get_table(code='imageright', scope='imageright', table='entries')
    print("Table data:", table_data)
