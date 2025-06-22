# --- Doris 基础依赖模块 ---
from Utils.cryptoUtils import prf, AES_enc, AES_dec
from Utils.TSet import TSet, genStag
from Utils.SSPE_XF import SSPE_XF
from Utils.fileUtils import read_index
from dataclasses import dataclass
from Crypto.Random import get_random_bytes
import logging
import os, sys, time

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
        self.ct = None  # 加密交集过滤器

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
        # 1️⃣ 生成 stag
        stag_t0 = time.time()
        stag = genStag(keys.kt, wi)
        print(f"gen stag for {wi}:", time.time() - stag_t0, "s")

        # 2️⃣ 从 tset 检索密文编号
        retrive_t0 = time.time()
        e_list = edb.tset.retrive(stag)
        print(f"retrive stag for {wi}:", time.time() - retrive_t0, "s")
        current_docids = set(e_list)

        # 3️⃣ 计算交集（每个 wi 与后续 wj 两两做）
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
            print(f"gen xtoken for {wi} & {wj}:", time.time() - xtoken_t0, "s")

        # 4️⃣ 差集处理
        current_docids -= inter_docids
        final_res.update(current_docids)

    # 5️⃣ 最后一个标签的全部密文编号直接加入
    last_tag = ws[-1]
    last_t0 = time.time()
    stag = genStag(keys.kt, last_tag)
    e_list = edb.tset.retrive(stag)
    final_res.update(e_list)


    # 6️⃣ 解密最终结果
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
    print("dec to get res:", time.time() - dec_t0, "s")
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
    edb = EDB(2000, 2)
    setup_start = time.time()
    msk = edb.setup(f_wid, f_idw, keys)
    print("total setup time:", time.time() - setup_start, "s")

    query_start = time.time()
    res = search_union_no_overlap_encrypted(msk, ws, edb, keys)
    print("total query time:", time.time() - query_start, "s")
    print(f"✅ 查询完成，无重复文档编号（解密后）: {[x.decode() for x in res]}")

