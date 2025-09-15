import numpy as np
import pickle
import os
from sentence_encoder import SentenceTransformer
from nlp_transformer import TextTokenizer
import torch

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("警告: FAISS 未安装，将使用简单的暴力搜索")

class VectorIndex:
    """向量索引系统"""
    
    def __init__(self, dimension=256, index_type='flat'):
        self.dimension = dimension
        self.index_type = index_type
        self.vectors = None
        self.texts = None
        self.metadata = None
        self.index = None
        self._build_index()
    
    def _build_index(self):
        """构建向量索引"""
        if FAISS_AVAILABLE:
            if self.index_type == 'flat':
                self.index = faiss.IndexFlatIP(self.dimension)  # 内积相似度
            elif self.index_type == 'ivf':
                quantizer = faiss.IndexFlatIP(self.dimension)
                self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
                self.index.nprobe = 10
            else:
                raise ValueError(f"不支持的索引类型: {self.index_type}")
        else:
            self.index = None
            self.vectors = np.array([]).reshape(0, self.dimension)
    
    def add_vectors(self, vectors, texts, metadata=None):
        """添加向量到索引"""
        vectors = np.array(vectors).astype('float32')
        
        if self.vectors is None:
            self.vectors = vectors
            self.texts = list(texts)
            self.metadata = metadata if metadata else [{}] * len(texts)
        else:
            self.vectors = np.vstack([self.vectors, vectors])
            self.texts.extend(texts)
            if metadata:
                self.metadata.extend(metadata)
            else:
                self.metadata.extend([{}] * len(texts))
        
        if FAISS_AVAILABLE and self.index is not None:
            if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                self.index.train(vectors)
            self.index.add(vectors)
    
    def search(self, query_vector, k=5, threshold=0.6):
        """搜索相似向量"""
        query_vector = np.array(query_vector).astype('float32').reshape(1, -1)
        
        if FAISS_AVAILABLE and self.index is not None:
            # 使用FAISS搜索
            distances, indices = self.index.search(query_vector, k)
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.texts) and distance >= threshold:
                    results.append({
                        'text': self.texts[idx],
                        'score': float(distance),
                        'index': int(idx),
                        'metadata': self.metadata[idx] if self.metadata else {}
                    })
            return results
        else:
            # 暴力搜索
            if self.vectors is None or self.vectors.size == 0:
                return []
            
            # 计算余弦相似度
            similarities = np.dot(self.vectors, query_vector.T).flatten()
            vector_norms = np.linalg.norm(self.vectors, axis=1)
            query_norm = np.linalg.norm(query_vector)
            norms = vector_norms * query_norm
            similarities = similarities / np.clip(norms, 1e-8, None)
            
            # 获取top-k结果
            indices = np.argsort(similarities)[::-1][:k]
            results = []
            for idx in indices:
                if similarities[idx] >= threshold and self.texts is not None and idx < len(self.texts):
                    result_item = {
                        'text': self.texts[idx],
                        'score': float(similarities[idx]),
                        'index': int(idx),
                    }
                    # 安全地添加metadata
                    if self.metadata is not None and idx < len(self.metadata):
                        result_item['metadata'] = self.metadata[idx]
                    else:
                        result_item['metadata'] = {}
                    results.append(result_item)
            return results
    
    def batch_search(self, query_vectors, k=5, threshold=0.6):
        """批量搜索"""
        results = []
        for query_vector in query_vectors:
            results.append(self.search(query_vector, k, threshold))
        return results
    
    def save(self, filepath):
        """保存索引到文件"""
        data = {
            'vectors': self.vectors,
            'texts': self.texts,
            'metadata': self.metadata,
            'dimension': self.dimension,
            'index_type': self.index_type
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"索引已保存到: {filepath}")
    
    def load(self, filepath):
        """从文件加载索引"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"索引文件不存在: {filepath}")
        
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        self.vectors = data['vectors']
        self.texts = data['texts']
        self.metadata = data['metadata']
        self.dimension = data['dimension']
        self.index_type = data['index_type']
        
        # 重新构建索引
        self._build_index()
        if FAISS_AVAILABLE and self.index is not None and len(self.vectors) > 0:
            self.index.add(self.vectors.astype('float32'))
        
        print(f"索引已从 {filepath} 加载，包含 {len(self.texts)} 个文档")

class SemanticSearchEngine:
    """语义搜索引擎"""
    
    def __init__(self, model_checkpoint=None, tokenizer=None, index_path=None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.tokenizer = tokenizer
        self.index = VectorIndex()
        
        if model_checkpoint:
            self.load_model(model_checkpoint)
        
        if index_path and os.path.exists(index_path):
            self.load_index(index_path)
    
    def load_model(self, checkpoint_path):
        """加载训练好的模型"""
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"模型文件不存在: {checkpoint_path}")
        
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        # 创建模型
        self.model = SentenceTransformer(
            vocab_size=checkpoint['vocab_size'],
            d_model=checkpoint['model_config']['d_model'],
            nhead=checkpoint['model_config']['nhead'],
            num_layers=checkpoint['model_config']['num_layers'],
            dim_feedforward=checkpoint['model_config']['dim_feedforward'],
            dropout=checkpoint['model_config']['dropout'],
            max_seq_length=checkpoint['model_config']['max_seq_length'],
            pooling_strategy=checkpoint['model_config']['pooling_strategy']
        )
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model = self.model.to(self.device)
        self.model.eval()
        
        self.tokenizer = checkpoint['tokenizer']
        print(f"模型已加载: {checkpoint_path}")
    
    def encode_text(self, text):
        """编码文本为向量"""
        if self.model is None or self.tokenizer is None:
            raise ValueError("模型或分词器未加载")
        
        with torch.no_grad():
            token_ids = self.tokenizer.encode(text)
            input_ids = torch.LongTensor([token_ids]).to(self.device)
            vector = self.model(input_ids)
            return vector.cpu().numpy()[0]
    
    def build_index_from_texts(self, texts, metadata=None, batch_size=32):
        """从文本构建索引"""
        if self.model is None or self.tokenizer is None:
            raise ValueError("模型或分词器未加载")
        
        print(f"开始构建索引，共 {len(texts)} 个文档...")
        
        # 批量编码文本
        vectors = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_vectors = self.model.encode(batch_texts, self.tokenizer, batch_size, str(self.device))
            vectors.append(batch_vectors)
        
        vectors = np.vstack(vectors)
        
        # 添加到索引
        self.index.add_vectors(vectors, texts, metadata)
        print(f"索引构建完成，共 {len(texts)} 个文档")
    
    def search(self, query, k=5, threshold=0.6):
        """语义搜索"""
        query_vector = self.encode_text(query)
        results = self.index.search(query_vector, k, threshold)
        return results
    
    def save_index(self, filepath):
        """保存索引"""
        self.index.save(filepath)
    
    def load_index(self, filepath):
        """加载索引"""
        self.index.load(filepath)

def demonstrate_semantic_search():
    """演示语义搜索"""
    print("语义搜索引擎演示")
    print("=" * 50)
    
    # 创建示例文档库
    documents = [
        "机器学习是人工智能的重要分支",
        "深度学习需要大量的训练数据",
        "自然语言处理让计算机理解人类语言",
        "Transformer模型在NLP领域很流行",
        "Python是数据科学的首选语言",
        "神经网络模仿人脑的工作方式",
        "数据预处理是机器学习的关键步骤",
        "模型评估需要合适的 metrics",
        "特征工程能提升模型性能",
        "梯度下降是常用的优化算法"
    ]
    
    # 创建搜索引擎
    search_engine = SemanticSearchEngine()
    
    # 使用简单模型进行演示（实际应该使用训练好的模型）
    from nlp_transformer import TextTokenizer
    tokenizer = TextTokenizer(vocab_size=1000)
    tokenizer.build_vocab(documents)
    
    # 创建简单模型
    model = SentenceTransformer(
        vocab_size=len(tokenizer.vocab),
        d_model=128,
        nhead=4,
        num_layers=2,
        pooling_strategy='mean'
    )
    model.eval()
    
    search_engine.model = model
    search_engine.tokenizer = tokenizer
    
    # 构建索引
    search_engine.build_index_from_texts(documents)
    
    # 测试搜索
    test_queries = [
        "人工智能",
        "数据科学",
        "神经网络",
        "编程语言"
    ]
    
    print("\n搜索演示:")
    for query in test_queries:
        print(f"\n查询: '{query}'")
        results = search_engine.search(query, k=3)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['text']} (相似度: {result['score']:.4f})")
    
    # 保存索引
    search_engine.save_index('semantic_index.pkl')
    print(f"\n索引已保存到: semantic_index.pkl")

if __name__ == "__main__":
    demonstrate_semantic_search()
