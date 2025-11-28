import json
import csv
import os
from pathlib import Path

class DataLoader:
    """用於載入各種格式的評論資料"""
    
    @staticmethod
    def load_from_txt(filename):
        """
        從 txt 檔案讀取評論（每行一則）
        
        檔案格式範例：
        這個產品很棒，推薦使用
        服務態度不好，不滿意
        一般般，沒有特別之處
        """
        try:
            if not os.path.exists(filename):
                print(f"❌ 檔案不存在：{filename}")
                return []
            
            with open(filename, "r", encoding="utf-8") as f:
                comments = [line.strip() for line in f if line.strip()]
            
            print(f"✓ 成功載入 TXT 檔案，共 {len(comments)} 條評論")
            return comments
        
        except Exception as e:
            print(f"❌ 讀取 TXT 檔案失敗：{str(e)}")
            return []
    
    @staticmethod
    def load_from_json(filename, key=None):
        """
        從 JSON 檔案讀取評論
        
        檔案格式範例 1（列表）：
        ["評論1", "評論2", "評論3"]
        
        檔案格式範例 2（對象，指定 key）：
        {
            "comments": ["評論1", "評論2"],
            "metadata": {}
        }
        """
        try:
            if not os.path.exists(filename):
                print(f"❌ 檔案不存在：{filename}")
                return []
            
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 如果是列表，直接返回
            if isinstance(data, list):
                comments = data
            # 如果是對象，使用指定的 key
            elif isinstance(data, dict) and key:
                comments = data.get(key, [])
            # 如果是對象但沒指定 key，嘗試找 "comments" 或 "data"
            elif isinstance(data, dict):
                comments = data.get("comments", data.get("data", []))
            else:
                print("❌ JSON 格式不支援")
                return []
            
            # 確保是列表
            if isinstance(comments, list):
                print(f"✓ 成功載入 JSON 檔案，共 {len(comments)} 條評論")
                return comments
            else:
                print("❌ JSON 中的評論數據不是列表格式")
                return []
        
        except Exception as e:
            print(f"❌ 讀取 JSON 檔案失敗：{str(e)}")
            return []
    
    @staticmethod
    def load_from_csv(filename, column_name="comment"):
        """
        從 CSV 檔案讀取評論
        
        參數：
        - filename: CSV 檔案路徑
        - column_name: 包含評論的欄位名稱（預設："comment"）
        
        檔案格式範例：
        id,comment,date
        1,很好用的產品,2024-01-01
        2,不推薦使用,2024-01-02
        """
        try:
            if not os.path.exists(filename):
                print(f"❌ 檔案不存在：{filename}")
                return []
            
            import pandas as pd
            df = pd.read_csv(filename, encoding="utf-8-sig")
            
            # 檢查欄位是否存在
            if column_name not in df.columns:
                print(f"❌ CSV 檔案中沒有 '{column_name}' 欄位")
                print(f"   可用的欄位：{', '.join(df.columns)}")
                return []
            
            comments = df[column_name].tolist()
            print(f"✓ 成功載入 CSV 檔案，共 {len(comments)} 條評論")
            return comments
        
        except Exception as e:
            print(f"❌ 讀取 CSV 檔案失敗：{str(e)}")
            return []
    
    @staticmethod
    def load_from_excel(filename, column_name="comment", sheet_name=0):
        """
        從 Excel 檔案讀取評論
        
        參數：
        - filename: Excel 檔案路徑
        - column_name: 包含評論的欄位名稱
        - sheet_name: 工作表名稱或索引（預設：0，第一個工作表）
        """
        try:
            if not os.path.exists(filename):
                print(f"❌ 檔案不存在：{filename}")
                return []
            
            import pandas as pd
            df = pd.read_excel(filename, sheet_name=sheet_name)
            
            if column_name not in df.columns:
                print(f"❌ Excel 檔案中沒有 '{column_name}' 欄位")
                print(f"   可用的欄位：{', '.join(df.columns)}")
                return []
            
            comments = df[column_name].tolist()
            print(f"✓ 成功載入 Excel 檔案，共 {len(comments)} 條評論")
            return comments
        
        except Exception as e:
            print(f"❌ 讀取 Excel 檔案失敗：{str(e)}")
            return []
    
    @staticmethod
    def auto_load(filename, **kwargs):
        """
        根據檔案副檔名自動偵測格式並載入
        
        參數：
        - filename: 檔案路徑
        - **kwargs: 傳給特定格式載入器的參數
        """
        if not os.path.exists(filename):
            print(f"❌ 檔案不存在：{filename}")
            return []
        
        file_ext = Path(filename).suffix.lower()
        
        if file_ext == ".txt":
            return DataLoader.load_from_txt(filename)
        elif file_ext == ".json":
            return DataLoader.load_from_json(filename, kwargs.get("key"))
        elif file_ext == ".csv":
            return DataLoader.load_from_csv(filename, kwargs.get("column_name", "comment"))
        elif file_ext in [".xlsx", ".xls"]:
            return DataLoader.load_from_excel(
                filename,
                kwargs.get("column_name", "comment"),
                kwargs.get("sheet_name", 0)
            )
        else:
            print(f"❌ 不支援的檔案格式：{file_ext}")
            return []
    
    @staticmethod
    def create_sample_files():
        """建立範例檔案供測試"""
        sample_comments = [
            "新推出的功能真的太棒了，使用體驗提升很多，介面也更直覺！",
            "這次更新有一些小問題，但整體方向還是不錯的。",
            "非常失望，客服態度惡劣，完全不推薦。",
            "中規中矩，沒有特別驚喜的地方，跟預期一樣。",
            "我非常喜歡這項服務，已經推薦給朋友了，真的超值。",
            "速度太慢了，經常當機，浪費我的時間。",
            "功能齊全，價格合理，是不錯的選擇。",
            "還可以，但是相比競爭對手就沒什麼優勢了。"
        ]
        
        # 建立 TXT 檔案
        with open("sample_comments.txt", "w", encoding="utf-8") as f:
            for comment in sample_comments:
                f.write(comment + "\n")
        print("✓ 已建立 sample_comments.txt")
        
        # 建立 JSON 檔案
        with open("sample_comments.json", "w", encoding="utf-8") as f:
            json.dump({"comments": sample_comments}, f, ensure_ascii=False, indent=2)
        print("✓ 已建立 sample_comments.json")
        
        # 建立 CSV 檔案
        import csv
        with open("sample_comments.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "comment", "date"])
            for idx, comment in enumerate(sample_comments, 1):
                writer.writerow([idx, comment, datetime.now().strftime("%Y-%m-%d")])
        print("✓ 已建立 sample_comments.csv")