# app.py (優化模型預載入)
from flask import Flask, render_template, request
from masking import mask_text, get_nlp_model # 導入 get_nlp_model

app = Flask(__name__)

# 在應用程式啟動時，預先載入常用的中英文模型
# 這樣可以避免第一次請求時的延遲。
try:
    get_nlp_model('zh')
    get_nlp_model('en')
    print("模型預載入完成：zh_core_web_sm 和 en_core_web_sm 已就緒。")
except Exception as e:
    print(f"模型預載入失敗：{e}")


@app.route('/', methods=['GET', 'POST'])
def index():
    original = ''
    masked = ''
    mode = 'semantic' 
    if request.method == 'POST':
        original = request.form['input_text']
        mode = request.form.get('mode', 'semantic')
        # 這裡調用 masking.py 中的函式
        masked = mask_text(original, mode=mode)
        
    return render_template('index.html', original=original, masked=masked, mode=mode)

if __name__ == '__main__':
    app.run(debug=True)