import sys
import json
import os
from datetime import datetime
import threading

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    pass

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sentiment_system import SentimentAnalysisSystem
from data_loader import DataLoader
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# 設定檔案上傳目錄
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'json', 'csv', 'xlsx', 'xls'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 上傳限制

# 全域變數用於儲存分析進度
analysis_progress = {
    'total': 0,
    'current': 0,
    'status': 'idle',
    'results': None,
    'report': None
}

def allowed_file(filename):
    """檢查檔案類型是否被允許"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """首頁路由"""
    return render_template('index.html')

@app.route('/api/analyze/manual', methods=['POST'])
def analyze_manual():
    """手動輸入評論進行分析"""
    try:
        data = request.json
        comments = data.get('comments', [])
        
        # 清理空白評論
        comments = [c.strip() for c in comments if c.strip()]
        
        if not comments:
            return jsonify({
                'success': False,
                'message': '請輸入至少一條評論'
            }), 400
        
        # 初始化系統
        system = SentimentAnalysisSystem()
        
        # 更新進度
        analysis_progress['total'] = len(comments)
        analysis_progress['current'] = 0
        analysis_progress['status'] = 'analyzing'
        
        # 執行分析
        results = system.analyze_batch(comments)
        
        if not results:
            return jsonify({
                'success': False,
                'message': '分析失敗，請檢查您的 API 密鑰'
            }), 500
        
        # 生成報告
        report = system.generate_report(results)
        
        # 儲存結果
        analysis_progress['results'] = results
        analysis_progress['report'] = report
        analysis_progress['status'] = 'completed'
        
        return jsonify({
            'success': True,
            'message': '分析完成',
            'results': results,
            'report': report
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'分析錯誤：{str(e)}'
        }), 500

@app.route('/api/analyze/file', methods=['POST'])
def analyze_file():
    """從上傳的檔案進行分析"""
    try:
        # 檢查是否有檔案上傳
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '沒有選擇檔案'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '檔案名稱不能為空'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': f'不支援的檔案類型，允許的格式：{", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # 保存檔案
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 根據檔案類型載入資料
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        if file_ext == 'txt':
            comments = DataLoader.load_from_txt(filepath)
        elif file_ext == 'json':
            column_key = request.form.get('column_key', None)
            comments = DataLoader.load_from_json(filepath, column_key)
        elif file_ext == 'csv':
            column_name = request.form.get('column_name', 'comment')
            comments = DataLoader.load_from_csv(filepath, column_name)
        elif file_ext in ['xlsx', 'xls']:
            column_name = request.form.get('column_name', 'comment')
            sheet_name = request.form.get('sheet_name', 0)
            try:
                sheet_name = int(sheet_name)
            except:
                pass
            comments = DataLoader.load_from_excel(filepath, column_name, sheet_name)
        else:
            return jsonify({
                'success': False,
                'message': '不支援的檔案格式'
            }), 400
        
        if not comments:
            return jsonify({
                'success': False,
                'message': '檔案中沒有找到評論資料'
            }), 400
        
        # 初始化系統
        system = SentimentAnalysisSystem()
        
        # 更新進度
        analysis_progress['total'] = len(comments)
        analysis_progress['current'] = 0
        analysis_progress['status'] = 'analyzing'
        
        # 執行分析
        results = system.analyze_batch(comments)
        
        if not results:
            return jsonify({
                'success': False,
                'message': '分析失敗，請檢查您的 API 密鑰'
            }), 500
        
        # 生成報告
        report = system.generate_report(results)
        
        # 儲存結果
        analysis_progress['results'] = results
        analysis_progress['report'] = report
        analysis_progress['status'] = 'completed'
        
        # 清理上傳的檔案
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': '分析完成',
            'results': results,
            'report': report
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'分析錯誤：{str(e)}'
        }), 500

@app.route('/api/progress', methods=['GET'])
def get_progress():
    """獲取分析進度"""
    return jsonify(analysis_progress), 200

@app.route('/api/export/json', methods=['POST'])
def export_json():
    """匯出 JSON 格式報告"""
    try:
        if analysis_progress['report'] is None:
            return jsonify({
                'success': False,
                'message': '沒有可匯出的報告'
            }), 400
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(analysis_progress['report'], f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'報告已匯出：{filename}',
            'filename': filename
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'匯出失敗：{str(e)}'
        }), 500

@app.route('/api/export/csv', methods=['POST'])
def export_csv():
    """匯出 CSV 格式結果"""
    try:
        if analysis_progress['results'] is None:
            return jsonify({
                'success': False,
                'message': '沒有可匯出的結果'
            }), 400
        
        import pandas as pd
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{timestamp}.csv"
        
        df = pd.DataFrame(analysis_progress['results'])
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        
        return jsonify({
            'success': True,
            'message': f'結果已匯出：{filename}',
            'filename': filename
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'匯出失敗：{str(e)}'
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    """重置分析結果"""
    global analysis_progress
    analysis_progress = {
        'total': 0,
        'current': 0,
        'status': 'idle',
        'results': None,
        'report': None
    }
    return jsonify({
        'success': True,
        'message': '已重置'
    }), 200

@app.errorhandler(413)
def request_entity_too_large(error):
    """處理檔案過大的錯誤"""
    return jsonify({
        'success': False,
        'message': '檔案過大，最大上傳限制為 16MB'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """處理 404 錯誤"""
    return jsonify({
        'success': False,
        'message': '請求的資源不存在'
    }), 404

if __name__ == '__main__':
    print("\n" + "="*60)
    print("【輿情分析系統 - 已啟動】")
    print("="*60)
    print("請在瀏覽器中開啟：http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)