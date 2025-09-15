import torch
import torch.nn as nn
from item_desc_train import LightweightTransformer, load_trained_model
from nlp_transformer import TextTokenizer
import numpy as np

class WordAssociationModel:
    """词汇联想模型"""
    
    def __init__(self, model_path='item_desc_model_final.pth'):
        self.model, self.tokenizer, self.device = load_trained_model(model_path)
        self.vocab = self.tokenizer.vocab
        self.inverse_vocab = self.tokenizer.inverse_vocab
    
    def get_word_embeddings(self):
        """获取词嵌入矩阵"""
        return self.model.embedding.weight.data.cpu().numpy()
    
    def find_similar_words(self, word, top_k=10):
        """查找相似词汇"""
        if word not in self.vocab:
            return f"词汇 '{word}' 不在词汇表中"
        
        # 获取词向量
        word_embeddings = self.get_word_embeddings()
        target_idx = self.vocab[word]
        target_vector = word_embeddings[target_idx]
        
        # 计算余弦相似度
        similarities = np.dot(word_embeddings, target_vector)
        norms = np.linalg.norm(word_embeddings, axis=1) * np.linalg.norm(target_vector)
        similarities = similarities / np.clip(norms, 1e-8, None)
        
        # 获取最相似的词汇（排除自身）
        similar_indices = np.argsort(similarities)[::-1][1:top_k+1]
        
        results = []
        for idx in similar_indices:
            if idx in self.inverse_vocab:
                results.append({
                    'word': self.inverse_vocab[idx],
                    'similarity': float(similarities[idx])
                })
        
        return results
    
    def generate_associations(self, input_text, max_associations=5, temperature=0.7):
        """生成词汇联想"""
        try:
            # 生成完整描述
            generated = self.model.generate(
                input_text, 
                self.tokenizer, 
                max_length=30, 
                temperature=temperature,
                top_k=20
            )
            
            # 提取生成的词汇（排除输入文本中的词汇）
            input_words = set(self.tokenizer._tokenize(input_text.lower()))
            generated_words = set(self.tokenizer._tokenize(generated.lower()))
            
            # 获取新的关联词汇
            new_words = list(generated_words - input_words)
            
            # 返回前几个关联词汇
            return new_words[:max_associations]
            
        except Exception as e:
            return f"生成错误: {e}"
    
    def complete_phrase(self, partial_phrase, max_completions=3):
        """短语补全"""
        try:
            # 生成多个补全建议
            completions = []
            for _ in range(max_completions):
                completed = self.model.generate(
                    partial_phrase,
                    self.tokenizer,
                    max_length=len(partial_phrase.split()) + 5,  # 只生成少量额外词汇
                    temperature=0.8,
                    top_k=15
                )
                # 提取补全部分（去掉原始短语）
                completion_part = completed[len(partial_phrase):].strip()
                if completion_part and completion_part not in completions:
                    completions.append(completion_part)
            
            return completions
            
        except Exception as e:
            return f"补全错误: {e}"
    
    def get_word_cloud(self, center_word, num_layers=2, words_per_layer=5):
        """生成词汇云（多层关联）"""
        if center_word not in self.vocab:
            return f"中心词汇 '{center_word}' 不在词汇表中"
        
        word_cloud = {0: [center_word]}  # 第0层是中心词汇
        
        # 第一层关联
        layer1_associations = self.find_similar_words(center_word, top_k=words_per_layer * 2)
        if isinstance(layer1_associations, list):
            word_cloud[1] = [assoc['word'] for assoc in layer1_associations[:words_per_layer]]
        else:
            word_cloud[1] = []
        
        # 第二层关联（如果需要）
        if num_layers > 1:
            word_cloud[2] = []
            for word in word_cloud[1]:
                associations = self.find_similar_words(word, top_k=3)
                if isinstance(associations, list):
                    for assoc in associations:
                        if assoc['word'] not in word_cloud[2] and assoc['word'] != center_word:
                            word_cloud[2].append(assoc['word'])
                            if len(word_cloud[2]) >= words_per_layer:
                                break
                if len(word_cloud[2]) >= words_per_layer:
                    break
        
        return word_cloud

def demonstrate_word_association():
    """演示词汇联想功能"""
    print("词汇联想功能演示")
    print("=" * 50)
    
    try:
        # 加载模型
        association_model = WordAssociationModel()
        
        # 测试词汇
        test_words = [
            "手机",
            "电脑", 
            "衣服",
            "美食",
            "旅游"
        ]
        
        print("1. 相似词汇查找:")
        print("-" * 30)
        for word in test_words:
            similar_words = association_model.find_similar_words(word, top_k=5)
            if isinstance(similar_words, list):
                print(f"'{word}' 的相似词汇:")
                for i, assoc in enumerate(similar_words, 1):
                    print(f"  {i}. {assoc['word']} (相似度: {assoc['similarity']:.3f})")
                print()
        
        print("\n2. 词汇联想生成:")
        print("-" * 30)
        test_phrases = [
            "智能手机",
            "游戏笔记本",
            "夏季连衣裙",
            "四川火锅",
            "海边度假"
        ]
        
        for phrase in test_phrases:
            associations = association_model.generate_associations(phrase, max_associations=3)
            if isinstance(associations, list):
                print(f"'{phrase}' 的关联词汇: {', '.join(associations)}")
            else:
                print(associations)
        
        print("\n3. 短语补全:")
        print("-" * 30)
        partial_phrases = [
            "高性能",
            "时尚",
            "美味",
            "舒适",
            "豪华"
        ]
        
        for phrase in partial_phrases:
            completions = association_model.complete_phrase(phrase, max_completions=2)
            if isinstance(completions, list):
                print(f"'{phrase}' 的补全建议: {', '.join(completions)}")
            else:
                print(completions)
        
        print("\n4. 词汇云生成:")
        print("-" * 30)
        center_words = ["科技", "时尚", "美食"]
        
        for word in center_words:
            word_cloud = association_model.get_word_cloud(word, num_layers=2, words_per_layer=3)
            if isinstance(word_cloud, dict):
                print(f"'{word}' 的词汇云:")
                for layer, words in word_cloud.items():
                    print(f"  第{layer}层: {', '.join(words)}")
                print()
            else:
                print(word_cloud)
    
    except FileNotFoundError:
        print("未找到训练好的模型，请先运行训练脚本")
    except Exception as e:
        print(f"加载模型时出错: {e}")

def interactive_word_association():
    """交互式词汇联想"""
    print("交互式词汇联想演示")
    print("=" * 50)
    
    try:
        association_model = WordAssociationModel()
        
        print("选择功能:")
        print("1. 相似词汇查找")
        print("2. 词汇联想生成") 
        print("3. 短语补全")
        print("4. 词汇云生成")
        print("输入 'quit' 退出")
        print("=" * 50)
        
        while True:
            choice = input("\n请选择功能 (1-4): ").strip()
            
            if choice.lower() == 'quit':
                break
            
            if choice == '1':
                word = input("请输入要查找相似词汇的词语: ").strip()
                if word:
                    similar_words = association_model.find_similar_words(word, top_k=8)
                    if isinstance(similar_words, list):
                        print(f"\n'{word}' 的相似词汇:")
                        for i, assoc in enumerate(similar_words, 1):
                            print(f"  {i}. {assoc['word']} (相似度: {assoc['similarity']:.3f})")
                    else:
                        print(similar_words)
            
            elif choice == '2':
                phrase = input("请输入短语进行联想: ").strip()
                if phrase:
                    associations = association_model.generate_associations(phrase, max_associations=5)
                    if isinstance(associations, list):
                        print(f"\n联想词汇: {', '.join(associations)}")
                    else:
                        print(associations)
            
            elif choice == '3':
                partial = input("请输入不完整的短语: ").strip()
                if partial:
                    completions = association_model.complete_phrase(partial, max_completions=3)
                    if isinstance(completions, list):
                        print(f"\n补全建议:")
                        for i, completion in enumerate(completions, 1):
                            print(f"  {i}. {partial}{completion}")
                    else:
                        print(completions)
            
            elif choice == '4':
                center = input("请输入中心词汇: ").strip()
                if center:
                    word_cloud = association_model.get_word_cloud(center, num_layers=2, words_per_layer=4)
                    if isinstance(word_cloud, dict):
                        print(f"\n'{center}' 的词汇云:")
                        for layer, words in word_cloud.items():
                            print(f"  第{layer}层: {', '.join(words)}")
                    else:
                        print(word_cloud)
            
            else:
                print("无效选择，请重新输入")
    
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    print("词汇联想系统")
    print("=" * 50)
    print("选择模式:")
    print("1. 功能演示")
    print("2. 交互式体验")
    
    mode = input("请选择模式 (1-2): ").strip()
    
    if mode == "1":
        demonstrate_word_association()
    elif mode == "2":
        interactive_word_association()
    else:
        print("无效选择，运行功能演示")
        demonstrate_word_association()
