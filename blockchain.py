from time import time
import datetime
import os
import pickle
import hashlib as hasher
from ipfs import *
from sift import *

UPLOAD_FOLDER = 'uploads'
TMP_FOLDER = 'tmp'
THRESHOLD = 0.88
""" Class for transactions made on the blockchain. Each transaction has a
    sender, recipient, and value.
    """


class Transaction:
    """ Transaction initializer """

    def __init__(self, title="", filename="", author="", img_cid="", kps_cid="", npy_cid=""):
        self.title = title
        self.filename = filename
        self.author = author
        self.img_cid = img_cid
        self.kps_cid = kps_cid
        self.npy_cid = npy_cid
    """ Converts the transaction to a dictionary """

    def toDict(self):
        return {
            'title': self.title,
            'filename': self.filename,
            'author': self.author,
            'img_cid': self.img_cid,
            'kps_cid': self.kps_cid,
            'npy_cid':self.npy_cid
        }

    def __str__(self):
        toString = self.author + f'({self.filename})'
        return toString


""" Class for Blocks. A block is an object that contains transaction information
    on the blockchain.
    """


class Block:
    def __init__(self, index, transaction, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.previous_hash = previous_hash
        self.transaction = transaction

    def compute_hash(self):
        concat_str = str(self.index) + str(self.timestamp) + str(self.previous_hash) + str(
            self.transaction['author']) + str(self.transaction['img_cid'])
        hash_result = hasher.sha256(concat_str.encode('utf-8')).hexdigest()
        return hash_result

    def serialize(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'transaction': self.transaction
        }


""" Blockchain class. The blockchain is the network of blocks containing all the
    transaction data of the system.
    """


class Blockchain:
    def __init__(self):

        self.unconfirmed_transactions = {}
        self.chain = []

    def create_genesis_block(self):
        empty_media = {
            'title': "",
            'filename': "",
            'author': "",
            'img_cid': "",
            'kps_cid': "",
            'npy_cid': ""
        }
        new_block = Block(index=0, transaction=empty_media, previous_hash=0)
        self.add_block(new_block)

        return new_block

    def new_transaction(self, title, filename, author, img_cid, kps_cid, npy_cid):
        new_trans = Transaction(title, filename, author, img_cid, kps_cid, npy_cid).toDict()
        self.unconfirmed_transactions = new_trans.copy()
        return new_trans

    def mine(self):
        # create a block, verify its originality and add to the blockchain
        if (len(self.chain) == 0):
            block_idx = 1
            previous_hash = 0
        else:
            block_idx = self.chain[-1].index + 1
            previous_hash = self.chain[-1].compute_hash()
        block = Block(block_idx, self.unconfirmed_transactions, previous_hash)
        if self.verify_block(block):
            self.add_block(block)
            return block
        else:
            return None

    def verify_block(self, block):
        # verify song originality and previous hash
        # check previous hash

        if len(self.chain) == 0:
            previous_hash = 0
        else:
            previous_hash = self.chain[-1].compute_hash()
        if block.previous_hash != previous_hash:
            return 0
        # downloads
        download_file(block.transaction['filename'] + ".kps.pkl", block.transaction['kps_cid'], TMP_FOLDER)
        download_file(block.transaction['filename'] + ".npy", block.transaction['npy_cid'], TMP_FOLDER)
        for prev_block in self.chain:
            curr_kps = path.join(TMP_FOLDER, block.transaction['filename'] + ".kps.pkl")
            curr_npy = path.join(TMP_FOLDER, block.transaction['filename'] + ".npy")
            if Blockchain.verify(curr_kps, curr_npy, prev_block) is False:
                delete_tmp(curr_kps)
                delete_tmp(curr_npy)
                return False
        return True

    @staticmethod
    def verify(curr_kps, curr_npy, block) -> bool:
        cmp_kps = path.join(TMP_FOLDER, block.transaction['filename'] + ".kps.pkl")
        cmp_npy = path.join(TMP_FOLDER, block.transaction['filename'] + ".npy")
        download_file(block.transaction['filename'] + ".kps.pkl", block.transaction['kps_cid'], TMP_FOLDER)
        download_file(block.transaction['filename'] + ".npy", block.transaction['npy_cid'], TMP_FOLDER)
        key1, des1 = load_kps(curr_kps, curr_npy)
        key2, des2 = load_kps(cmp_kps, cmp_npy)
        sim = calculate_similarity_file(key1, des1, key2, des2)
        delete_tmp(cmp_kps)
        delete_tmp(cmp_npy)
        if sim < THRESHOLD:
            print(sim)
            print("Sim check PASS")
            return True
        else:
            print(sim)
            return False

    def lookup(self, transaction):
        # check originality
        pass

    def add_block(self, block):
        self.chain.append(block)

        with open('./blockchain/chain.pkl', 'wb') as output:
            pickle.dump(self.chain, output, pickle.HIGHEST_PROTOCOL)

    def check_integrity(self):
        return 0

    """ Function that returns the last block on the chain"""

    @property
    def last_block(self):
        return self.chain[-1]
