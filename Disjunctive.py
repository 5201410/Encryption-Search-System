from Utils.cryptoUtils import prf, AES_enc, AES_dec
from Utils.TSet import TSet, genStag, cal_size
from Utils.SSPE_XF import SSPE_XF
from Utils.fileUtils import read_index
from dataclasses import dataclass
from Crypto.Random import get_random_bytes
import logging
import os, sys, time, pickle

logging.basicConfig(filename='debug_log.txt', level=logging.DEBUG, format='%(asctime)s - %(message)s')

@dataclass
class PARAMS:
    ke: bytes = get_random_bytes(16)
    kx: bytes = get_random_bytes(16)
    kt: bytes = None

sspe = SSPE_XF()

class EDB:
    def __init__(self, n, k):
        self.tset = TSet(n, k)
        self.ct = None  

    def setup(self, fpath_wid, fpath_idw, keys: PARAMS):
        t0 = time.time()
        dct_wid = read_index(fpath_wid)
        dct_idw = read_index(fpath_idw)
        T = {}
        xset = set()

        for w, ids in dct_wid.items():
            t = []
            i = 1
            kw = prf(keys.ke, w)
            for id in ids:
                e = AES_enc(kw, id)
                ws = dct_idw[id].copy()
                if w in ws:
                    ws.remove(w)
                for w_tmp in ws:
                    xtag = prf(keys.kx, w + w_tmp + str(i))
                    xset.add(xtag)
                t.append(e)
                i += 1
            T[w] = t

        keys.kt = self.tset.setup(T)
        msk_bf = sspe.setup(len(xset))
        sspe.enc(msk_bf, xset)
        self.ct = msk_bf.xf
        print("edb setup:", time.time() - t0, "s")
        return msk_bf.msk

def search_union_no_overlap_encrypted(msk, ws, edb, keys):
    final_res = set()
    num_tags = len(ws)

    for i in range(num_tags):
        wi = ws[i]
    
        stag_t0 = time.time()
        stag = genStag(keys.kt, wi)
        print(f"gen stag for {wi}:", time.time() - stag_t0, "s")

       
        retrive_t0 = time.time()
        e_list = edb.tset.retrive(stag)
        print(f"retrive stag for {wi}:", time.time() - retrive_t0, "s")
        current_docids = set(e_list)

       
        inter_docids = set()
        for j in range(i+1, num_tags):
            wj = ws[j]
            xtoken_t0 = time.time()
            tmp_inter = set()
            for idx, e in enumerate(e_list):
                qtag = prf(keys.kx, wi + wj + str(idx+1))
                xtoken = sspe.keyGen(msk, [qtag])
                if sspe.dec(xtoken, edb.ct):
                    tmp_inter.add(e)
            inter_docids.update(tmp_inter)
            print(f"gen xtoken for {wi} ∧ {wj}:", time.time() - xtoken_t0, "s")

       
        current_docids -= inter_docids
        final_res.update(current_docids)

  
    last_tag = ws[-1]
    last_t0 = time.time()
    stag = genStag(keys.kt, last_tag)
    e_list = edb.tset.retrive(stag)
    final_res.update(e_list)

    start_es = time.time()
    xtokens = []
    for idx in range(len(e_list)):
        qtag = prf(keys.kx, last_tag + last_tag + str(idx+1))
        xtokens.append(qtag)
    xtoken = sspe.keyGen(msk, xtokens)
    es = sspe.dec(xtoken, edb.ct)
    print(f"get es: {time.time() - start_es} s")

  
    dec_t0 = time.time()
    all_res = set()
    for e in final_res:
        for w in ws:
            ke = prf(keys.ke, w)
            try:
                ind = AES_dec(ke, e)
                all_res.add(ind)
                break
            except:
                continue
    print(f"dec to get res: {time.time() - dec_t0} s")
    return list(all_res)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 Doris_XF_new.py <index_file> <inverted_file> <keyword1> <keyword2> ...")
        sys.exit(1)

    f_idw, f_wid, ws = sys.argv[1], sys.argv[2], sys.argv[3:]

    if not os.path.exists(f_idw) or not os.path.exists(f_wid):
        print("❌ 文件路径无效")
        sys.exit(1)

    keys = PARAMS()
    edb = EDB(5000000, 3)
    setup_start = time.time()
    msk = edb.setup(f_wid, f_idw, keys)
    print("total setup time:", time.time() - setup_start, "s")
    
    tset_size_calc = cal_size(edb.tset)
    print(f"tset size (cal length): {tset_size_calc / 1024:.2f} KB")
    tset_size_dump = len(pickle.dumps(edb.tset))
    print(f"tset size (dump)      : {tset_size_dump / 1024:.2f} KB")
    xset_size_calc = len(edb.ct) * 32
    print(f"xset size (cal length): {xset_size_calc / 1024:.2f} KB")
    xset_size_dump = len(pickle.dumps(edb.ct))
    print(f"xset size (dump)      : {xset_size_dump / 1024:.2f} KB")

    res = search_union_no_overlap_encrypted(msk, ws, edb, keys)
    print(f"✅ 查询完成，无重复文档编号（解密后）: {[x.decode() for x in res]}")

