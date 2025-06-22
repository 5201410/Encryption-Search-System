import csv
from collections import defaultdict

# 输入原始文件路径（截图结构）
input_csv_path = 'test_inverted0.csv'   # 修改为你的路径
wid_path = 'wid.csv'
idw_path = 'idw.csv'

# 映射结构
tag_to_docs = defaultdict(set)
doc_to_tags = defaultdict(set)

# 尝试使用宽容的 latin1 编码读取
with open(input_csv_path, 'r', encoding='latin1') as f:
    reader = csv.reader(f)
    for row in reader:
        if not row or len(row) < 3:
            continue
        _, tag, *doc_ids = row
        for doc_id in doc_ids:
            tag = tag.strip()
            doc_id = doc_id.strip()
            tag_to_docs[tag].add(doc_id)
            doc_to_tags[doc_id].add(tag)

# 写入 wid.csv（标签 → 文档编号）
with open(wid_path, 'w', newline='') as wf:
    writer = csv.writer(wf)
    for tag, docs in tag_to_docs.items():
        writer.writerow([tag] + sorted(docs))

# 写入 idw.csv（文档编号 → 标签）
with open(idw_path, 'w', newline='') as wf:
    writer = csv.writer(wf)
    for doc_id, tags in doc_to_tags.items():
        writer.writerow([doc_id] + sorted(tags))

print("✅ 转换完成，生成 wid.csv 和 idw.csv")
