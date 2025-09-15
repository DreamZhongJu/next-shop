import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from nlp_transformer import TextTokenizer
import numpy as np
from tqdm import tqdm
import os
import math

class ItemDescDataset(Dataset):
    """商品描述数据集"""
    
    def __init__(self, file_path, tokenizer, max_seq_length=128, max_samples=None):
        self.file_path = file_path
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length
        self.samples = []
        
        # 读取数据
        self._load_data(max_samples)
    
    def _load_data(self, max_samples):
        """加载数据"""
        print("加载数据集...")
        count = 0
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in tqdm(f, desc="读取数据"):
                if '\t' in line:
                    title, desc = line.strip().split('\t', 1)
                    
                    # 创建训练样本：使用标题作为输入，描述作为目标
                    if title and desc:
                        self.samples.append((title, desc))
                        count += 1
                        
                        if max_samples and count >= max_samples:
                            break
        
        print(f"加载完成，共 {len(self.samples)} 个样本")
    
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        title, desc = self.samples[idx]
        # 先拿“纯 token id”，不加特殊符，不 padding
        title_ids = self.tokenizer.encode(title, max_length=None, add_special=False, pad_to_max=False)
        desc_ids  = self.tokenizer.encode(desc,  max_length=None, add_special=False, pad_to_max=False)

        sos = self.tokenizer.special_tokens['<SOS>']
        eos = self.tokenizer.special_tokens['<EOS>']
        sep = self.tokenizer.special_tokens['<SEP>']
        pad = self.tokenizer.special_tokens['<PAD>']

        # 统一拼：[SOS] title [SEP] desc [EOS]
        ids = [sos] + title_ids + [sep] + desc_ids + [eos]

        # 截断到 max_seq_length
        ids = ids[:self.max_seq_length]
        attn = [1] * len(ids)

        # padding 到固定长度
        if len(ids) < self.max_seq_length:
            pad_n = self.max_seq_length - len(ids)
            ids  += [pad] * pad_n
            attn += [0] * pad_n

        # 右移标签：next-token，PAD 的 label 记为 -100（和 loss 的 ignore_index 对齐）
        ignore_index = -100
        labels = ids[1:] + [pad]
        labels = [tok if tok != pad else ignore_index for tok in labels]

        key_padding_mask = [m == 0 for m in attn]  # True=PAD

        return torch.LongTensor(ids), torch.LongTensor(labels), torch.BoolTensor(key_padding_mask)



class LightweightTransformer(nn.Module):
    """轻量级Transformer语言模型，适合4GB显存"""
    
    def __init__(self, vocab_size, d_model=256, nhead=8, 
                 num_layers=4, dim_feedforward=512, dropout=0.1, 
                 max_seq_length=128):
        super(LightweightTransformer, self).__init__()
        
        self.d_model = d_model
        self.vocab_size = vocab_size
        self.max_seq_length = max_seq_length
        
        # 词嵌入
        self.embedding = nn.Embedding(vocab_size, d_model)
        
        # 位置编码
        self.pos_encoder = nn.Embedding(max_seq_length, d_model)
        
        # Transformer编码器
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # 输出层
        self.output_layer = nn.Linear(d_model, vocab_size)
        self.dropout = nn.Dropout(dropout)
        
        # 初始化权重
        self._init_weights()
    
    def _init_weights(self):
        """初始化权重"""
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.output_layer.bias.data.zero_()
        self.output_layer.weight.data.uniform_(-initrange, initrange)
    
    def forward(self, src, src_mask=None, src_key_padding_mask=None):
        """前向传播"""
        batch_size, seq_len = src.size()
        
        # 词嵌入
        src_emb = self.embedding(src) * math.sqrt(self.d_model)
        
        # 位置编码
        positions = torch.arange(seq_len, device=src.device).unsqueeze(0).expand(batch_size, seq_len)
        pos_emb = self.pos_encoder(positions)
        src_emb = src_emb + pos_emb
        
        # Transformer编码
        output = self.transformer(src_emb, mask=src_mask, src_key_padding_mask=src_key_padding_mask)
        
        # 输出预测
        output = self.output_layer(output)
        return output
    
    def generate(self, input_text, tokenizer, max_length=50, temperature=1.0, top_k=50):
        """
        自回归生成（联想友好版）：
        - 滑动窗口避免位置越界
        - 屏蔽特殊 token（仅允许 <EOS> 用于结束）
        - 2-gram 重复阻断
        """
        self.eval()
        device = next(self.parameters()).device

        # 兼容你的 encode：若没有 add_special/pad_to_max 参数则走老签名
        try:
            ids = tokenizer.encode(input_text, max_length=self.max_seq_length - 2,
                                add_special=False, pad_to_max=False)
        except TypeError:
            ids = tokenizer.encode(input_text, max_length=self.max_seq_length - 2)
        if isinstance(ids, list):
            # 防止 encode 里已经 pad/加特殊符，这里只保留长度限制
            ids = ids[: self.max_seq_length - 2]

        sos = tokenizer.special_tokens['<SOS>']
        eos = tokenizer.special_tokens['<EOS>']
        sep = tokenizer.special_tokens.get('<SEP>', eos)

        seq = [sos] + ids + [sep]
        generated = torch.as_tensor([seq], dtype=torch.long, device=device)  # (1, L)

        # 构建禁止采样的 token（除了 <EOS>）
        ban_tokens = []
        for k in ['<PAD>', '<SOS>', '<SEP>', '<UNK>']:
            tid = tokenizer.special_tokens.get(k, None)
            if tid is not None and tid != eos:
                ban_tokens.append(tid)
        ban_tokens = torch.as_tensor(ban_tokens, dtype=torch.long, device=device) if ban_tokens else None

        def to_tensor_1d(x, device, dtype=torch.long):
            """把 list/ndarray/tensor 统一成 1D Tensor（不拷贝就地引用）"""
            if isinstance(x, torch.Tensor):
                return x.to(device=device, dtype=dtype).view(-1)
            try:
                return torch.as_tensor(x, device=device, dtype=dtype).view(-1)
            except Exception:
                # 兜底：返回长度为 0 的 1D tensor，跳过阻断逻辑
                return torch.empty(0, device=device, dtype=dtype)

        def block_repeated_bigrams(prefix_ids, logits):
            """2-gram 重复阻断：屏蔽历史中 (last, y) 出现过的 y。兼容 list/tensor。"""
            p = to_tensor_1d(prefix_ids, device=logits.device)
            if p.numel() < 2:
                return logits
            last = int(p[-1].item())
            seen_next = set()
            arr = p.tolist()
            for i in range(len(arr) - 1):
                if arr[i] == last:
                    seen_next.add(arr[i + 1])
            if seen_next:
                ix = torch.as_tensor(list(seen_next), device=logits.device, dtype=torch.long)
                logits.index_fill_(0, ix, float('-inf'))
            return logits

        new_tokens = 0
        with torch.no_grad():
            while new_tokens < max_length:
                # 保持右侧窗口 = max_seq_length
                if generated.size(1) > self.max_seq_length:
                    generated = generated[:, -self.max_seq_length:]

                L = generated.size(1)
                causal_mask = torch.triu(torch.ones(L, L, device=device, dtype=torch.bool), diagonal=1)

                logits = self(generated, src_mask=causal_mask)[0, -1, :] / max(temperature, 1e-5)

                # 屏蔽特殊 token
                if ban_tokens is not None and ban_tokens.numel() > 0:
                    logits.index_fill_(0, ban_tokens, float('-inf'))

                # 2-gram 阻断（传进去的是 tensor 切片；函数内部也能处理 list）
                logits = block_repeated_bigrams(generated[0, -self.max_seq_length:], logits)

                # top-k
                if top_k and top_k > 0:
                    k = min(top_k, logits.size(0))
                    vals, idx = torch.topk(logits, k)
                    filtered = torch.full_like(logits, float('-inf'))
                    filtered[idx] = vals
                    logits = filtered

                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)  # (1,)

                generated = torch.cat([generated, next_token.view(1, 1)], dim=1)
                new_tokens += 1

                if int(next_token.item()) == eos:
                    break

        # 你的 decode 已会过滤特殊符并在 <EOS> 截断
        return tokenizer.decode(generated[0].tolist())




def train_model():
    """训练模型"""
    print("开始训练商品描述生成模型")
    print("=" * 60)
    
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    # 数据集路径
    data_path = r"D:\Document\MyCodeProject\实习项目-电商平台\AI\数据集\item_desc_dataset\item_desc_dataset.txt"
    
    # 创建分词器
    tokenizer = TextTokenizer(vocab_size=20000)
    
    # 先构建词汇表（使用部分数据）
    print("构建词汇表...")
    sample_texts = []
    with open(data_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if '\t' in line:
                title, desc = line.strip().split('\t', 1)
                sample_texts.extend([title, desc])
            if i >= 10000:  # 使用前10000行构建词汇表
                break
    
    tokenizer.build_vocab(sample_texts)
    vocab_size = len(tokenizer.vocab)
    print(f"词汇表大小: {vocab_size}")
    
    # 创建数据集（使用部分数据以适应显存）
    dataset = ItemDescDataset(
        data_path, 
        tokenizer, 
        max_seq_length=64,
        max_samples=50000  # 使用5万样本训练
    )
    
    # 数据加载器
    dataloader = DataLoader(
        dataset, 
        batch_size=16,  # 小批次以适应显存
        shuffle=True, 
        num_workers=0
    )
    
    # 创建模型
    model = LightweightTransformer(
        vocab_size=vocab_size,
        d_model=256,      # 较小的模型维度
        nhead=8,
        num_layers=4,     # 较少的层数
        dim_feedforward=512,
        dropout=0.1,
        max_seq_length=64
    )
    model = model.to(device)
    
    # ---- 关键点1：损失忽略 -100（我们会把 PAD 的 label 设为 -100）----
    criterion = nn.CrossEntropyLoss(ignore_index=-100)
    optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)

    num_epochs = 5
    total_steps = len(dataloader) * num_epochs
    # ---- 关键点2：CosineAnnealingLR 的 T_max 用总 step 数 ----
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=total_steps)
    
    print(f"模型参数量: {sum(p.numel() for p in model.parameters()):,}")
    print(f"批次大小: 16")
    print(f"学习率: 1e-4")
    print(f"训练样本: {len(dataset)}")
    print()
    
    # 训练循环
    model.train()

    max_len = 64
    ignore_index = -100

    for epoch in range(num_epochs):
        total_loss = 0.0
        progress_bar = tqdm(dataloader, desc=f'Epoch {epoch+1}/{num_epochs}')

        for batch_idx, batch in enumerate(progress_bar):
            # ✅ 这里直接解包数据集返回的三件套
            input_ids, labels, key_padding_mask = batch  # (B, L), (B, L), (B, L)

            input_ids = input_ids.to(device)
            labels = labels.to(device)
            key_padding_mask = key_padding_mask.to(device)

            # 因果 mask（上三角为 True）
            L = input_ids.size(1)
            causal_mask = torch.triu(
                torch.ones(L, L, device=device, dtype=torch.bool),
                diagonal=1
            )

            # 前向 & 损失
            logits = model(
                input_ids,
                src_mask=causal_mask,
                src_key_padding_mask=key_padding_mask
            )  # (B, L, V)

            loss = criterion(
                logits.reshape(-1, vocab_size),
                labels.reshape(-1)
            )

            # 反向传播
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()

            total_loss += float(loss.item())
            progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})

        avg_loss = total_loss / len(dataloader)
        print(f'Epoch {epoch+1}/{num_epochs}, Average Loss: {avg_loss:.4f}')

        # 每个 epoch 后做一次生成测试
        test_generation(model, tokenizer, device)

        # 保存检查点（训练已稳定时）
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': avg_loss,
            'vocab_size': vocab_size,
            'tokenizer': tokenizer,
            'model_config': {
                'd_model': 256,
                'nhead': 8,
                'num_layers': 4,
                'dim_feedforward': 512,
                'dropout': 0.1,
                'max_seq_length': 64
            }
        }
        torch.save(checkpoint, f'item_desc_model_epoch_{epoch+1}.pth')
        print(f"检查点已保存: item_desc_model_epoch_{epoch+1}.pth")

    
    # 保存最终模型
    final_checkpoint = {
        'model_state_dict': model.state_dict(),
        'vocab_size': vocab_size,
        'tokenizer': tokenizer,
        'model_config': checkpoint['model_config']
    }
    torch.save(final_checkpoint, 'item_desc_model_final.pth')
    print("最终模型已保存: item_desc_model_final.pth")
    
    return model, tokenizer


def test_generation(model, tokenizer, device, test_cases=None):
    """测试文本生成"""
    if test_cases is None:
        test_cases = [
            "智能手机",
            "连衣裙",
            "笔记本电脑",
            "运动鞋",
            "化妆品"
        ]
    
    print("\n文本生成测试:")
    print("-" * 50)
    
    model.eval()
    for query in test_cases:
        try:
            generated = model.generate(query, tokenizer, max_length=30, temperature=0.8, top_k=20)
            print(f"输入: '{query}'")
            print(f"生成: '{generated}'")
            print()
        except Exception as e:
            print(f"生成错误: {e}")
    model.train()

def load_trained_model(model_path='item_desc_model_final.pth'):
    """加载训练好的模型"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    
    checkpoint = torch.load(model_path, map_location=device)
    
    # 创建模型
    model = LightweightTransformer(
        vocab_size=checkpoint['vocab_size'],
        **checkpoint['model_config']
    )
    
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    tokenizer = checkpoint['tokenizer']
    
    print(f"模型已加载: {model_path}")
    return model, tokenizer, device

def interactive_demo():
    """交互式演示"""
    print("商品描述生成演示")
    print("=" * 50)
    
    try:
        model, tokenizer, device = load_trained_model()
        
        print("\n输入商品名称，模型会生成相关的描述")
        print("输入 'quit' 退出")
        print("=" * 50)
        
        while True:
            query = input("\n请输入商品名称: ").strip()
            
            if query.lower() == 'quit':
                break
            if not query:
                continue
            
            try:
                generated = model.generate(query, tokenizer, max_length=50, temperature=0.7, top_k=30)
                print(f"生成结果: {generated}")
            except Exception as e:
                print(f"生成错误: {e}")
    
    except FileNotFoundError:
        print("未找到训练好的模型，请先运行训练脚本")
    except Exception as e:
        print(f"加载模型时出错: {e}")

if __name__ == "__main__":
    # 训练模型
    trained_model, tokenizer = train_model()
    
    # 交互式演示
    interactive_demo()
