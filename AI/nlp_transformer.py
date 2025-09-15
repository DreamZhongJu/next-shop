import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import numpy as np
from collections import Counter
import re
class TextTokenizer:
    """简单的文本分词器"""
    def __init__(self, vocab_size=10000):
        self.vocab_size = vocab_size
        self.vocab = {}
        self.inverse_vocab = {}
        self.special_tokens = {
            '<PAD>': 0, '<SOS>': 1, '<EOS>': 2, '<UNK>': 3, '<SEP>': 4
        }

    def build_vocab(self, texts):
        from collections import Counter
        import re
        words = []
        for text in texts:
            tokens = self._tokenize(text)
            words.extend(tokens)
        word_counts = Counter(words)
        most_common = word_counts.most_common(self.vocab_size - len(self.special_tokens))
        self.vocab = {**self.special_tokens}
        self.inverse_vocab = {v: k for k, v in self.special_tokens.items()}
        for i, (word, _) in enumerate(most_common, start=len(self.special_tokens)):
            self.vocab[word] = i
            self.inverse_vocab[i] = word

    def _tokenize(self, text):
        """更稳的中英混合分词：中文按字切，英文按词切，保留标点"""
        import re
        text = text.lower()
        # 拆成：中文单字 | 英文/数字串 | 其他符号
        tokens = re.findall(r'[\u4e00-\u9fff]|[a-z0-9]+|[^\w\s]', text)
        return tokens

    def encode(self, text, max_length=None, add_special=False, pad_to_max=False):
        """
        add_special: 是否在两端添加 <SOS>/<EOS>
        pad_to_max : 是否把长度补到 max_length（只在给模型喂定长输入时用）
        """
        tokens = self._tokenize(text)
        unk = self.special_tokens['<UNK>']
        pad = self.special_tokens['<PAD>']
        eos = self.special_tokens['<EOS>']
        sos = self.special_tokens['<SOS>']

        token_ids = [self.vocab.get(t, unk) for t in tokens]

        if add_special:
            token_ids = [sos] + token_ids + [eos]

        if max_length is not None and pad_to_max:
            if len(token_ids) > max_length:
                # 截断时确保句尾有 EOS
                token_ids = token_ids[:max_length]
                if token_ids[-1] != eos and add_special:
                    token_ids[-1] = eos
            else:
                token_ids = token_ids + [pad] * (max_length - len(token_ids))

        return token_ids

    def decode(self, token_ids, drop_special=True, stop_at_eos=True, concat_chinese=True):
        """把 id 还原为文本，可选择过滤特殊符号"""
        specials = set(self.special_tokens.values())
        eos = self.special_tokens['<EOS>']
        out = []
        for tid in token_ids:
            if stop_at_eos and tid == eos:
                break
            if drop_special and tid in specials:
                continue
            out.append(self.inverse_vocab.get(tid, ''))
        # 中文建议不加空格
        return ''.join(out) if concat_chinese else ' '.join(out)


class PositionalEncoding(nn.Module):
    """位置编码层"""
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        
        self.register_buffer('pe', pe)
        
    def forward(self, x):
        x = x + self.pe[:, :x.size(1)]
        return x

class LanguageModelTransformer(nn.Module):
    """用于自然语言处理的Transformer语言模型"""
    def __init__(self, vocab_size, d_model=512, nhead=8, 
                 num_layers=6, dim_feedforward=2048, dropout=0.1, max_seq_length=512):
        super(LanguageModelTransformer, self).__init__()
        
        self.d_model = d_model
        self.vocab_size = vocab_size
        self.max_seq_length = max_seq_length
        
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
        # 嵌入和位置编码
        src_emb = self.embedding(src) * math.sqrt(self.d_model)
        src_emb = self.pos_encoder(src_emb)
        
        # Transformer编码
        output = self.transformer(src_emb, mask=src_mask, src_key_padding_mask=src_key_padding_mask)
        
        # 输出预测
        output = self.output_layer(output)
        return output
    
    def generate(self, prompt, tokenizer, max_length=50, temperature=1.0):
        """文本生成"""
        self.eval()
        
        # 编码提示文本
        input_ids = tokenizer.encode(prompt, max_length=self.max_seq_length)
        input_ids = torch.LongTensor([input_ids]).to(next(self.parameters()).device)
        
        generated = input_ids.clone()
        
        with torch.no_grad():
            for _ in range(max_length):
                # 前向传播
                outputs = self(generated)
                
                # 获取最后一个时间步的预测
                next_token_logits = outputs[0, -1, :] / temperature
                next_token_probs = F.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(next_token_probs, num_samples=1)
                
                # 添加到生成序列
                generated = torch.cat([generated, next_token.unsqueeze(0)], dim=1)
                
                # 如果生成结束标记，停止生成
                if next_token.item() == tokenizer.special_tokens['<EOS>']:
                    break
        
        return tokenizer.decode(generated[0].cpu().numpy())

    def encode(self, src, src_key_padding_mask=None, pool='mean'):
        self.eval()
        with torch.no_grad():
            x = self.embedding(src) * math.sqrt(self.d_model)
            x = self.pos_encoder(x)
            h = self.transformer(x, src_key_padding_mask=src_key_padding_mask)  # [B,T,D]
            if pool == 'cls':
                # 约定第一个token是 <SOS> 当作 CLS
                return h[:, 0]                              # [B, D]
            else:
                if src_key_padding_mask is None:
                    return h.mean(dim=1)                    # [B, D]
                mask = (~src_key_padding_mask).float().unsqueeze(-1)  # 1=valid
                return (h * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-6)


def create_sample_text_data():
    """创建示例文本数据"""
    sample_texts = [
        "The quick brown fox jumps over the lazy dog",
        "Hello world, this is a test sentence",
        "Machine learning is a subset of artificial intelligence",
        "Natural language processing helps computers understand human language",
        "Transformers have revolutionized the field of NLP",
        "Attention is all you need, said the famous paper",
        "Deep learning models require large amounts of data",
        "Python is a popular programming language for AI",
        "Neural networks are inspired by the human brain",
        "GPT models are based on the transformer architecture"
    ]
    return sample_texts

def demonstrate_nlp_transformer():
    """演示NLP Transformer"""
    print("自然语言处理Transformer演示")
    print("=" * 50)
    
    # 检查设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    # 创建示例文本数据
    texts = create_sample_text_data()
    print("示例文本数据:")
    for i, text in enumerate(texts, 1):
        print(f"{i}. {text}")
    print()
    
    # 构建词汇表
    tokenizer = TextTokenizer(vocab_size=1000)
    tokenizer.build_vocab(texts)
    print(f"词汇表大小: {len(tokenizer.vocab)}")
    print()
    
    # 创建模型
    vocab_size = len(tokenizer.vocab)
    model = LanguageModelTransformer(
        vocab_size=vocab_size,
        d_model=128,
        nhead=4,
        num_layers=2,
        dim_feedforward=512,
        dropout=0.1,
        max_seq_length=50
    )
    model = model.to(device)
    print(f"模型参数量: {sum(p.numel() for p in model.parameters()):,}")
    print()
    
    # 演示编码和解码
    test_text = "Hello world this is a test"
    encoded = tokenizer.encode(test_text, max_length=20)
    decoded = tokenizer.decode(encoded)
    
    print("文本编码演示:")
    print(f"原始文本: {test_text}")
    print(f"编码结果: {encoded}")
    print(f"解码结果: {decoded}")
    print()
    
    # 演示模型前向传播
    print("模型前向传播演示:")
    input_ids = torch.LongTensor([encoded]).to(device)
    with torch.no_grad():
        output = model(input_ids)
        print(f"输入形状: {input_ids.shape}")
        print(f"输出形状: {output.shape}")
        print(f"最后一个token的预测: {output[0, -1, :10]}...")  # 显示前10个logits
    
    print("\n演示完成!")

if __name__ == "__main__":
    demonstrate_nlp_transformer()
