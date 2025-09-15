import torch
from sentence_encoder import SentenceTransformer
from nlp_transformer import TextTokenizer
from vector_index import SemanticSearchEngine
import numpy as np

class InteractiveSearchDemo:
    """交互式搜索演示"""
    
    def __init__(self, model_checkpoint=None, index_path=None):
        self.search_engine = SemanticSearchEngine(model_checkpoint, None, index_path)
        self.documents = []
    
    def load_sample_data(self):
        """加载示例数据"""
        sample_documents = [
            # 机器学习相关
            "机器学习通过算法让计算机从数据中学习模式",
            "监督学习使用标注数据训练预测模型",
            "无监督学习发现数据中的隐藏结构",
            "深度学习使用多层神经网络处理复杂任务",
            "卷积神经网络专门用于图像识别任务",
            "循环神经网络适合处理序列数据",
            
            # 自然语言处理
            "自然语言处理让计算机理解人类语言",
            "文本分类是将文档分配到预定义类别",
            "情感分析识别文本中的情感倾向",
            "命名实体识别提取文本中的实体信息",
            "机器翻译将一种语言自动翻译成另一种",
            
            # 计算机视觉
            "计算机视觉让计算机理解和分析图像",
            "目标检测识别图像中的物体位置",
            "图像分割将图像分成有意义的区域",
            "人脸识别验证或识别图像中的人脸",
            
            # 数据处理
            "数据清洗处理缺失值和异常值",
            "特征工程创建更好的输入特征",
            "数据标准化使不同尺度的特征可比",
            
            # 模型相关
            "模型评估使用测试数据验证性能",
            "交叉验证更可靠地评估模型表现",
            "过拟合指模型在训练数据上表现太好但在新数据上差",
            "正则化技术防止模型过拟合",
            
            # 应用场景
            "推荐系统根据用户喜好推荐物品",
            "欺诈检测识别异常交易行为",
            "医疗影像分析辅助医生诊断疾病",
            "自动驾驶汽车感知和理解环境"
        ]
        return sample_documents
    
    def build_demo_index(self):
        """构建演示索引"""
        print("构建演示索引...")
        self.documents = self.load_sample_data()
        
        if self.search_engine.model is None:
            # 创建简单模型用于演示
            tokenizer = TextTokenizer(vocab_size=5000)
            tokenizer.build_vocab(self.documents)
            
            model = SentenceTransformer(
                vocab_size=len(tokenizer.vocab),
                d_model=256,
                nhead=8,
                num_layers=3,
                pooling_strategy='mean'
            )
            model.eval()
            
            self.search_engine.model = model
            self.search_engine.tokenizer = tokenizer
        
        # 构建索引
        self.search_engine.build_index_from_texts(self.documents)
        print(f"索引构建完成，共 {len(self.documents)} 个文档")
    
    def interactive_search(self):
        """交互式搜索"""
        print("\n" + "="*60)
        print("语义搜索演示系统")
        print("="*60)
        print("输入查询语句进行搜索，输入 'quit' 退出")
        print("输入 'list' 查看所有文档")
        print("输入 'stats' 查看系统状态")
        print("="*60)
        
        while True:
            try:
                query = input("\n请输入搜索查询: ").strip()
                
                if query.lower() == 'quit':
                    break
                elif query.lower() == 'list':
                    self.list_documents()
                    continue
                elif query.lower() == 'stats':
                    self.show_stats()
                    continue
                elif not query:
                    continue
                
                # 执行搜索
                results = self.search_engine.search(query, k=5, threshold=0.3)
                
                if not results:
                    print("未找到相关结果")
                    continue
                
                print(f"\n找到 {len(results)} 个相关结果:")
                print("-" * 80)
                
                for i, result in enumerate(results, 1):
                    print(f"{i}. [相似度: {result['score']:.4f}]")
                    print(f"   {result['text']}")
                    print()
                
            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"搜索过程中出现错误: {e}")
    
    def list_documents(self):
        """列出所有文档"""
        print(f"\n文档库中共有 {len(self.documents)} 个文档:")
        print("-" * 80)
        for i, doc in enumerate(self.documents, 1):
            print(f"{i:2d}. {doc}")
    
    def show_stats(self):
        """显示系统状态"""
        print("\n系统状态:")
        print(f"设备: {self.search_engine.device}")
        print(f"文档数量: {len(self.documents)}")
        if self.search_engine.model:
            print(f"模型参数量: {sum(p.numel() for p in self.search_engine.model.parameters()):,}")
        else:
            print("模型: 未加载")
    
    def benchmark_search(self, queries=None):
        """搜索性能基准测试"""
        if queries is None:
            queries = [
                "机器学习",
                "深度学习",
                "自然语言处理",
                "计算机视觉",
                "数据预处理",
                "模型训练"
            ]
        
        print("\n搜索性能测试:")
        print("-" * 60)
        
        import time
        total_time = 0
        total_results = 0
        
        for query in queries:
            start_time = time.time()
            results = self.search_engine.search(query, k=3)
            end_time = time.time()
            
            search_time = (end_time - start_time) * 1000  # 毫秒
            total_time += search_time
            total_results += len(results)
            
            print(f"查询: '{query}' - {search_time:.2f}ms - {len(results)} 结果")
        
        avg_time = total_time / len(queries)
        print(f"\n平均搜索时间: {avg_time:.2f}ms")
        print(f"总结果数: {total_results}")
    
    def save_demo(self):
        """保存演示数据"""
        self.search_engine.save_index('demo_search_index.pkl')
        print("演示索引已保存到: demo_search_index.pkl")

def demonstrate_complete_system():
    """演示完整的语义搜索系统"""
    print("完整的语义搜索系统演示")
    print("=" * 60)
    
    # 创建演示系统
    demo = InteractiveSearchDemo()
    
    # 构建索引
    demo.build_demo_index()
    
    # 显示系统状态
    demo.show_stats()
    
    # 性能测试
    demo.benchmark_search()
    
    # 交互式搜索
    demo.interactive_search()
    
    # 保存演示数据
    demo.save_demo()
    
    print("\n演示完成！")

def load_and_test_pretrained():
    """加载预训练模型并测试"""
    print("加载预训练模型测试")
    print("=" * 60)
    
    try:
        # 尝试加载训练好的模型
        demo = InteractiveSearchDemo('sentence_encoder_final.pth')
        demo.build_demo_index()
        
        # 测试几个查询
        test_queries = [
            "神经网络模型",
            "文本处理技术",
            "图像识别算法"
        ]
        
        for query in test_queries:
            print(f"\n查询: '{query}'")
            results = demo.search_engine.search(query, k=3)
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. [相似度: {result['score']:.4f}] {result['text']}")
    
    except FileNotFoundError:
        print("未找到训练好的模型，请先运行训练脚本")
    except Exception as e:
        print(f"加载模型时出错: {e}")

if __name__ == "__main__":
    print("语义搜索系统演示")
    print("=" * 60)
    print("选择模式:")
    print("1. 完整系统演示")
    print("2. 加载预训练模型测试")
    print("3. 仅交互式搜索")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    demo = InteractiveSearchDemo()
    
    if choice == "1":
        demonstrate_complete_system()
    elif choice == "2":
        load_and_test_pretrained()
    elif choice == "3":
        demo.build_demo_index()
        demo.interactive_search()
    else:
        print("无效选择，运行完整演示")
        demonstrate_complete_system()
