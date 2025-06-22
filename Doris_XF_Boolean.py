import csv
import time
from collections import defaultdict
from Doris_XF import EDB, PARAMS, search
from Doris_XF_new import search_union_no_overlap_encrypted

# === Step 0: 输入文件路径 ===
TAG_FILE = 'test_inverted0.csv'      # 原始输入
FINAL_WID = 'wid.csv'
FINAL_IDW = 'idw.csv'

def parse_input_file(path):
    d_to_tags = defaultdict(list)
    tag_to_docs = defaultdict(list)
    with open(path, 'r', encoding='latin1') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 3:
                continue
            D, tag, *docs = row
            d_to_tags[D.strip()].append(tag.strip())
            tag_to_docs[tag.strip()] = [x.strip() for x in docs if x.strip()]
    return d_to_tags, tag_to_docs

def get_docids_for_D(d_to_tags):
    d_to_docids = {}
    for D, tags in d_to_tags.items():
        print(f"\n🔍 并集查询 D={D}, tags={tags}")
        t0 = time.time()
        keys = PARAMS()
        edb = EDB(2000, 2)
        msk = edb.setup('wid.csv', 'idw.csv', keys)
        res = search_union_no_overlap_encrypted(msk, tags, edb, keys)
        decoded = [r.decode() for r in res]
        t1 = time.time()
        print(f"✅ 得到文档编号: {decoded}")
        print(f"⏰ 并集耗时: {t1 - t0:.3f} 秒")
        d_to_docids[D] = decoded
    return d_to_docids

def save_wid_idw_from_d_map(d_to_docs):
    with open(FINAL_WID, 'w', newline='') as wf:
        writer = csv.writer(wf)
        for D, docs in d_to_docs.items():
            writer.writerow([D] + docs)

    doc_to_ds = defaultdict(list)
    for D, docs in d_to_docs.items():
        for doc in docs:
            doc_to_ds[doc].append(D)

    with open(FINAL_IDW, 'w', newline='') as wf:
        writer = csv.writer(wf)
        for doc, Ds in doc_to_ds.items():
            writer.writerow([doc] + Ds)

def run_final_intersection(D_list):
    print(f"\n🚀 执行最终交集查询: {D_list}")
    t0 = time.time()
    keys = PARAMS()
    edb = EDB(2000, 2)
    msk = edb.setup(FINAL_WID, FINAL_IDW, keys)
    result = search(msk, D_list, edb, keys)
    t1 = time.time()
    decoded = [x.decode() for x in result]
    print(f"✅ 交集查询完成，耗时: {t1 - t0:.3f} 秒")
    print(f"🎯 最终交集结果文档编号：{decoded}")
    return decoded

if __name__ == "__main__":
    d_to_tags, _ = parse_input_file(TAG_FILE)
    d_to_docids = get_docids_for_D(d_to_tags)
    save_wid_idw_from_d_map(d_to_docids)
    run_final_intersection(list(d_to_docids.keys()))

