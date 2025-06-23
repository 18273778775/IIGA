from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def run_flask_app():
    # 在实际部署中，不要使用 debug=True
    # 使用 threading 时，werkzeug 的 reloader 可能会导致问题，通常设为 use_reloader=False
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
