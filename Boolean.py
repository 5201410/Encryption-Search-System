import csv
import time
import sys
import os
from Utils.TSet import cal_size
from collections import defaultdict
from Conjunctive import EDB, PARAMS, search
from Disjunctive import search_union_no_overlap_encrypted
import logging, pickle


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('boolean_query.log')
    ]
)


def get_temp_filename(prefix, suffix):
    timestamp = int(time.time())
    return f"{prefix}_{timestamp}{suffix}"


def parse_and_generate_initial_index(path):
    """解析布尔结构文件，生成初始索引文件"""
    tag_to_docs = defaultdict(list)
    d_to_tags = defaultdict(list)
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 3:
                continue
            D, tag, *docs = row
            d_to_tags[D.strip()].append(tag.strip())
            tag_to_docs[tag.strip()].extend([d.strip() for d in docs if d.strip()])

    
    INITIAL_WID = get_temp_filename("initial_wid", ".csv")
    INITIAL_IDW = get_temp_filename("initial_idw", ".csv")
    

    with open(INITIAL_WID, 'w', newline='', encoding='utf-8') as wf:
        writer = csv.writer(wf)
        for tag, docs in tag_to_docs.items():
            writer.writerow([tag] + list(set(docs)))


    doc_to_tags = defaultdict(list)
    for tag, docs in tag_to_docs.items():
        for doc in set(docs):
            doc_to_tags[doc].append(tag)
    with open(INITIAL_IDW, 'w', newline='', encoding='utf-8') as wf:
        writer = csv.writer(wf)
        for doc, tags in doc_to_tags.items():
            writer.writerow([doc] + tags)

    return d_to_tags, INITIAL_WID, INITIAL_IDW


def get_docids_for_D(d_to_tags, keys, edb, msk, D_list):
    """为每个D_i执行并集查询，获取对应的文档ID集合"""
    d_to_docids = {}
    for D in D_list:
        if D not in d_to_tags:
            logging.warning(f"⚠️ 指定的D_i '{D}' 不在输入文件中，跳过")
            continue
            
        tags = d_to_tags[D]
        logging.info(f"\n🔍 并集查询 D={D}, tags={tags}")
        t0 = time.time()
        res = search_union_no_overlap_encrypted(msk, tags, edb, keys)
        decoded = [r.decode() for r in res]
        t1 = time.time()
        logging.info(f"✅ 得到文档编号: {decoded}")
        logging.info(f"⏰ 并集耗时: {t1 - t0:.3f} 秒")
        d_to_docids[D] = decoded
    return d_to_docids


def save_wid_idw_from_d_map(d_to_docs):
    """将D_i与文档ID的对应关系保存为新的索引文件"""
    # 生成唯一的临时文件名
    FINAL_WID = get_temp_filename("final_wid", ".csv")
    FINAL_IDW = get_temp_filename("final_idw", ".csv")
    
    with open(FINAL_WID, 'w', newline='', encoding='utf-8') as wf:
        writer = csv.writer(wf)
        for D, docs in d_to_docs.items():
            writer.writerow([D] + docs)

    doc_to_ds = defaultdict(list)
    for D, docs in d_to_docs.items():
        for doc in docs:
            doc_to_ds[doc].append(D)

    with open(FINAL_IDW, 'w', newline='', encoding='utf-8') as wf:
        writer = csv.writer(wf)
        for doc, Ds in doc_to_ds.items():
            writer.writerow([doc] + Ds)
            
    return FINAL_WID, FINAL_IDW


def run_final_intersection(D_list, keys, edb, msk):
    """对指定的D_i列表执行交集查询，返回同时包含这些D_i的文档ID"""
    if not D_list:
        logging.warning("⚠️ 没有指定D_i列表，交集查询中止")
        return []
    logging.info(f"\n🚀 执行最终交集查询: {D_list}")
    t0 = time.time()
    result = search(msk, D_list, edb, keys)
    t1 = time.time()
    decoded = [x.decode() for x in result]
    logging.info(f"✅ 交集查询完成，耗时: {t1 - t0:.6f} 秒")
    logging.info(f"🎯 最终交集结果文档编号：{decoded}")
    return decoded


if __name__ == "__main__":
    try:
   
        if len(sys.argv) < 4:
            print("用法: python Boolean.py <query_structure_file> <inverted_index_file> <query_file>")
            print("示例: python Boolean.py query_structure.csv inverted_index.csv query.txt")
            sys.exit(1)
        
  
        query_structure_file = sys.argv[1]
        inverted_index_file = sys.argv[2]
        query_file = sys.argv[3]
        
      
        if not os.path.exists(query_structure_file):
            raise FileNotFoundError(f"查询结构文件不存在: {query_structure_file}")
        if not os.path.exists(inverted_index_file):
            raise FileNotFoundError(f"倒排索引文件不存在: {inverted_index_file}")
        if not os.path.exists(query_file):
            raise FileNotFoundError(f"查询文件不存在: {query_file}")

       
        with open(query_file, 'r', encoding='utf-8') as f:
            d_list = [line.strip() for line in f if line.strip()]
        
        
        print("📖 解析布尔结构文件并生成初始索引...")
        d_to_tags, INITIAL_WID, INITIAL_IDW = parse_and_generate_initial_index(query_structure_file)
        
       
        print("📦 初始化加密数据库...")
        keys = PARAMS()
        edb = EDB(5000000, 3)
        msk = edb.setup(INITIAL_WID, INITIAL_IDW, keys)
        
       
        print("\n📊 计算指定D_i的文档ID并集...")
        d_to_docids = get_docids_for_D(d_to_tags, keys, edb, msk, d_list)
        
      
        print("\n💾 基于并集结果生成新的索引文件...")
        FINAL_WID, FINAL_IDW = save_wid_idw_from_d_map(d_to_docids)
        
     
        print("📥 更新加密数据库为新索引...")
        msk = edb.setup(FINAL_WID, FINAL_IDW, keys)
        
      
        print(f"\n🌟 开始交集查询，目标D_i列表: {d_list}")
        final_result = run_final_intersection(d_list, keys, edb, msk)
        
      
        print(f"\n🎉 最终查询结果: {final_result}")
        
        tset_size_calc = cal_size(edb.tset)
        print(f"  - TSet 逻辑长度计算: {tset_size_calc / 1024:.2f} KB")

        tset_size_dump = len(pickle.dumps(edb.tset))
        print(f"  - TSet 序列化大小  : {tset_size_dump / 1024:.2f} KB")

        xset_size_calc = len(edb.ct) * 32
        print(f"  - XSet 逻辑长度计算: {xset_size_calc / 1024:.2f} KB")

        xset_size_dump = len(pickle.dumps(edb.ct))
        print(f"  - XSet 序列化大小  : {xset_size_dump / 1024:.2f} KB")
        
        
        for file in [INITIAL_WID, INITIAL_IDW, FINAL_WID, FINAL_IDW]:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                print(f"⚠️ 删除临时文件 {file} 失败: {e}")
        
    except FileNotFoundError as e:
        print(f"❌ 文件未找到: {e}")
    except KeyError as e:
        print(f"❌ 指定的D_i {e} 不在输入文件中")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
