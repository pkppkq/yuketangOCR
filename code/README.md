# Yuketang Question Scraper (雨课堂题目抓取工具)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Framework-Playwright-green.svg)](https://playwright.dev/)
[![OCR](https://img.shields.io/badge/OCR-RapidOCR-orange.svg)](https://github.com/RapidAI/RapidOCR)

一个基于 Playwright 和 RapidOCR 的自动化脚本，专门用于精准抓取雨课堂（Yuketang）测试及课件中的题目。支持 DOM 文本提取、精准区域截图以及本地 OCR 识别，帮助你高效整理学习资料。

## ✨ 功能特性

- **🚀 自动化流控**：基于 Playwright 驱动浏览器，自动处理登录后的页面交互。
- **🎯 精准定位**：内置智能评分算法，自动识别并定位幻灯片主体区域，排除侧边栏、菜单栏等 UI 干扰。
- **📸 智能截图**：不仅抓取全屏，还能针对题目区域进行精准裁剪截图。
- **🔍 本地 OCR**：集成 RapidOCR 引擎，即使题目是图片形式也能精准转化为可编辑文本。
- **📝 双重备份**：同步保存网页原生 DOM 文本和 OCR 识别文本，互为补充。
- **🛡️ 智能去重**：自动检测重复内容，避免在连续抓取时产生冗余数据。

## 🛠️ 安装步骤

### 1. 克隆仓库
```bash
git clone https://github.com/your-username/yuketang-scraper.git
cd yuketang-scraper
```

### 2. 安装依赖
建议使用虚拟环境：
```bash
pip install -r requirements.txt
```

### 3. 安装浏览器内核
```bash
playwright install firefox
```

## 🚀 使用指南

1. **运行脚本**：
   ```bash
   python yuketang_scraper.py
   ```
2. **扫码登录**：脚本会启动一个火狐浏览器窗口，请在弹出的窗口中扫码登录雨课堂并进入目标测试页面。
3. **开始抓取**：
   - 确保题目已完全加载。
   - 在终端按 **回车键** 即可执行抓取。
   - 脚本会自动保存：
     - `yuketang_questions_crawled.txt`: 网页原生文本。
     - `yuketang_questions_ocr.txt`: 图片 OCR 识别出的文本。
     - `yuketang_screenshots/`: 题目的精准截图。
4. **切换下一题**：在浏览器切换到下一题后，回到终端再次按回车。
5. **退出程序**：在终端输入 `q` 并回车。

## 📁 目录结构

```text
.
├── yuketang_scraper.py      # 主程序
├── requirements.txt         # 依赖清单
├── .gitignore               # Git 忽略配置
├── yuketang_questions_crawled.txt # (自动生成) 网页文本输出
├── yuketang_questions_ocr.txt     # (自动生成) OCR 文本输出
└── yuketang_screenshots/          # (自动生成) 题目截图文件夹
```

## ⚠️ 免责声明

本工具仅用于**学术研究**和**个人学习整理**。请务必遵守所在学校及雨课堂平台的相关规定，不得利用本项目进行任何形式的作弊或侵权行为。开发者对因使用本工具导致的任何后果不承担责任。

## 🤝 贡献与反馈

欢迎提交 Issue 或 Pull Request 来完善这个项目！

---
*如果这个项目对你有帮助，欢迎点个 Star 🌟*
