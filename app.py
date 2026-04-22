"""
Code Review NLP Assistant — Gradio App
Run with: python app.py
"""


import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import gradio as gr
import plotly.graph_objects as go

from models.code_analyzer import CodeReviewAnalyzer
from utils.helpers import (
    extract_functions,
    extract_classes,
    score_to_grade,
    score_color,
    build_report,
)
from data.sample_code import SAMPLES

analyzer = CodeReviewAnalyzer(use_gpu=False)


def build_radar(doc_score, name_score, comp_score, overall):
    fig = go.Figure(go.Scatterpolar(
        r=[doc_score, name_score, comp_score, overall, doc_score],
        theta=["Documentation", "Naming", "Complexity", "Overall", "Documentation"],
        fill="toself",
        fillcolor="rgba(99,102,241,0.2)",
        line=dict(color="#6366f1", width=2),
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
        height=320,
    )
    return fig


def build_bars(doc_score, name_score, comp_score):
    fig = go.Figure(go.Bar(
        x=["Documentation", "Naming", "Complexity"],
        y=[doc_score, name_score, comp_score],
        marker_color=[
            score_color(doc_score),
            score_color(name_score),
            score_color(comp_score),
        ],
        text=[str(doc_score), str(name_score), str(comp_score)],
        textposition="outside",
    ))
    fig.update_layout(
        yaxis=dict(range=[0, 115]),
        margin=dict(l=20, r=20, t=20, b=20),
        height=300,
    )
    return fig


def analyze_code(code, sample_choice, generate_doc, get_embed):
    if sample_choice != "None" and not code.strip():
        code = SAMPLES[sample_choice]

    if not code.strip():
        return (
            "<p>⚠️ Please paste some code or pick a sample.</p>",
            None, None, "", "", "", "", ""
        )

    result = analyzer.analyze(
        code,
        generate_doc=generate_doc,
        get_embedding=get_embed,
    )

    functions    = extract_functions(code)
    classes      = extract_classes(code)
    grade, label = score_to_grade(result.overall_score)
    color        = score_color(result.overall_score)

    score_html = f"""
    <div style="text-align:center; padding:1.5rem;
                background:#0f172a; border-radius:16px;
                border:1px solid #1e293b; color:white;">
        <div style="font-size:0.8rem; color:#94a3b8;
                    text-transform:uppercase; letter-spacing:0.1em;">
            Overall Score
        </div>
        <div style="font-size:3rem; font-weight:700; color:{color}; margin:0.3rem 0;">
            {result.overall_score}
        </div>
        <div style="font-size:1rem; color:#e2e8f0;">
            Grade {grade} — {label}
        </div>
        <div style="display:flex; justify-content:center;
                    gap:2rem; margin-top:1rem; flex-wrap:wrap;">
            <div>
                <div style="color:#94a3b8; font-size:0.75rem;">Docs</div>
                <div style="color:{score_color(result.documentation_score)};
                            font-weight:600; font-size:1.1rem;">
                    {result.documentation_score}
                </div>
            </div>
            <div>
                <div style="color:#94a3b8; font-size:0.75rem;">Naming</div>
                <div style="color:{score_color(result.naming_score)};
                            font-weight:600; font-size:1.1rem;">
                    {result.naming_score}
                </div>
            </div>
            <div>
                <div style="color:#94a3b8; font-size:0.75rem;">Complexity</div>
                <div style="color:{score_color(result.complexity_score)};
                            font-weight:600; font-size:1.1rem;">
                    {result.complexity_score}
                </div>
            </div>
        </div>
    </div>
    """

    issues_md = "\n".join(f"⚠️ {i}" for i in result.issues) \
        if result.issues else "✅ No critical issues found!"

    suggestions_md = "\n".join(f"💡 {s}" for s in result.suggestions)

    func_lines = []
    for fn in functions:
        doc  = "✓ docstring" if fn["has_docstring"] else "✗ no docstring"
        args = ", ".join(fn["args"]) if fn["args"] else "none"
        func_lines.append(
            f"**def {fn['name']}()** — args: `{args}` | "
            f"returns: `{fn['returns'] or 'not annotated'}` | {doc}"
        )
    funcs_md = "\n\n".join(func_lines) if func_lines else "No functions found."

    class_lines = []
    for cls in classes:
        doc     = "✓ docstring" if cls["has_docstring"] else "✗ no docstring"
        methods = ", ".join(cls["methods"][:5])
        class_lines.append(
            f"**class {cls['name']}** — methods: `{methods}` | {doc}"
        )
    classes_md = "\n\n".join(class_lines) if class_lines else "No classes found."

    docstring_md = f"```python\n{result.generated_docstring}\n```" \
        if result.generated_docstring else "Docstring generation was disabled."

    report = build_report(result)

    radar = build_radar(
        result.documentation_score,
        result.naming_score,
        result.complexity_score,
        result.overall_score,
    )
    bars = build_bars(
        result.documentation_score,
        result.naming_score,
        result.complexity_score,
    )

    return (
        score_html, radar, bars,
        issues_md, suggestions_md,
        funcs_md, classes_md,
        docstring_md, report,
    )


def load_sample(sample_choice):
    if sample_choice == "None":
        return ""
    return SAMPLES[sample_choice]


with gr.Blocks(title="Code Review NLP Assistant") as demo:

    gr.Markdown("# 🔬 Code Review NLP Assistant")
    gr.Markdown("Powered by **CodeBERT** · **CodeT5** · **AST Analysis** — 100% free & open source")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📝 Input")

            sample_dropdown = gr.Dropdown(
                choices=["None"] + list(SAMPLES.keys()),
                value="None",
                label="Load a sample",
            )

            code_input = gr.Code(
                language="python",
                label="Paste your Python code here",
                lines=20,
            )

            sample_dropdown.change(
                fn=load_sample,
                inputs=sample_dropdown,
                outputs=code_input,
            )

            with gr.Row():
                generate_doc = gr.Checkbox(value=True,  label="Generate docstring (CodeT5)")
                get_embed    = gr.Checkbox(value=False, label="Get embedding (CodeBERT)")

            analyze_btn = gr.Button("🔍 Analyze Code", variant="primary", size="lg")

        with gr.Column(scale=2):
            gr.Markdown("### 📊 Results")

            score_html  = gr.HTML()

            with gr.Row():
                radar_chart = gr.Plot(label="Quality Radar")
                bar_chart   = gr.Plot(label="Score Breakdown")

            with gr.Tabs():
                with gr.Tab("⚠️ Issues"):
                    issues_out = gr.Markdown()
                with gr.Tab("💡 Suggestions"):
                    suggestions_out = gr.Markdown()
                with gr.Tab("🔧 Functions"):
                    funcs_out = gr.Markdown()
                with gr.Tab("🏛️ Classes"):
                    classes_out = gr.Markdown()
                with gr.Tab("🤖 Docstring"):
                    docstring_out = gr.Markdown()
                with gr.Tab("📄 Full Report"):
                    report_out = gr.Markdown()

    analyze_btn.click(
        fn=analyze_code,
        inputs=[code_input, sample_dropdown, generate_doc, get_embed],
        outputs=[
            score_html, radar_chart, bar_chart,
            issues_out, suggestions_out,
            funcs_out, classes_out,
            docstring_out, report_out,
        ],
    )

if __name__ == "__main__":
    demo.launch(share=True)