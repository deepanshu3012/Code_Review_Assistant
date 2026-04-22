# 🔬 Code Review NLP Assistant

> An end-to-end NLP project that analyzes Python code quality using pre-trained transformer models — **100% free, no paid APIs needed.**

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-2.6.0-red?style=flat-square&logo=pytorch)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-yellow?style=flat-square&logo=huggingface)
![Gradio](https://img.shields.io/badge/Gradio-5.23.0-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🌐 Live Demo

**Try it here →** [https://deepanshu3012-codereviewassistant.hf.space](https://deepanshu3012-codereviewassistant.hf.space)

---

## 📌 What it does

Paste any Python code and get an instant AI-powered review:

- 📊 **Overall quality score** (0–100) with grade A to F
- 🔍 **Issue detection** — bare excepts, magic numbers, missing type hints, deep nesting, TODO comments
- 💡 **Suggestions** for improving code quality
- 🤖 **Auto-generated docstrings** using CodeT5 (AI writes documentation for your code)
- 🧠 **Semantic embeddings** using CodeBERT (optional)
- 📈 **Radar chart and bar chart** visualizations
- 🔧 **Function and class analysis** — args, return types, docstring presence
- ⬇️ **Downloadable Markdown report**

---

## 🧪 Results on Sample Code

| Code Quality | Score | Grade |
|---|---|---|
| Poor quality (bad names, no docs, deep nesting) | 45.5 / 100 | D |
| Good quality (docstrings, type hints, clean structure) | 78.9 / 100 | B |

The gap between scores proves the models actually understand code quality — not just syntax.

---

## 🏗️ Project Structure
Code_Review_Assistant/
├── app.py                  ← Gradio web app (main entry point)
├── requirements.txt        ← All dependencies
├── .gitignore
├── README.md
├── models/
│   ├── init.py
│   └── code_analyzer.py    ← CodeBERT + CodeT5 wrapper + scoring engine
├── utils/
│   ├── init.py
│   └── helpers.py          ← AST parsing, grading, report generation
└── data/
├── init.py
└── sample_code.py      ← 3 sample files (poor / medium / good quality)
---

## 🤖 Models Used

### CodeBERT — microsoft/codebert-base
- A RoBERTa-based model pre-trained on 6 programming languages
- Used for generating 768-dimensional semantic embeddings of code
- Captures meaning beyond syntax — understands what code does
- Paper: https://arxiv.org/abs/2002.08155

### CodeT5 — Salesforce/codet5-base-codexglue-sum-python
- A T5-based encoder-decoder fine-tuned on CodeSearchNet
- Used for automatic docstring generation from raw function code
- Paper: https://arxiv.org/abs/2109.00859

---

## 📊 Scoring System

| Dimension | Weight | How it is computed |
|---|---|---|
| Documentation | 35% | Docstring presence + comment density |
| Naming Quality | 30% | Average identifier length + meaningful names |
| Complexity | 35% | Branch count (if/for/while) + nesting depth |

### Grade Scale

| Score | Grade | Meaning |
|---|---|---|
| 90 – 100 | A | Excellent — production ready |
| 75 – 89 | B | Good — minor improvements needed |
| 60 – 74 | C | Needs work — several issues |
| 40 – 59 | D | Poor — significant refactoring needed |
| 0 – 39 | F | Critical — major overhaul required |

---

## 🚀 Run Locally

1. Clone the repo

git clone https://github.com/Deepanshu3012/Code_Review_Assistant.git
cd Code_Review_Assistant

2. Create virtual environment (Windows PowerShell)

python -m venv venv
.\venv\Scripts\Activate.ps1

3. Install dependencies

pip install -r requirements.txt

4. Run the app

python app.py

Open your browser at http://127.0.0.1:7860

Note: First run downloads CodeT5 (~900MB) and caches it locally. Subsequent runs are instant.

---

## 🆓 Free Tools Used

| Tool | Purpose | Cost |
|---|---|---|
| Hugging Face Transformers | CodeBERT + CodeT5 models | Free |
| Hugging Face Spaces | App hosting | Free |
| Gradio | Web UI | Free |
| PyTorch | Deep learning engine | Free |
| Python ast module | Code parsing | Built-in |
| Plotly | Charts and visualizations | Free |
| GitHub | Code storage | Free |

Total cost to build and deploy: Rs 0

---

## 🔭 Future Improvements

- Multi-language support (JavaScript, Java, C++) using tree-sitter
- Fine-tune CodeBERT on labeled good/bad code dataset
- Code similarity search using FAISS vector database
- GitHub Action to auto-review pull requests
- VS Code extension integration

---

## 📚 Resources

- CodeSearchNet Dataset: https://huggingface.co/datasets/code_search_net
- CodeBERT: https://huggingface.co/microsoft/codebert-base
- CodeT5: https://huggingface.co/Salesforce/codet5-base

---

## 👨‍💻 Author

Deepanshu
Final Year B.Tech CSE Student

GitHub: https://github.com/deepanshu3012
Live Demo: https://deepanshu3012-codereviewassistant.hf.space
LinkedIn: https://www.linkedin.com/in/deepanshu-joshi-b851102bb/

---

## 📄 License

MIT License — free to use, modify and distribute.

---

Built with curiosity, zero budget, and a lot of debugging 🛠️
