import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sentence_encoder import ContrastiveSentenceEncoder, create_semantic_search_model
from nlp_transformer import TextTokenizer
import numpy as np
from tqdm import tqdm
import random

class ContrastiveDataset(Dataset):
    """对比学习数据集"""
    
    def __init__(self, texts, tokenizer, max_length=128, augmentations=None):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.augmentations = augmentations or []
        
        # 为每个文本分配唯一ID作为标签
        self.text_to_id = {text: idx for idx, text in enumerate(texts)}
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        
        # 数据增强（可选）
        if self.augmentations and random.random() > 0.5:
            aug_func = random.choice(self.augmentations)
            augmented_text = aug_func(text)
        else:
            augmented_text = text
        
        # 编码文本
        token_ids = self.tokenizer.encode(text, max_length=self.max_length)
        augmented_ids = self.tokenizer.encode(augmented_text, max_length=self.max_length)
        
        return (
            torch.LongTensor(token_ids),
            torch.LongTensor(augmented_ids),
            self.text_to_id[text]  # 标签用于对比学习
        )

def create_synthetic_dataset(size=1000):
    """创建合成训练数据"""
    base_phrases = [
        "机器学习", "深度学习", "自然语言处理", "计算机视觉",
        "人工智能", "神经网络", "数据分析", "模型训练",
        "算法优化", "特征工程", "数据预处理", "模型评估"
    ]
    
    templates = [
        "{}是人工智能的重要领域",
        "{}需要大量的数据支持",
        "{}技术正在快速发展",
        "{}在工业界有广泛应用",
        "{}的研究取得了重大突破",
        "{}算法非常有效",
        "{}模型性能优秀",
        "{}方法简单易用"
    ]
    
    texts = []
    for _ in range(size):
        phrase = random.choice(base_phrases)
        template = random.choice(templates)
        texts.append(template.format(phrase))
    
    return texts

def text_augmentation(text):
    """简单的文本数据增强"""
    words = text.split()
    
    # 随机删除单词
    if len(words) > 3 and random.random() > 0.7:
        del_idx = random.randint(0, len(words) - 1)
        words.pop(del_idx)
    
    # 随机替换同义词（简单版本）
    synonym_map = {
        "机器学习": ["ML", "machine learning"],
        "深度学习": ["DL", "deep learning"],
        "自然语言处理": ["NLP", "自然语言理解"],
        "计算机视觉": ["CV", "图像识别"],
        "人工智能": ["AI", "智能系统"]
    }
    
    for i, word in enumerate(words):
        if word in synonym_map and random.random() > 0.8:
            words[i] = random.choice(synonym_map[word])
    
    return ' '.join(words)

def train_contrastive_model():
    """训练对比学习模型"""
    print("开始训练对比学习句子编码器")
    print("=" * 50)
    
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    # 创建训练数据
    train_texts = create_synthetic_dataset(size=2000)
    print(f"训练数据量: {len(train_texts)}")
    
    # 构建词汇表
    tokenizer = TextTokenizer(vocab_size=5000)
    tokenizer.build_vocab(train_texts)
    vocab_size = len(tokenizer.vocab)
    print(f"词汇表大小: {vocab_size}")
    
    # 创建数据集和数据加载器
    dataset = ContrastiveDataset(
        texts=train_texts,
        tokenizer=tokenizer,
        max_length=64,
        augmentations=[text_augmentation]
    )
    
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=0)
    
    # 创建模型
    model = create_semantic_search_model(
        vocab_size=vocab_size,
        d_model=256,
        nhead=8,
        num_layers=3,
        dim_feedforward=1024,
        dropout=0.1,
        max_seq_length=64,
        pooling_strategy='mean'
    )
    model = model.to(device)
    
    # 损失函数和优化器
    criterion = nn.CosineEmbeddingLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=len(dataloader) * 10)
    
    print(f"模型参数量: {sum(p.numel() for p in model.parameters()):,}")
    print(f"批次大小: 32")
    print(f"学习率: 1e-4")
    print()
    
    # 训练循环
    num_epochs = 10
    model.train()
    
    for epoch in range(num_epochs):
        total_loss = 0
        progress_bar = tqdm(dataloader, desc=f'Epoch {epoch+1}/{num_epochs}')
        
        for batch_idx, (orig_ids, aug_ids, labels) in enumerate(progress_bar):
            orig_ids, aug_ids = orig_ids.to(device), aug_ids.to(device)
            labels = labels.to(device)
            
            # 前向传播
            orig_embeddings = model(orig_ids)
            aug_embeddings = model(aug_ids)
            
            # 计算对比损失
            target = torch.ones(orig_embeddings.size(0)).to(device)
            loss = criterion(orig_embeddings, aug_embeddings, target)
            
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            scheduler.step()
            
            total_loss += loss.item()
            progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        avg_loss = total_loss / len(dataloader)
        print(f'Epoch {epoch+1}/{num_epochs}, Average Loss: {avg_loss:.4f}')
        
        # 每个epoch保存检查点
        if (epoch + 1) % 2 == 0:
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': avg_loss,
                'vocab_size': vocab_size,
                'tokenizer': tokenizer
            }
            torch.save(checkpoint, f'sentence_encoder_epoch_{epoch+1}.pth')
            print(f"检查点已保存: sentence_encoder_epoch_{epoch+1}.pth")
    
    # 保存最终模型
    final_checkpoint = {
        'model_state_dict': model.state_dict(),
        'vocab_size': vocab_size,
        'tokenizer': tokenizer,
        'model_config': {
            'd_model': 256,
            'nhead': 8,
            'num_layers': 3,
            'dim_feedforward': 1024,
            'dropout': 0.1,
            'max_seq_length': 64,
            'pooling_strategy': 'mean'
        }
    }
    torch.save(final_checkpoint, 'sentence_encoder_final.pth')
    print("最终模型已保存: sentence_encoder_final.pth")
    
    return model, tokenizer

def evaluate_model(model, tokenizer, device):
    """评估模型性能"""
    model.eval()
    
    # 测试句子
    test_sentences = [
        "机器学习需要数据",
        "深度学习模型",
        "自然语言处理技术",
        "人工智能应用",
        "神经网络训练"
    ]
    
    print("\n模型评估:")
    print("测试句子相似度:")
    
    with torch.no_grad():
        # 编码所有测试句子
        embeddings = []
        for sentence in test_sentences:
            token_ids = tokenizer.encode(sentence, max_length=64)
            input_ids = torch.LongTensor([token_ids]).to(device)
            embedding = model(input_ids)
            embeddings.append(embedding.cpu().numpy())
        
        embeddings = np.concatenate(embeddings, axis=0)
        
        # 计算相似度矩阵
        similarity_matrix = np.dot(embeddings, embeddings.T)
        
        # 打印相似度结果
        for i, sent1 in enumerate(test_sentences):
            for j, sent2 in enumerate(test_sentences):
                if i <= j:
                    sim = similarity_matrix[i, j]
                    print(f"'{sent1}' vs '{sent2}': {sim:.4f}")
            print()

if __name__ == "__main__":
    # 训练模型
    trained_model, tokenizer = train_contrastive_model()
    
    # 评估模型
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    evaluate_model(trained_model, tokenizer, device)
    
    print("训练完成! 模型已保存为 'sentence_encoder_final.pth'")
