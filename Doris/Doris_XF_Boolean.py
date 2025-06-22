import csv
from collections import defaultdict
from Doris_XF import EDB, PARAMS, search
from Doris_XF_new import search_union_no_overlap_encrypted

# === Step 0: 输入文件路径 ===
TAG_FILE = 'test_inverted0.csv'          # 原始输入（截图样式）
FINAL_WID = 'wid.csv'                 # 最终用于交集的 wid 文件
FINAL_IDW = 'idw.csv'                 # 最终用于交集的 idw 文件

# === Step 1: 读取 D -> 标签, 标签 -> 文档编号 ===
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

# === Step 2: 对每个 D 标签并集，使用 Doris_XF_new 执行加密查询 ===
def get_docids_for_D(d_to_tags):
    d_to_docids = {}
    for D, tags in d_to_tags.items():
        print(f"\n🔍 并集查询 D={D}, tags={tags}")
        keys = PARAMS()
        edb = EDB(2000, 2)
        msk = edb.setup('wid.csv', 'idw.csv', keys)  # 使用你预加密过的数据
        res = search_union_no_overlap_encrypted(msk, tags, edb, keys)
        decoded = [r.decode() for r in res]
        print(f"✅ 得到文档编号: {decoded}")
        d_to_docids[D] = decoded
    return d_to_docids

# === Step 3: 保存并集结果为 D → 文档编号，对应 wid/idw 文件 ===
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

# === Step 4: 使用 Doris 执行最终 D 级别的交集查询 ===
def run_final_intersection(D_list):
    print(f"\n🚀 执行最终交集查询: {D_list}")
    keys = PARAMS()
    edb = EDB(2000, 2)
    msk = edb.setup(FINAL_WID, FINAL_IDW, keys)
    result = search(msk, D_list, edb, keys)
    decoded = [x.decode() for x in result]
    print(f"\n🎯 最终交集结果文档编号：{decoded}")
    return decoded

# === Main Process ===
if __name__ == "__main__":
    d_to_tags, _ = parse_input_file(TAG_FILE)
    d_to_docids = get_docids_for_D(d_to_tags)
    save_wid_idw_from_d_map(d_to_docids)
    run_final_intersection(list(d_to_docids.keys()))

