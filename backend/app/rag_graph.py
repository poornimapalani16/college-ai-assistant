"""
LangGraph-orchestrated RAG pipeline.

Graph shape:

    [rewrite_query] -> [retrieve] -> [generate_answer] -> END

- rewrite_query: folds recent chat history into a standalone search query
  (handles follow-ups like "what about for postgrad?" after a fees question).
- retrieve: similarity search against ChromaDB, returns top-k chunks.
- generate_answer: calls Gemini with a strict "answer only from context"
  system prompt, streams back an answer + which chunks it actually used.

Conversation memory is kept per session_id in an in-memory dict for this
reference implementation. Swap `SESSION_STORE` for Redis/Postgres to make
it durable across server restarts / multiple instances.
"""
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.config import settings
from app.vectorstore import get_vectorstore

SESSION_STORE: dict[str, list] = {}  # session_id -> list of {role, content}
MAX_HISTORY_TURNS = 6


class RAGState(TypedDict):
    question: str
    session_id: str
    role: str  # student | parent | faculty | admin
    chat_history: List[dict]
    standalone_query: str
    retrieved_chunks: List[dict]
    answer: str


def _get_llm(temperature: float = 0.2):
    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your .env file or Render "
            "environment variables before calling the /api/chat endpoint."
        )
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=temperature,
    )


def rewrite_query_node(state: RAGState) -> RAGState:
    history = state["chat_history"][-MAX_HISTORY_TURNS:]
    if not history:
        state["standalone_query"] = state["question"]
        return state

    history_text = "\n".join(f"{h['role']}: {h['content']}" for h in history)
    llm = _get_llm(temperature=0)
    prompt = (
        "Rewrite the LATEST user question into a fully standalone question "
        "that makes sense without the chat history, resolving pronouns and "
        "implicit references. Only output the rewritten question, nothing else.\n\n"
        f"Chat history:\n{history_text}\n\nLatest question: {state['question']}"
    )
    try:
        result = llm.invoke([HumanMessage(content=prompt)])
        state["standalone_query"] = result.content.strip() or state["question"]
    except Exception:
        state["standalone_query"] = state["question"]
    return state


def retrieve_node(state: RAGState) -> RAGState:
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_relevance_scores(
        state["standalone_query"], k=settings.TOP_K
    )
    chunks = []
    for doc, score in results:
        chunks.append({
            "document_name": doc.metadata.get("filename", "Unknown document"),
            "page": doc.metadata.get("page"),
            "snippet": doc.page_content,
            "score": round(float(score), 3),
        })
    state["retrieved_chunks"] = chunks
    return state


ROLE_FRAMING = {
    "student": "The user is a STUDENT. Prioritize academics, attendance, exams, fees, hostel, library, placements, scholarships.",
    "parent": "The user is a PARENT. Prioritize fee structure, admissions process, hostel/safety, bus routes, and contact info. Use clear, non-jargon language.",
    "faculty": "The user is FACULTY. Prioritize academic calendar, timetables, department policies, and examination/evaluation guidelines.",
    "admin": "The user is ADMINISTRATIVE STAFF. Prioritize policy/process precision.",
}


def generate_answer_node(state: RAGState) -> RAGState:
    llm = _get_llm(temperature=0.2)
    chunks = state["retrieved_chunks"]

    if not chunks or all(c["score"] < 0.15 for c in chunks):
        state["answer"] = (
            "I couldn't find this in the official documents I have indexed. "
            "Please check with the relevant office or ask an admin to upload "
            "the document that covers this topic."
        )
        return state

    context_block = "\n\n".join(
        f"[Source {i+1}: {c['document_name']}"
        + (f", page {c['page']}" if c['page'] is not None else "")
        + f"]\n{c['snippet']}"
        for i, c in enumerate(chunks)
    )

    system_prompt = (
        "You are the official College AI Assistant. Answer ONLY using the "
        "provided context from official college documents. If the context "
        "does not contain the answer, say so plainly and suggest who to "
        "contact - never invent policies, fees, or dates. Always cite which "
        "Source number(s) you used inline, like (Source 1). Be concise and "
        "structure multi-part answers with bullet points.\n\n"
        f"{ROLE_FRAMING.get(state['role'], ROLE_FRAMING['student'])}\n\n"
        f"CONTEXT:\n{context_block}"
    )

    messages = [SystemMessage(content=system_prompt)]
    for h in state["chat_history"][-MAX_HISTORY_TURNS:]:
        cls = HumanMessage if h["role"] == "user" else AIMessage
        messages.append(cls(content=h["content"]))
    messages.append(HumanMessage(content=state["question"]))

    result = llm.invoke(messages)
    state["answer"] = result.content
    return state


def build_graph():
    graph = StateGraph(RAGState)
    graph.add_node("rewrite_query", rewrite_query_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate_answer", generate_answer_node)

    graph.set_entry_point("rewrite_query")
    graph.add_edge("rewrite_query", "retrieve")
    graph.add_edge("retrieve", "generate_answer")
    graph.add_edge("generate_answer", END)
    return graph.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run_chat(question: str, session_id: str, role: str = "student") -> dict:
    history = SESSION_STORE.get(session_id, [])

    initial_state: RAGState = {
        "question": question,
        "session_id": session_id,
        "role": role,
        "chat_history": history,
        "standalone_query": "",
        "retrieved_chunks": [],
        "answer": "",
    }

    graph = get_graph()
    final_state = graph.invoke(initial_state)

    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": final_state["answer"]})
    SESSION_STORE[session_id] = history[-(MAX_HISTORY_TURNS * 2):]

    return {
        "answer": final_state["answer"],
        "sources": final_state["retrieved_chunks"],
    }
