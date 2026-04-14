"""
chain.py
────────
Builds the final prompt from retrieved context + user question,
calls the OpenAI chat API, and returns a structured response.
"""

import os
from typing import List, Dict

from openai import OpenAI
from dotenv import load_dotenv

from retriever import Retriever

load_dotenv()

CHAT_MODEL  = "gpt-3.5-turbo"
MAX_TOKENS  = 600
TEMPERATURE = 0.2     # low temp = factual, consistent answers

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a knowledgeable automotive finance assistant for a dealership finance department.
You help customers and finance staff understand loan terms, rates, eligibility, fees, and processes.

INSTRUCTIONS:
- Answer questions ONLY using the provided context from our finance documents.
- Be specific: quote rates, dollar amounts, and percentages directly from the context.
- If the context does not contain enough information to answer, say so clearly — do not invent numbers.
- Keep answers concise but complete. Use bullet points for lists of conditions or requirements.
- Always mention which document or source supports your answer when relevant.
- Do not give personal financial advice — direct complex situations to a finance manager."""


def build_prompt(question: str, context: str) -> List[Dict]:
    """
    Constructs the message list for the chat completion API.
    Separates system instructions from the user-facing context+question.
    """
    user_message = f"""Use the following excerpts from our automotive finance documents to answer the question.

CONTEXT:
{context}

QUESTION: {question}

Answer based strictly on the context above."""

    return [
        {"role": "system",  "content": SYSTEM_PROMPT},
        {"role": "user",    "content": user_message},
    ]


def answer(
    question: str,
    retriever: Retriever,
    k: int = 3,
    chat_history: List[Dict] = None
) -> Dict:
    """
    Full RAG chain: retrieve → prompt → generate.

    Args:
        question:     User's natural language question
        retriever:    Loaded Retriever instance
        k:            Number of chunks to retrieve
        chat_history: Optional list of prior {role, content} turns

    Returns dict with:
        answer        — LLM-generated response string
        sources       — list of retrieved chunk metadata
        context_used  — the formatted context fed to LLM
    """
    # 1. Retrieve relevant chunks
    results = retriever.search(question, k=k)
    context = retriever.format_context(results)

    # 2. Build messages
    messages = build_prompt(question, context)

    # 3. Inject conversation history (multi-turn support)
    if chat_history:
        # Insert history between system prompt and current question
        messages = [messages[0]] + chat_history + [messages[1]]

    # 4. Call LLM
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )

    answer_text = response.choices[0].message.content.strip()

    return {
        "answer":       answer_text,
        "sources":      results,
        "context_used": context,
        "model":        response.model,
        "usage":        {
            "prompt_tokens":     response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens":      response.usage.total_tokens,
        }
    }


# ── Quick CLI test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    retriever = Retriever()

    questions = [
        "What APR will I get on a new car with a 760 credit score and 60-month term?",
        "What is the late payment fee and grace period?",
        "Do I need GAP insurance?",
    ]

    for q in questions:
        print(f"\n{'='*65}")
        print(f"Q: {q}")
        print('='*65)
        result = answer(q, retriever)
        print(f"A: {result['answer']}")
        print(f"\nSources used:")
        for s in result["sources"]:
            print(f"  [{s['rank']}] {s['source_name']}  (score={s['score']:.4f})")
        print(f"\nTokens: {result['usage']['total_tokens']}")
