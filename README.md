# IIGA 项目

改进遗传算法的相关代码。

## 项目结构

- `main.py`: 项目的入口点。用于一键启动后端服务并自动在浏览器中打开前端页面。
- `app/`: 包含 Flask 后端应用的目录。
  - `__init__.py`: Flask 应用的初始化和路由定义。
  - `templates/`: 存放 HTML 模板文件。
    - `index.html`: 基本的前端显示页面。

## 如何运行

1.  **安装依赖**:
    确保你已经安装了 Python 和 Flask。如果未安装 Flask，可以通过 pip 安装：
    ```bash
    pip install Flask
    ```

2.  **一键启动**:
    直接运行根目录下的 `main.py` 脚本：
    ```bash
    python main.py
    ```
    该脚本会自动执行以下操作：
    - 启动 Flask 后端服务 (默认运行在 `http://127.0.0.1:5000`)。
    - 尝试在你的默认网页浏览器中打开 `http://127.0.0.1:5000`。

    启动后，你会在终端看到类似以下的输出：
    ```
    正在启动后端服务...
    后端服务应该已经在 http://127.0.0.1:5000 上运行。
    等待后端服务启动...
    尝试在浏览器中打开 http://127.0.0.1:5000...
    浏览器已打开或尝试打开页面。
    一键启动完成。后端服务正在运行。按 Ctrl+C 关闭。
    * Serving Flask app 'app'
    * Debug mode: on
    WARNING: This is a development server. Do not use it in a production deployment.
    * Running on http://127.0.0.1:5000
    Press CTRL+C to quit
    ```

3.  **访问应用**:
    如果浏览器没有自动打开，请手动访问 `http://127.0.0.1:5000`。

4.  **关闭应用**:
    在运行 `main.py` 的终端中，按 `Ctrl+C` 来停止后端服务和脚本。

## 注意事项
-   `app/__init__.py` 中的 Flask 应用当前以 `debug=True` 和 `use_reloader=False` 模式运行。`use_reloader=False` 是因为在线程中运行 Flask 时，reloader 可能会导致问题。在生产环境中，应使用生产级 WSGI 服务器（如 Gunicorn 或 uWSGI）并禁用调试模式。
-   自动打开浏览器的功能依赖于系统的默认浏览器设置。
-   `main.py` 中 `time.sleep(3)` 的等待时间是为了给 Flask 应用足够的时间启动。如果你的应用启动较慢，可能需要适当增加这个时间。
