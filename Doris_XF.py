import logging
import pickle
from Crypto.Random import get_random_bytes
from typing import List
from Utils.cryptoUtils import prf, AES_enc, AES_dec
from Utils.TSet import TSet, cal_size, genStag
from Utils.SSPE_XF import SSPE_XF, MSK
from Utils.fileUtils import read_index
from dataclasses import dataclass
import sys
import os

# 配置日志记录
logging.basicConfig(filename='debug_log.txt', level=logging.DEBUG, format='%(asctime)s - %(message)s')


@dataclass
class PARAMS:
    ke: bytes = get_random_bytes(16)
    kx: bytes = get_random_bytes(16)
    kt: bytes = None

sspe = SSPE_XF()

class EDB:
    def __init__(self, n: int, k: int) -> None:
        self.tset = TSet(n, k)
        self.ct = None  # sspe

    def setup(self, fpath_wid: str, fpath_idw: str, keys: PARAMS) -> MSK:
        dct_wid = read_index(fpath_wid)
        dct_idw = read_index(fpath_idw)

        T = dict()
        xset = set()

        for w, ids in dct_wid.items():
            t = []
            i = 1
            kw = prf(keys.ke, w)
            for id in ids:
                e = AES_enc(kw, id)
                ws = dct_idw.get(id).copy()
                ws.remove(w)

                for w_tmp in ws:
                    xtag = prf(keys.kx, w + w_tmp + str(i))
                    xset.add(xtag)
                t.append(e)
                i += 1
            T[w] = t

        logging.debug(f"T: {T}")  # Log the data for debugging
        keys.kt = self.tset.setup(T)

        msk_bf = sspe.setup(len(xset))
        sspe.enc(msk_bf, xset)
        self.ct = msk_bf.xf

        logging.debug(f"ct: {self.ct}")  # Log the encrypted data
        return msk_bf.msk

def search(msk: MSK, ws: List[str], edb: EDB, keys: PARAMS) -> List[int]:
    w1 = ws[0]
    ke = prf(keys.ke, w1)
    stag = genStag(keys.kt, w1)
    t = edb.tset.retrive(stag)

    end = []
    for i, e in enumerate(t):
        QSet = []
        for j in range(1, len(ws)):
            qtag = prf(keys.kx, w1 + ws[j] + str(i + 1))
            QSet.append(qtag)

        xtoken = sspe.keyGen(msk, QSet)
        if sspe.dec(xtoken, edb.ct):
            ind = AES_dec(ke, e)
            end.append(ind)

    logging.debug(f"Search result: {end}")  # Log the search results
    return end

def c_gen_stag(ws: List[str], keys: PARAMS):
    return genStag(keys.kt, ws[0])

def s_retrive_stag(tset: TSet, stag: bytes):
    return tset.retrive(stag)

def c_gen_xtoken(msk: MSK, t_len: int, ws: List[str], keys: PARAMS):
    xtoken = []
    w1 = ws[0]
    for i in range(t_len):
        QSet = []
        for j in range(1, len(ws)):
            qtag = prf(keys.kx, w1 + ws[j] + str(i + 1))
            QSet.append(qtag)
        key = sspe.keyGen(msk, QSet)
        xtoken.append(key)

    logging.debug(f"Generated xtoken: {xtoken}")  # Log generated xtoken
    return xtoken

def s_get_es(xtoken, t, ct) -> List[bytes]:
    es = []
    for i, e in enumerate(t):
        s = xtoken[i]
        if sspe.dec(s, ct):
            es.append(e)
    logging.debug(f"Retrieved encrypted data: {es}")  # Log the encrypted data
    return es

def c_decrypt_e(es: List[bytes], ws: List[str], keys: PARAMS):
    ke = prf(keys.ke, ws[0])
    res = [AES_dec(ke, e) for e in es]
    logging.debug(f"Decrypted results: {res}")  # Log the decrypted result
    return res

if __name__ == "__main__":
    from time import time

    if len(sys.argv) < 3:
        print("Usage: python3 Doris_XF.py <index_file> <inverted_file> <keyword1> <keyword2> ...")
        sys.exit(1)

    f_idw = sys.argv[1]
    f_wid = sys.argv[2]
    ws = sys.argv[3:]

    if not os.path.exists(f_idw) or not os.path.exists(f_wid):
        print("❌ 文件路径无效")
        sys.exit(1)

    # 设置较大的空间参数，避免溢出
    n = 2000
    k = 2

    start = time()
    keys = PARAMS()
    edb = EDB(n, k)
    msk = edb.setup(f_wid, f_idw, keys)
    end = time()
    print(f"edb setup: {end-start} s")

    inds = search(msk, ws, edb, keys)
    print(f"res:{inds}")

    start = time()
    stag = c_gen_stag(ws, keys)
    end = time()
    print(f"gen stag: {end-start} s")

    start = time()
    t = s_retrive_stag(edb.tset, stag)
    end = time()
    print(f"retrive stag: {end-start} s")

    start = time()
    xtoken = c_gen_xtoken(msk, len(t), ws, keys)
    end = time()
    print(f"gen xtoken: {end-start} s")

    start = time()
    es = s_get_es(xtoken, t, edb.ct)
    end = time()
    print(f"get es: {end-start} s")

    start = time()
    res = c_decrypt_e(es, ws, keys)
    end = time()
    print(f"dec to get res: {end-start} s")
    print(f"res:{res}")
    print(f"文档编号： {[x.decode() for x in res]}")


