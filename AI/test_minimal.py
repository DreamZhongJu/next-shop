import torch
import torch.nn as nn
from nlp_transformer import TextTokenizer
import numpy as np

class MinimalTransformer(nn.Module):
    """最小化的Transformer模型用于测试"""
    
    def __init__(self, vocab_size, d_model=64, nhead=4, num_layers=2):
        super(MinimalTransformer, self).__init__()
        
        self.d_model = d_model
        self.vocab_size = vocab_size
        
        # 词嵌入
        self.embedding = nn.Embedding(vocab_size, d_model)
        
        # 简单的位置编码（使用学习的位置嵌入）
        self.pos_encoder = nn.Embedding(50, d_model)  # 最大长度50
        
        # Transformer编码器
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=128,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # 输出层
        self.output_layer = nn.Linear(d_model, vocab_size)
        
        # 初始化权重
        self._init_weights()
    
    def _init_weights(self):
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.output_layer.bias.data.zero_()
        self.output_layer.weight.data.uniform_(-initrange, initrange)
    
    def forward(self, src):
        batch_size, seq_len = src.size()
        
        # 词嵌入
        src_emb = self.embedding(src)
        
        # 位置编码
        positions = torch.arange(seq_len, device=src.device).unsqueeze(0).expand(batch_size, seq_len)
        pos_emb = self.pos_encoder(positions)
        src_emb = src_emb + pos_emb
        
        # Transformer编码
        output = self.transformer(src_emb)
        
        # 输出预测
        output = self.output_layer(output)
        return output

def create_test_data():
    """创建测试数据"""
    test_samples = [
        ("智能手机", "高端智能手机，拍照清晰，运行流畅"),
        ("笔记本电脑", "轻薄笔记本电脑，性能强大，续航持久"),
        ("连衣裙", "时尚连衣裙，修身显瘦，面料舒适"),
        ("运动鞋", "专业运动鞋，缓震效果好，透气性强"),
        ("化妆品", "天然化妆品，不刺激皮肤，效果明显")
    ]
    return test_samples

def test_minimal_model():
    """测试最小化模型"""
    print("测试最小化模型")
    print("=" * 40)
    
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    # 创建测试数据
    test_samples = create_test_data()
    texts = []
    for title, desc in test_samples:
        texts.extend([title, desc])
    
    # 创建分词器
    tokenizer = TextTokenizer(vocab_size=1000)
    tokenizer.build_vocab(texts)
    vocab_size = len(tokenizer.vocab)
    print(f"词汇表大小: {vocab_size}")
    
    # 创建模型
    model = MinimalTransformer(vocab_size=vocab_size, d_model=64, nhead=4, num_layers=2)
    model = model.to(device)
    model.train()
    
    print(f"模型参数量: {sum(p.numel() for p in model.parameters()):,}")
    
    # 准备训练数据
    train_data = []
    for title, desc in test_samples:
        title_ids = tokenizer.encode(title, max_length=20)
        desc_ids = tokenizer.encode(desc, max_length=30)
        train_data.append((title_ids, desc_ids))
    
    # 简单训练循环
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    print("\n开始训练...")
    for epoch in range(3):
        total_loss = 0
        
        for title_ids, desc_ids in train_data:
            # 转换为tensor
            title_tensor = torch.LongTensor([title_ids]).to(device)
            desc_tensor = torch.LongTensor([desc_ids]).to(device)
            
            # 前向传播
            outputs = model(title_tensor)
            
            # 计算损失
            outputs = outputs.view(-1, vocab_size)
            targets = desc_tensor.view(-1)
            
            # 确保目标在有效范围内
            valid_mask = (targets < vocab_size) & (targets >= 0)
            if valid_mask.any():
                # 只选择有效的目标
                valid_targets = targets[valid_mask]
                # 选择对应的输出（确保长度匹配）
                min_len = min(len(outputs), len(valid_targets))
                valid_outputs = outputs[:min_len]
                valid_targets = valid_targets[:min_len]
                loss = criterion(valid_outputs, valid_targets)
            else:
                loss = torch.tensor(0.0, device=device, requires_grad=True)
            
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        print(f"Epoch {epoch+1}/3, Loss: {total_loss/len(train_data):.4f}")
    
    # 测试生成
    print("\n测试生成:")
    print("-" * 30)
    
    model.eval()
    test_queries = ["手机", "电脑", "裙子", "鞋子", "化妆品"]
    
    for query in test_queries:
        try:
            # 编码输入
            input_ids = tokenizer.encode(query, max_length=20)
            input_tensor = torch.LongTensor([input_ids]).to(device)
            
            # 生成（简单版本）
            with torch.no_grad():
                outputs = model(input_tensor)
                predictions = torch.softmax(outputs[0, -1, :], dim=-1)
                top_k = torch.topk(predictions, 5)
                
                print(f"输入: '{query}'")
                print("预测词汇:", end=" ")
                for i in range(len(top_k.values)):
                    prob = top_k.values[i].item()
                    idx = top_k.indices[i].item()
                    if idx in tokenizer.inverse_vocab:
                        word = tokenizer.inverse_vocab[idx]
                        print(f"{word}({prob:.3f})", end=" ")
                print("\n")
                
        except Exception as e:
            print(f"生成 '{query}' 时出错: {e}")
    
    print("测试完成!")

if __name__ == "__main__":
    test_minimal_model()
