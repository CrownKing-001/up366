# up366

从天学网（up366）听力练习页面的 JS 缓存文件中提取答案的小工具。

纯本地运行：读取 `page1.js`，解析出 `pageConfig` 里的题目数据，把每道题的正确答案以弹窗形式展示出来。不联网、不上传任何数据。

## 使用方法

1. 在天学网听力练习页面打开浏览器开发者工具（F12），在 Network 面板中找到并保存页面的 `page1.js` 文件（或使用浏览器缓存/另存为的方式拿到该文件）。
2. 将文件放在本脚本同级目录，确保文件名为 `page1.js`。
3. 运行：

```bash
python up366.py
```

解析成功后，会弹出一个窗口，按题号列出所有答案文本。

## 工作原理

```
page1.js ──▶ 提取 pageConfig JSON ──▶ 容错修复 ──▶ 解析题目结构 ──▶ 匹配正确选项 ──▶ 弹窗展示
```

- 用正则从 JS 中提取 `var pageConfig = {...};` 里的 JSON 对象。
- `fix_json_format()` 对提取出的文本做一系列容错修复：去除注释、单引号转双引号、给未加引号的键名补引号、清除尾部逗号、反转义 HTML 实体、平衡不匹配的引号。
- 按 `displayType` 区分两节题目：
  - 第一节（`displayType == "1"`）：5 段对话，每段对应 `questionList` 中的题目。
  - 第二节（displayType == "2"）：5 段材料，每段材料下嵌套 `questions_list` / `questionsList` 子题目。
- 每题根据 `answer_text`（正确选项 id）在 `options` 中找到对应文本，经 `clean_text()` 清理 HTML 标签、实体与多余空格后输出。

## 依赖

- Python 3（仅使用标准库：`tkinter`、`re`、`json`、`html`、`os`）
- Windows / macOS / Linux 均可运行，弹窗界面基于 tkinter（Linux 需安装 `python3-tk`）

## 免责说明

本项目仅供学习与技术研究使用，请勿用于违反平台规则的用途。使用者需自行承担相关责任。
