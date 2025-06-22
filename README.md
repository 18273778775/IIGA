# 免疫遗传算法 (IGA) Flask Web 应用

本项目实现了多种免疫遗传算法 (IGA)，并提供了一个 Flask Web 应用程序来运行它们、可视化结果以及比较不同算法的变体。

## 项目概述

项目的核心在于 `algorithm.py` 文件，该文件定义了一个抽象基类 `ImmuneGeneticAlgorithm` 和几个具体实现：
*   `StandardImmuneGeneticAlgorithm` (标准免疫遗传算法)
*   `ImprovedImmuneGeneticAlgorithm` (改进的免疫遗传算法，可选精英保留策略)
*   `TournamentSelectionIGA` (锦标赛选择免疫遗传算法)
*   `AdaptiveMutationIGA` (自适应变异免疫遗传算法)
*   `DiversityEnhancedIGA` (多样性增强免疫遗传算法)
*   `OptimizedImmuneGeneticAlgorithm` (优化免疫遗传算法)

Flask 应用程序 (`app.py`, `main.py`) 允许用户：
*   使用指定参数运行选定的 IGA。
*   查看多代最佳和平均适应度图表。
*   运行田口实验 (Taguchi experiments) 为 `ImprovedImmuneGeneticAlgorithm` 查找最优参数。
*   比较两种不同 IGA 变体的性能。

## 安装与设置

1.  **克隆代码仓库 (如果尚未克隆):**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **创建 Python 虚拟环境:**
    强烈建议使用虚拟环境来管理项目依赖。
    ```bash
    python -m venv venv
    ```

3.  **激活虚拟环境:**
    *   在 macOS 和 Linux 上:
        ```bash
        source venv/bin/activate
        ```
    *   在 Windows 上:
        ```bash
        venv\\Scripts\\activate
        ```

4.  **安装依赖:**
    项目依赖项列在 `requirements.txt` 文件中。
    ```bash
    pip install -r requirements.txt
    ```

## 运行应用程序

设置完成后，您可以运行 Flask 应用程序：

1.  **启动 Flask 开发服务器:**
    ```bash
    python main.py
    ```
    或者，您可以使用 `flask` 命令 (如果 Flask 已全局安装或虚拟环境已激活):
    ```bash
    flask run
    ```
    应用程序通常会在 `http://127.0.0.1:5000` 或 `http://0.0.0.0:5000` 上可用。

2.  **打开您的网络浏览器** 并导航到终端中显示的地址。

您应该能看到 Web 界面，在那里您可以选择算法、调整参数并运行模拟。

## 项目结构

```
.
├── README.md           # 本文件 (自述文件)
├── algorithm.py        # 核心 IGA 实现
├── app.py              # Flask 应用逻辑 (路由、视图)
├── main.py             # 运行 Flask 应用的入口点
├── models.py           # 数据库模型的占位文件 (当前未使用)
├── pyproject.toml      # 项目元数据和依赖 (PEP 621)
├── requirements.txt    # 用于 pip 的固定依赖项列表
├── utils.py            # 工具函数
└── templates/          # Flask 应用的 HTML 模板 (由 render_template 隐式使用)
    └── index.html      # 主要的 HTML 页面 (注意：此文件是占位符)
```

**关于 `templates/index.html` 的说明:**
Flask 应用程序 (`app.py`) 使用 `render_template('index.html')`。此项目中的 `templates/index.html` 文件当前是一个基础占位符，它允许应用程序运行，但**不包含完整的用户交互界面**。
如果您拥有原始 Replit 项目中的 `index.html` 文件以及任何相关的 CSS/JavaScript 文件，您需要将它们放置在 `templates` 目录 (以及可能的 `static` 目录，用于存放 CSS/JS 文件) 中，以获得完整的可视化界面。否则，用户将只能通过编程方式 (例如使用 Postman 或 curl) 与 API 端点交互。

## 如何贡献
(如果这是一个开放项目，可以在此添加贡献指南)。
