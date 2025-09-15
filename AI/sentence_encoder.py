import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from nlp_transformer import TextTokenizer, PositionalEncoding
import numpy as np

class SentenceTransformer(nn.Module):
    """句子编码器 - 将文本转换为向量表示"""
    
    def __init__(self, vocab_size, d_model=512, nhead=8, 
                 num_layers=6, dim_feedforward=2048, dropout=0.1, 
                 max_seq_length=512, pooling_strategy='mean'):
        super(SentenceTransformer, self).__init__()
        
        self.d_model = d_model
        self.vocab_size = vocab_size
        self.max_seq_length = max_seq_length
        self.pooling_strategy = pooling_strategy
        
        # 词嵌入和位置编码
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, max_seq_length)
        
        # Transformer编码器
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # 输出投影层（可选）
        self.projection = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)
        
        # 初始化权重
        self._init_weights()
    
    def _init_weights(self):
        """初始化权重"""
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        if hasattr(self, 'projection'):
            self.projection.bias.data.zero_()
            self.projection.weight.data.uniform_(-initrange, initrange)
    
    def forward(self, src, src_key_padding_mask=None, return_all=False):
        """前向传播"""
        # 嵌入和位置编码
        src_emb = self.embedding(src) * math.sqrt(self.d_model)
        src_emb = self.pos_encoder(src_emb)
        
        # Transformer编码
        hidden_states = self.transformer(src_emb, src_key_padding_mask=src_key_padding_mask)
        
        # 句子向量池化
        sentence_vectors = self.pooling(hidden_states, src_key_padding_mask)
        
        # 投影层
        if hasattr(self, 'projection'):
            sentence_vectors = self.projection(sentence_vectors)
            sentence_vectors = F.relu(sentence_vectors)
            sentence_vectors = self.dropout(sentence_vectors)
        
        # 归一化
        sentence_vectors = F.normalize(sentence_vectors, p=2, dim=1)
        
        if return_all:
            return sentence_vectors, hidden_states
        return sentence_vectors
    
    def pooling(self, hidden_states, attention_mask=None):
        """池化策略生成句子向量"""
        if self.pooling_strategy == 'mean':
            if attention_mask is None:
                return hidden_states.mean(dim=1)
            mask = (~attention_mask).float().unsqueeze(-1)
            return (hidden_states * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-6)
        
        elif self.pooling_strategy == 'cls':
            # 使用第一个token（通常是CLS token）作为句子表示
            return hidden_states[:, 0]
        
        elif self.pooling_strategy == 'max':
            if attention_mask is None:
                return hidden_states.max(dim=1)[0]
            # 对有效token取max
            masked_hidden = hidden_states.clone()
            masked_hidden[attention_mask] = -float('inf')
            return masked_hidden.max(dim=1)[0]
        
        else:
            raise ValueError(f"Unknown pooling strategy: {self.pooling_strategy}")
    
    def encode(self, texts, tokenizer, batch_size=32, device='cpu'):
        """批量编码文本为向量"""
        self.eval()
        all_vectors = []
        
        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i+batch_size]
                
                # 编码文本
                batch_ids = []
                for text in batch_texts:
                    token_ids = tokenizer.encode(text, max_length=self.max_seq_length)
                    batch_ids.append(token_ids)
                
                batch_ids = torch.LongTensor(batch_ids).to(device)
                
                # 获取句子向量
                vectors = self(batch_ids)
                all_vectors.append(vectors.cpu().numpy())
        
        return np.concatenate(all_vectors, axis=0)

class ContrastiveSentenceEncoder(SentenceTransformer):
    """对比学习句子编码器"""
    
    def __init__(self, *args, **kwargs):
        super(ContrastiveSentenceEncoder, self).__init__(*args, **kwargs)
        
    def contrastive_loss(self, embeddings, labels, temperature=0.05):
        """对比学习损失函数"""
        # 计算相似度矩阵
        similarity_matrix = torch.matmul(embeddings, embeddings.T) / temperature
        
        # 创建标签矩阵
        batch_size = embeddings.size(0)
        labels = labels.view(-1, 1)
        label_matrix = (labels == labels.T).float()
        
        # 对角线设为0（自身对比）
        mask = torch.eye(batch_size, dtype=torch.bool, device=embeddings.device)
        label_matrix.masked_fill_(mask, 0)
        similarity_matrix.masked_fill_(mask, -float('inf'))
        
        # 计算InfoNCE损失
        positives = similarity_matrix * label_matrix
        negatives = similarity_matrix * (1 - label_matrix)
        
        # 计算log softmax
        logits = similarity_matrix
        exp_logits = torch.exp(logits)
        log_prob = logits - torch.log(exp_logits.sum(dim=1, keepdim=True))
        
        # 只计算正样本的损失
        loss = - (label_matrix * log_prob).sum(dim=1) / label_matrix.sum(dim=1).clamp(min=1e-6)
        return loss.mean()

def create_semantic_search_model(vocab_size, **kwargs):
    """创建语义搜索模型"""
    return SentenceTransformer(
        vocab_size=vocab_size,
        d_model=kwargs.get('d_model', 256),
        nhead=kwargs.get('nhead', 4),
        num_layers=kwargs.get('num_layers', 2),
        dim_feedforward=kwargs.get('dim_feedforward', 512),
        dropout=kwargs.get('dropout', 0.1),
        max_seq_length=kwargs.get('max_seq_length', 128),
        pooling_strategy=kwargs.get('pooling_strategy', 'mean')
    )

def demonstrate_sentence_encoder():
    """演示句子编码器"""
    print("句子编码器演示")
    print("=" * 50)
    
    # 检查设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    # 创建示例文本数据
    sample_texts = [
        "机器学习是人工智能的一个子集",
        "深度学习需要大量的数据",
        "自然语言处理帮助计算机理解人类语言",
        "Transformer模型彻底改变了NLP领域",
        "Python是AI领域流行的编程语言"
    ]
    
    # 构建词汇表
    tokenizer = TextTokenizer(vocab_size=1000)
    tokenizer.build_vocab(sample_texts)
    vocab_size = len(tokenizer.vocab)
    
    # 创建句子编码器
    model = create_semantic_search_model(
        vocab_size=vocab_size,
        d_model=128,
        nhead=4,
        num_layers=2,
        pooling_strategy='mean'
    )
    model = model.to(device)
    
    print(f"词汇表大小: {vocab_size}")
    print(f"模型参数量: {sum(p.numel() for p in model.parameters()):,}")
    print()
    
    # 演示编码
    test_text = "机器学习需要数据"
    encoded = tokenizer.encode(test_text, max_length=20)
    print(f"文本: {test_text}")
    print(f"编码: {encoded}")
    
    # 转换为向量
    input_ids = torch.LongTensor([encoded]).to(device)
    with torch.no_grad():
        vector = model(input_ids)
        print(f"句子向量形状: {vector.shape}")
        print(f"向量范数: {torch.norm(vector).item():.4f}")
        print(f"向量示例: {vector[0, :5].cpu().numpy()}")  # 显示前5维
    
    print("\n演示完成!")

if __name__ == "__main__":
    demonstrate_sentence_encoder()
