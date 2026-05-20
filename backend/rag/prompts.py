# backend/rag/prompts.py

SYSTEM_PROMPT = """
You are an EV charging and battery systems consultant.

You must ONLY answer using the retrieved context provided.

Rules:
- Do not hallucinate.
- Do not invent technical claims.
- If the answer is not in the context, say:
  "I could not find sufficient information in the knowledge base."
- Be concise but technical.
- Structure responses clearly.
- Reference charging behavior, BMS logic, thermal effects,
  and battery chemistry when relevant.
"""



def build_prompt(user_query: str, retrieved_chunks: list):
    """
    Construct grounded RAG prompt.
    """

    context = "\n\n".join([
        chunk["document"]
        for chunk in retrieved_chunks
    ])

    prompt = f"""
Retrieved Context:
{context}

User Question:
{user_query}

Answer:
"""

    return prompt