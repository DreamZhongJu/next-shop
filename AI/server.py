# server.py
import os
import math
import torch
import uvicorn
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
# ===== 在文件顶部 imports 附近补充 =====
import re
import jieba
import jieba.posseg as pseg
from collections import Counter

# ===== 工具：清理文本，尽量只留“短词/短语”友好的字符 =====
_CHINESE_RE = re.compile(r'[\u4e00-\u9fff]+')
_ALNUM_RE   = re.compile(r'[a-z0-9]+', re.I)
_PUNC_STRIP = " ，。,.、/|;；:：-—()（）[]【】~!@#$%^&*_+<>?:\"'\\"

STOPWORDS = set([
    # 口水/功能词，尽量别出现在联想里
    "这款","采用","具有","无论是","可以","就是","整体","如果","以及","能够","支持",
    "非常","比较","还是","的话","更加","进行","关于","以及","一种","一款","款式",
])

# 简单词性白名单（名词、形容词、专名、英文等）
POS_WHITELIST = set(["n","nr","ns","nz","nt","eng","x","a","an","vn","vnf"])

def _is_good_token(w, flag):
    if not w:
        return False
    if w in STOPWORDS:
        return False
    # 纯标点/空白过滤
    if not (_CHINESE_RE.search(w) or _ALNUM_RE.search(w)):
        return False
    # 词性过滤
    if flag not in POS_WHITELIST:
        # 允许纯数字/字母
        if _ALNUM_RE.fullmatch(w):
            return True
        return False
    # 单字允许，但更偏向 2-3 字
    return True

def _extract_keywords_cn(text: str, top_k=20):
    """用 jieba 抽关键词（单词），只保留白名单词性。"""
    words = []
    for w, f in pseg.cut(text):
        w = w.strip(_PUNC_STRIP).strip()
        if _is_good_token(w, f):
            words.append(w)
    # 频次 + 长度微弱加成
    cnt = Counter(words)
    scored = sorted(cnt.items(), key=lambda x: (x[1], len(x[0])>=2, len(x[0])), reverse=True)
    return [w for w,_ in scored[:top_k]]

def _compose_bigrams(words, query):
    """把相邻的关键词组成二元短语；优先包含 query 的短语。"""
    bigrams = []
    for i in range(len(words)-1):
        a, b = words[i], words[i+1]
        if a in STOPWORDS or b in STOPWORDS: 
            continue
        # 过滤太长的词拼接
        if len(a) > 8 or len(b) > 8:
            continue
        phrase = a + b
        # 控制总长度（中文 4~10 字）
        if 2 <= len(phrase) <= 10:
            bigrams.append(phrase)
    # 排序：包含 query 的优先，然后按长度适中优先
    q = (query or "").strip()
    bigrams = sorted(set(bigrams), key=lambda s: (q and q in s, 4 <= len(s) <= 8, len(s)), reverse=True)
    return bigrams

# 放在工具函数区域（和 _extract_keywords_cn / _compose_bigrams 放一起）
_PUNC_STRIP = " ，。,.、/|;；:：-—()（）[]【】~!@#$%^&*_+<>?:\"'\\"

def _remove_query_from_phrase(phrase: str, query: str) -> str:
    """把候选里的 query 去掉，只保留联想内容；兼顾中文的前缀重叠等情况。"""
    if not phrase:
        return ""
    s = phrase.strip(_PUNC_STRIP).strip()
    q = (query or "").strip()
    if not q:
        return s

    # 1) 直接替换掉完整 query 出现的位置
    s = s.replace(q, "")

    # 2) 若依然以 query 的前缀开头（例如 tokenizer/抽词导致“智能手…”），去掉最长公共前缀（阈值≥2个字）
    i = 0
    m = min(len(s), len(q))
    while i < m and s[i] == q[i]:
        i += 1
    if i >= 2:
        s = s[i:]

    # 3) 处理一些常见尾部重叠（例如 q 结尾“手机”，候选以“手机”开头）
    for k in (q[-2:], q[-1:]):
        if k and s.startswith(k):
            s = s[len(k):]

    return s.strip(_PUNC_STRIP).strip()

def _postprocess_suggestions(raw_texts, query, max_chars=12, want_n=8, association_only=True):
    """句子 -> 关键词集合（单词 + 二元短语）-> 清洗/去重/截断
       association_only=True 时，把候选里的 query 部分去掉，只保留“联想内容”。
    """
    from collections import Counter

    # 1) 先抽关键词
    cand_words = []
    for t in raw_texts:
        t = (t or "").strip()
        t = t.strip(_PUNC_STRIP)
        if not t:
            continue
        cand_words.extend(_extract_keywords_cn(t, top_k=20))

    # 2) bigram + 单词，优先和 query 相关的
    bigrams = _compose_bigrams(cand_words, query)
    q = (query or "").strip()
    singles = list(dict.fromkeys([w for w in cand_words if (not q) or (q in w or w in q)]))

    merged = bigrams + singles  # bigram 优先

    # 3) 去掉 query，做清理与长度裁剪
    cleaned = []
    for s in merged:
        s = s.strip(_PUNC_STRIP).strip()
        if not s:
            continue
        if association_only:
            s = _remove_query_from_phrase(s, q)
        if not s or s == q:
            continue
        if len(s) > max_chars:
            s = s[:max_chars]
        # 避免只剩下标点/空白
        if not s or all(ch in _PUNC_STRIP for ch in s):
            continue
        cleaned.append(s)

    # 4) 去重、保序，取前 N
    seen = set()
    out = []
    for s in cleaned:
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
        if len(out) >= want_n:
            break
    return out




# ========= 你自己的模型/分词器 =========
# 如果这些类定义就在本文件，请直接粘贴进来；
# 若在其他文件，请改成 from your_module import LightweightTransformer, TextTokenizer
from nlp_transformer import TextTokenizer  # 你已有
from item_desc_train import LightweightTransformer  # 如果类在当前文件，改为: from __main__ import LightweightTransformer

# ========= 配置 =========
MODEL_PATH = os.environ.get("MODEL_PATH", "item_desc_model_final.pth")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ========= 全局对象 =========
app = FastAPI(title="Suggest API", version="1.0.0")
model = None
tokenizer = None
vocab_size = None
model_cfg = None

# ========= 工具函数 =========
def load_model(model_path: str):
    global model, tokenizer, vocab_size, model_cfg
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    ckpt = torch.load(model_path, map_location=DEVICE)
    vocab_size = ckpt["vocab_size"]
    model_cfg = ckpt["model_config"]
    tokenizer_obj = ckpt["tokenizer"]

    # 构建模型并加载权重
    mdl = LightweightTransformer(vocab_size=vocab_size, **model_cfg)
    mdl.load_state_dict(ckpt["model_state_dict"], strict=True)
    mdl.to(DEVICE)
    mdl.eval()

    return mdl, tokenizer_obj, vocab_size, model_cfg

def _clean_text(s: str, max_chars: int = 18) -> str:
    """把 decode 后的文本清理/截断成更适合联想的短语。"""
    s = (s or "").strip()
    # 去掉多余空格（中文习惯）
    s = s.replace("  ", " ")
    # 优先在标点处截断
    cutset = "，。,.、/|;；:：-—()（）[]【】"
    for i, ch in enumerate(s):
        if i >= max_chars:
            break
        # 尽量在第一个“合适标点”之前截断
    if len(s) > max_chars:
        s = s[:max_chars]
    # 去掉前后标点/空白
    return s.strip(" ，。,.、/|;；:：-—()（）[]【】").strip()

def _dedup_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in items:
        k = x.strip()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(k)
    return out

# ========= 数据模型 =========
class SuggestResponse(BaseModel):
    query: str
    suggestions: List[str]

# ===== 用模型过采样，然后做关键词化的主函数：替换原 generate_suggestions =====
@torch.inference_mode()
def generate_suggestions(
    q: str,
    *,
    n: int = 8,
    oversample: int = 3,
    max_new_tokens: int = 12,
    temperature: float = 0.9,
    top_k: int = 30,
) -> List[str]:
    """
    关键词联想：
      1) 用模型生成 oversample*n 条句子片段；
      2) 用 jieba 抽关键词 + 组合二元短语；
      3) 清洗/去重/截断，返回 N 条短词/短语。
    """
    if not q or not q.strip():
        return []

    rounds = max(1, n * oversample)
    raw_texts: List[str] = []
    for _ in range(rounds):
        text = model.generate(
            input_text=q.strip(),
            tokenizer=tokenizer,
            max_length=max_new_tokens,
            temperature=temperature,
            top_k=top_k
        )
        raw_texts.append(text)

    suggestions = _postprocess_suggestions(raw_texts, query=q, max_chars=12, want_n=n)
    return suggestions


# ========= FastAPI 路由 =========
@app.on_event("startup")
def _startup():
    global model, tokenizer, vocab_size, model_cfg
    try:
        print(f"[Startup] Loading model from: {MODEL_PATH} on {DEVICE} ...")
        model, tokenizer, vocab_size, model_cfg = load_model(MODEL_PATH)
        print(f"[Startup] Model loaded. vocab_size={vocab_size}, cfg={model_cfg}")
    except Exception as e:
        # 启动失败时抛异常，让容器/进程管理器重启
        raise RuntimeError(f"加载模型失败: {e}")

@app.get("/health")
def health():
    ok = model is not None and tokenizer is not None
    return {"ok": ok, "device": str(DEVICE), "model_path": MODEL_PATH}

@app.get("/suggest", response_model=SuggestResponse)
def suggest(
    q: str = Query(..., description="用户输入的查询前缀"),
    n: int = Query(8, ge=1, le=20, description="返回候选数"),
    max_new_tokens: int = Query(12, ge=2, le=32, description="每条候选最多生成 token 数"),
    temperature: float = Query(0.9, ge=0.1, le=1.5, description="采样温度"),
    top_k: int = Query(30, ge=0, le=200, description="Top-k 采样阈值；0 表示不启用"),
):
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="模型尚未就绪")
    try:
        sugs = generate_suggestions(
            q,
            n=n,
            oversample=3,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_k=top_k,
        )
        return SuggestResponse(query=q, suggestions=sugs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {e}")

# 可选：热重载模型（线上慎用）
@app.post("/reload")
def reload_model():
    global model, tokenizer, vocab_size, model_cfg
    try:
        model, tokenizer, vocab_size, model_cfg = load_model(MODEL_PATH)
        return {"ok": True, "msg": "模型重载成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重载失败: {e}")

if __name__ == "__main__":
    # 运行：python server.py
    # 或者：uvicorn server:app --host 0.0.0.0 --port 8000 --workers 1
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
