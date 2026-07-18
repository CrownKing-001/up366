import json
import re
import html
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox

def extract_answers_from_js_file(file_path):
    """从JS文件中提取JSON数据，增强格式错误处理"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # 尝试提取pageConfig变量后的JSON
        json_str = None
        # 更精确的正则模式，确保捕获完整的JSON对象
        match = re.search(r'var\s+pageConfig\s*=\s*({[\s\S]*?});\s*$', js_content)
        if match:
            json_str = match.group(1)
        else:
            # 尝试寻找最外层的{}对
            match = re.search(r'({[\s\S]*})', js_content)
            if match:
                json_str = match.group(1)
        
        if not json_str:
            raise ValueError("未找到有效的JSON数据")
        
        # 增强的JSON格式修复
        json_str = fix_json_format(json_str)
        
        return json.loads(json_str)
    
    except Exception as e:
        raise ValueError(f"JSON解析错误: {str(e)} 在位置 {e.pos}")

def fix_json_format(json_str):
    """修复常见的JSON格式问题，增强版"""
    # 1. 移除注释
    json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    
    # 2. 处理字符串内的单引号（先转义再替换）
    json_str = re.sub(r'"([^"]*)"', lambda m: m.group(0).replace("'", "\\'"), json_str)
    json_str = json_str.replace("'", '"')
    
    # 3. 修复键名缺少引号的问题
    json_str = re.sub(r'([{,]\s*)([\w-]+)\s*:', r'\1"\2":', json_str)
    
    # 4. 修复尾部逗号
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    
    # 5. 修复HTML实体和特殊字符
    json_str = html.unescape(json_str)
    json_str = json_str.replace('\n', '\\n').replace('\r', '\\r')
    
    # 6. 确保布尔值和null的正确格式
    json_str = re.sub(r'\btrue\b', 'true', json_str)
    json_str = re.sub(r'\bfalse\b', 'false', json_str)
    json_str = re.sub(r'\bnull\b', 'null', json_str)
    
    # 7. 修复可能的引号不匹配问题
    json_str = balance_quotes(json_str)
    
    return json_str

def balance_quotes(s):
    """平衡引号，确保每个开引号都有关闭引号"""
    quotes = []
    for i, c in enumerate(s):
        if c == '"':
            if quotes and quotes[-1] == i-1 and s[i-1] == '\\':
                # 处理转义引号
                quotes.pop()
            else:
                quotes.append(i)
    
    # 如果引号数量为奇数，移除最后一个
    if len(quotes) % 2 != 0:
        last_quote = quotes[-1]
        s = s[:last_quote] + s[last_quote+1:]
    
    return s

def extract_answers(page_config):
    """从解析后的JSON结构中提取答案"""
    results = []
    question_count = 1
    
    # 处理第一节（5段对话）
    for slide in page_config.get("slides", []):
        if slide.get("displayType") == "1":  # 第一节
            for question in slide.get("questionList", []):
                # 获取答案文本
                correct_answer = question.get("answer_text", "")
                answer_text = ""
                for option in question.get("options", []):
                    if option.get("id") == correct_answer:
                        answer_text = option.get("content", "")
                        break
                
                results.append({
                    "question_number": question_count,
                    "answer_text": clean_text(answer_text)
                })
                question_count += 1
    
    # 处理第二节（5段材料）
    for slide in page_config.get("slides", []):
        if slide.get("displayType") == "2":  # 第二节
            for material in slide.get("questionList", []):
                # 处理嵌套的问题
                questions_list = material.get("questions_list", [])
                if not questions_list:
                    questions_list = material.get("questionsList", [])
                
                for question in questions_list:
                    # 获取答案文本
                    correct_answer = question.get("answer_text", "")
                    answer_text = ""
                    for option in question.get("options", []):
                        if option.get("id") == correct_answer:
                            answer_text = option.get("content", "")
                            break
                    
                    results.append({
                        "question_number": question_count,
                        "answer_text": clean_text(answer_text)
                    })
                    question_count += 1
    
    return results

def clean_text(text):
    """清理文本中的HTML标签和多余空格"""
    if not text:
        return ""
    
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 处理HTML实体
    text = html.unescape(text)
    
    # 移除多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 确保首字母大写
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    
    # 确保末尾有句点
    if text and not text.endswith(('.', '!', '?')):
        text += '.'
    
    return text

def create_answer_box(answers):
    """创建答案文本框"""
    root = tk.Tk()
    root.title("听力测试答案")
    root.geometry("600x700")
    
    # 添加标题
    title_label = tk.Label(root, text="天学网分析", font=("Arial", 16, "bold"))
    title_label.pack(pady=10)
    
    # 创建滚动文本框
    text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12))
    text_box.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # 插入答案
    for ans in answers:
        text_box.insert(tk.END, f"{ans['question_number']} {ans['answer_text']}\n")
    
    # 添加关闭按钮
    close_btn = tk.Button(root, text="关闭", command=root.destroy, width=10)
    close_btn.pack(pady=10)
    
    root.mainloop()

def main():
    input_file = "page1.js"  # 输入的JS文件路径
    
    try:
        # 检查文件是否存在
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"文件不存在: {input_file}")
        
        # 提取JSON数据
        page_config = extract_answers_from_js_file(input_file)
        print("成功解析JSON数据")
        
        # 提取答案
        answers = extract_answers(page_config)
        print(f"成功提取 {len(answers)} 个题目的答案")
        
        # 创建答案文本框
        create_answer_box(answers)
        
    except Exception as e:
        # 错误处理
        error_msg = f"处理过程中出错: {str(e)}"
        print(error_msg)
        
        # 显示错误对话框
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("错误", error_msg)
        root.destroy()

if __name__ == "__main__":
    main()
