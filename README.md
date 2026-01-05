# Auto Grading System (自动阅卷系统)

这是一个基于 C 语言核心逻辑和 Python Flask Web 界面的自动阅卷系统。支持命令行 (CLI) 和 Web 两种交互方式。

## 项目特性

*   **双模式交互**：
    *   **CLI 模式**：
        *   经典的命令行交互，支持 Windows/Linux。
        *   **全新彩色 UI**：引入 ANSI 颜色支持，界面更美观清晰。
        *   **自动清屏**：优化交互流程，保持界面整洁。
    *   **Web 模式**：
        *   **现代化界面**：基于 Bootstrap 5 的响应式设计。
        *   **考试安全**：考试模式锁定（禁止访问其他页面）、防后退、防意外刷新/关闭。
        *   **数据保护**：客户端表单自动缓存（LocalStorage），防止意外丢失答案。
        *   **历史记录**：自动保存考试成绩与详情，支持查看历史作答和删除记录。
        *   **富文本支持**：支持题目多行输入（适合代码题）和图片上传。
        *   **管理功能**：支持批量添加、编辑、删除题目。
        *   **随机化出题**：每次考试题目顺序自动打乱，防止背题。
        *   **考试限时**：支持倒计时显示，超时自动提交（时长可在 `config.py` 中配置）。
        *   **题目集分类**：支持按类别（如“C语言”、“历史”）筛选题目进行专项练习。
        *   **成绩导出**：支持将历史成绩导出为 CSV 文件。
*   **智能评分**：
    *   引入 **Levenshtein 编辑距离算法**，支持模糊匹配。
    *   不再要求答案完全一致，允许一定程度的错别字（如 "Hello" 与 "Hllo"），评分更加人性化。
*   **混合编程**：
    *   核心阅卷逻辑 (`grading.c`) 由 C 语言编写，编译为动态链接库 (`.dll`/`.so`)。
    *   Web 层由 Python Flask 实现，通过 `ctypes` 调用 C 语言核心库，确保高性能与逻辑复用。
*   **数据持久化**：
    *   题目存储在 `questions.txt` (UTF-8)。
    *   考试记录存储在 `results.json`。

## 目录结构

```text
auto-grading-system/
├── build/                # 编译产物 (可执行文件和动态库)
├── include/              # C 头文件
├── src/                  # C 源文件
├── web/                  # Python Web 源代码
│   ├── static/           # 静态资源 (uploads/)
│   ├── templates/        # HTML 模板
│   │   ├── add.html      # 添加题目
│   │   ├── base.html     # 基础布局
│   │   ├── edit.html     # 编辑题目
│   │   ├── exam.html     # 考试页面
│   │   ├── history.html  # 历史记录
│   │   ├── index.html    # 首页
│   │   ├── manage.html   # 管理题目
│   │   ├── result.html   # 结果详情
│   │   └── select_set.html # 题目集选择
│   ├── utils/            # 工具模块
│   │   └── data_manager.py # 数据管理类
│   ├── app.py            # Flask 主程序
│   └── config.py         # 项目配置
├── Makefile              # 构建脚本
├── questions.txt         # 题库文件
├── results.json          # 历史成绩记录
└── README.md             # 项目说明
```

## 快速开始

### 1. 环境准备

*   **C 编译器**: GCC (MinGW for Windows)
*   **构建工具**: Make
*   **Python**: 3.8+

### 2. 编译项目

在项目根目录下运行：

```bash
make
```

这将生成：
*   `build/auto_grader.exe`: 命令行版主程序。
*   `build/libgrading.dll`: 供 Python 调用的核心动态库。

### 3. 运行命令行版 (CLI)

```bash
./build/auto_grader.exe
```
*注意：CLI 版本已升级为彩色界面，支持中文显示。*

### 4. 运行 Web 版

#### 安装依赖

建议使用虚拟环境：

```bash
# 创建虚拟环境 (如果尚未创建)
python -m venv .venv

# 激活虚拟环境 (Windows)
.\.venv\Scripts\Activate

# 安装依赖
pip install -r web/requirements.txt
```

#### 启动服务

```bash
python web/app.py
```

访问浏览器：[http://127.0.0.1:5000](http://127.0.0.1:5000)

## 公网访问 (Ngrok)

如果你想将本地运行的 Web 服务分享给他人访问，可以使用 `ngrok`。

1.  **安装 Ngrok**: [下载并注册](https://ngrok.com/)。
2.  **启动映射**:
    确保你的 Flask 应用正在运行 (端口 5000)，然后在新的终端窗口中运行：
    ```bash
    ngrok http 5000
    ```
    *提示：ngrok 免费版首次访问可能会显示警告页，点击 "Visit Site" 继续即可。*

3.  **获取链接**:
    复制终端显示的 `Forwarding` 地址 (例如 `https://xxxx-xxxx.ngrok-free.app`) 发送给其他人即可访问你的自动阅卷系统。

## 开发说明

*   **添加题目**: 可以在 Web 界面添加（支持图片|分类(可选)和多行文本），也可以直接编辑 `questions.txt`。
    *   格式: `题目|答案|分值|图片文件名(可选)`
    *   注意：直接编辑文件时，换行符请使用 `[NEWLINE]` 代替。
*   **修改核心逻辑**: 修改 `src/grading.c` 后，必须重新运行 `make` 更新动态库。
