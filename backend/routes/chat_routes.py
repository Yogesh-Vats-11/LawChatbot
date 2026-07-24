from flask import Blueprint, request, jsonify
from services.search_service import semantic_search
from models.embedding import sections
from models.summarizer import summarizer
import json
from config import GRAPH_PATH

chat_bp = Blueprint("chat", __name__)

def clean_content(text):
    lines = text.split("\n")

    lines = [l.strip() for l in lines if l.strip()]

    if len(lines) > 2:
        lines = lines[2:]

    clean = " ".join(lines)

    return clean


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query", "").lower()

    if not query:
        return jsonify({"error": "Query required"}), 400

    results = semantic_search(query, top_k=1)

    mode = "short"
    if any(word in query for word in ["detail", "explain", "full", "all"]):
        mode = "full"

    formatted = []

    for law in results:
        content = clean_content(law["content"])

        if mode == "short":
            if "." in content:
                content = content.split(".")[0] + "."
            else:
                content = content[:150] + "..."

        formatted.append({
            "content": content
        })

    return jsonify({
        "mode": mode,
        "results": formatted
    })


@chat_bp.route("/analyze_case", methods=["POST"])
def analyze_case():
    data = request.json
    case = data.get("case")

    if not case:
        return jsonify({"error": "Case required"}), 400

    laws = semantic_search(case)

    try:
        with open(GRAPH_PATH) as f:
            graph = json.load(f)
    except:
        graph = {}

    related = []
    for law in laws:
        related.extend(graph.get(law["section_title"], []))

    return jsonify({
        "relevant_laws": laws,
        "related_crimes": related
    })


@chat_bp.route("/summarize", methods=["POST"])
def summarize():
    text = request.json.get("text")

    if not text:
        return jsonify({"error": "Text required"}), 400

    result = summarizer(text, max_length=200, do_sample=False)

    return jsonify({
        "summary": result[0]["generated_text"]
    })

@chat_bp.route("/sections", methods=["GET"])
def get_sections():
    return jsonify({
        "total_sections": len(sections),
        "sections": sections
    })


def format_response(law, mode="short"):
    content = law["content"]

    if mode == "short":
        return content[:200] + "..." if len(content) > 200 else content

    if mode == "medium":
        return content[:500] + "..." if len(content) > 500 else content

    return content