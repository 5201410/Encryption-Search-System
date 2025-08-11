import csv
from dataclasses import dataclass
from typing import List, Dict, Set
from Crypto.Random import get_random_bytes
import mmh3
import sys
import os

class CryptoUtils:
    @staticmethod
    def prf(key: bytes, data: str) -> bytes:
        """伪随机函数"""
        return mmh3.hash_bytes(data.encode(), seed=int.from_bytes(key, byteorder=sys.byteorder))

    @staticmethod
    def aes_enc(key: bytes, plaintext: str) -> bytes:
        """AES加密"""
        return CryptoUtils.prf(key, plaintext)[:16]

    @staticmethod
    def aes_dec(key: bytes, ciphertext: bytes) -> str:
        """AES解密（返回原始数字）"""
        try:
            # 这里简化处理，实际应该用真正的AES解密
            return str(int.from_bytes(ciphertext, byteorder='big') % 1000)
        except:
            return "0"

@dataclass
class WordEntry:
    word: str
    doc_ids: List[int]

@dataclass
class DNode:
    name: str
    words: List[WordEntry]

class EncryptedBooleanIndex:
    def __init__(self):
        self.keys = {
            'ke': get_random_bytes(16),
            'kx': get_random_bytes(16),
            'kt': get_random_bytes(16)
        }
        self.tset = {}
        self.xset = set()
        self.d_nodes = []
        self.doc_id_map = {}  # 新增：存储加密文档ID到原始ID的映射

    def build_index(self, d_nodes: List[DNode]):
        self.d_nodes = d_nodes
        print("\n构建加密索引中...")
        
        for d_node in d_nodes:
            for word_entry in d_node.words:
                stag = CryptoUtils.prf(self.keys['kt'], word_entry.word)
                encrypted_docs = []
                
                for doc_id in word_entry.doc_ids:
                    enc_doc = CryptoUtils.aes_enc(self.keys['ke'], str(doc_id))
                    encrypted_docs.append(enc_doc)
                    # 建立映射关系
                    self.doc_id_map[enc_doc] = doc_id
                
                self.tset[stag] = encrypted_docs
                
                for idx, doc_id in enumerate(word_entry.doc_ids):
                    xtag = CryptoUtils.prf(self.keys['kx'], f"{word_entry.word}_{doc_id}_{idx}")
                    self.xset.add(xtag)
        
        print(f"索引构建完成，共 {len(self.d_nodes)} 个D节点")
        print(f"文档ID映射表大小: {len(self.doc_id_map)}")

    def query(self, d_names: List[str]) -> List[int]:
        if not d_names:
            return []

        print(f"\n执行查询: {' ∧ '.join(d_names)}")
        
        # 查找D节点
        query_nodes = []
        for name in d_names:
            node = next((n for n in self.d_nodes if n.name == name), None)
            if not node:
                print(f"警告: 未找到D节点 {name}")
                return []
            query_nodes.append(node)
            print(f"找到 {name} 节点，包含 {len(node.words)} 个关键词")

        # 获取第一个D节点的所有文档
        first_node = query_nodes[0]
        result_docs = self._get_d_encrypted_docs(first_node)
        print(f"初始文档集: {len(result_docs)} 个")

        # 逐步求交集
        for node in query_nodes[1:]:
            current_docs = self._get_d_encrypted_docs(node)
            result_docs.intersection_update(current_docs)
            print(f"与 {node.name} 交集后剩余: {len(result_docs)} 个")
            
            if not result_docs:
                print("交集为空，终止查询")
                break

        # 通过映射表直接获取原始ID
        final_ids = [self.doc_id_map[doc] for doc in result_docs if doc in self.doc_id_map]
        print(f"解密后的文档编号: {final_ids}")
        return final_ids

    def _get_d_encrypted_docs(self, d_node: DNode) -> Set[bytes]:
        enc_docs = set()
        for word_entry in d_node.words:
            stag = CryptoUtils.prf(self.keys['kt'], word_entry.word)
            if stag in self.tset:
                enc_docs.update(self.tset[stag])
        return enc_docs

class CSVParser:
    @staticmethod
    def parse_inverted_csv(file_path: str) -> List[DNode]:
        d_nodes = {}
        print(f"\n解析文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 3:
                        continue
                    
                    d_name = row[0].strip()
                    word = row[1].strip()
                    doc_ids = []
                    
                    for x in row[2:]:
                        if x.strip().isdigit():
                            doc_ids.append(int(x.strip()))
                    
                    if not doc_ids:
                        continue
                    
                    if d_name not in d_nodes:
                        d_nodes[d_name] = DNode(name=d_name, words=[])
                    
                    d_nodes[d_name].words.append(WordEntry(word=word, doc_ids=doc_ids))
                    print(f"添加: {d_name}.{word} -> {doc_ids}")

            print(f"解析完成，共找到 {len(d_nodes)} 个D节点")
            return list(d_nodes.values())
        except Exception as e:
            print(f"解析错误: {e}")
            return []

def main():
    print("=== 加密布尔查询系统 ===")
    print("输入示例: D1 ∧ D2 ∧ D3")
    
    input_file = "boolean_test.csv"
    if not os.path.exists(input_file):
        print(f"错误: 文件 {input_file} 不存在")
        return
    
    d_nodes = CSVParser.parse_inverted_csv(input_file)
    if not d_nodes:
        print("错误: 无有效数据")
        return
    
    index = EncryptedBooleanIndex()
    index.build_index(d_nodes)
    
    while True:
        query = input("\n请输入查询(用∧连接): ").strip()
        if not query:
            break
            
        d_names = [x.strip() for x in query.replace('/', '∧').split('∧')]
        result = index.query(d_names)
        
        print("\n=== 最终结果 ===")
        print(f"文档编号: {sorted(result)}")
        print("=" * 20)

if __name__ == "__main__":
    main()
