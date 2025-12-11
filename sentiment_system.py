import os
from dotenv import load_dotenv
from mistralai import Mistral
import pandas as pd
import jieba
from datetime import datetime
import json
import sys

# 載入環境變數
load_dotenv()

class SentimentAnalysisSystem:
    def __init__(self, api_key=None):
        """初始化輿情分析系統（使用 Mistral AI）"""
        api_key = api_key or os.getenv("MISTRAL_API_KEY")
        
        if not api_key:
            raise ValueError("MISTRAL_API_KEY 環境變數未設定")
        
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-large-latest"
    
    def preprocess_text(self, text):
        """文本前處理：分詞、清理等"""
        words = jieba.cut(text)
        words = [w for w in words if len(w) > 1 and w.strip()]
        return list(words)
    
    def analyze_single_comment(self, text):
        """分析單一條評論"""
        try:
            # 建立分析提示詞
            prompt = f"""你是一個專業的輿情分析專家。請詳細分析以下文本內容。

【待分析文本】
{text}

【分析要求】
請按照以下格式提供分析結果：

1. 情感分類：正面/中立/負面
2. 情感強度：1-10分（1為最弱，10為最強）
3. 核心議題：列出3-5個主要議題
4. 關鍵詞標籤：列出5-8個關鍵詞
5. 輿情特點分析：用2-3句話說明這則文本的輿情特徵

【回應格式】
請直接按照上述編號順序回應，每項佔一行。"""
            
            # 使用 Mistral 進行分析
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"分析錯誤：{str(e)}"
    
    def analyze_batch(self, comments_list):
        """批量分析多條評論"""
        results = []
        total = len(comments_list)
        
        if total == 0:
            print("❌ 錯誤：沒有評論資料可以分析")
            return results
        
        for idx, comment in enumerate(comments_list, 1):
            # 跳過空白評論
            if not comment or not str(comment).strip():
                print(f"[警告] 第 {idx} 條評論為空，已跳過")
                continue
            
            print(f"[進度] 正在分析第 {idx}/{total} 條評論...", end=" ")
            sys.stdout.flush()
            
            analysis = self.analyze_single_comment(str(comment))
            
            results.append({
                "序號": idx,
                "原始評論": str(comment),
                "AI分析結果": analysis,
                "分析時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            print("✓")
        
        return results
    
    def extract_sentiment_label(self, analysis_text):
        """從分析結果中提取情感標籤"""
        if "正面" in analysis_text:
            return "正面"
        elif "負面" in analysis_text:
            return "負面"
        else:
            return "中立"
    
    def extract_sentiment_score(self, analysis_text):
        """從分析結果中提取情感強度分數"""
        import re
        match = re.search(r'(\d+)\s*[-~]?\s*10', analysis_text)
        if match:
            return int(match.group(1))
        return 5  # 預設為中立
    
    def generate_report(self, results):
        """生成輿情分析報告"""
        if not results:
            return None
        
        sentiments = [self.extract_sentiment_label(r["AI分析結果"]) for r in results]
        
        report = {
            "報告生成時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "總評論數": len(results),
            "詳細分析結果": results,
            "統計摘要": {
                "正面評論數": sentiments.count("正面"),
                "中立評論數": sentiments.count("中立"),
                "負面評論數": sentiments.count("負面"),
                "正面比例": f"{sentiments.count('正面')/len(results)*100:.1f}%",
                "中立比例": f"{sentiments.count('中立')/len(results)*100:.1f}%",
                "負面比例": f"{sentiments.count('負面')/len(results)*100:.1f}%",
            }
        }
        return report
    
    def save_report_to_json(self, report, filename="sentiment_report.json"):
        """將報告保存為 JSON 檔案"""
        if report is None:
            print("❌ 報告為空，無法保存")
            return
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"✓ 報告已保存至：{filename}")
    
    def save_report_to_csv(self, results, filename="sentiment_results.csv"):
        """將結果保存為 CSV 檔案"""
        if not results:
            print("❌ 沒有結果可以保存")
            return
        
        df = pd.DataFrame(results)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"✓ CSV 結果已保存至：{filename}")
    
    def display_report_summary(self, report):
        """在終端機顯示報告摘要"""
        if report is None:
            print("❌ 報告為空，無法顯示")
            return
        
        summary = report["統計摘要"]
        print("\n" + "="*60)
        print("【輿情分析報告摘要】")
        print("="*60)
        print(f"報告生成時間：{report['報告生成時間']}")
        print(f"分析評論總數：{report['總評論數']}")
        print(f"使用模型：Mistral AI")
        print("-"*60)
        print(f"正面評論數：{summary['正面評論數']} ({summary['正面比例']})")
        print(f"中立評論數：{summary['中立評論數']} ({summary['中立比例']})")
        print(f"負面評論數：{summary['負面評論數']} ({summary['負面比例']})")
        print("="*60)