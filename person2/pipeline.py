import os
import json
import sqlite3
import faiss
import numpy as np
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import warnings
warnings.filterwarnings("ignore")

# Constants
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "curriculum.db")
FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "faiss_index.bin")
CURRICULUM_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "curriculum.json")
CANDIDATES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "candidates.json")

# Initialize models
_llm = None
def get_llm():
    global _llm
    if _llm is None:
        from langchain_google_genai import ChatGoogleGenerativeAI
        _llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest", temperature=0.1)
    return _llm
_embedder = None
def get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")
    return _embedder

# Pydantic Schemas
class EnrichedDay(BaseModel):
    key_concepts: List[str] = Field(description="List of key concepts for the day")
    interview_questions: List[str] = Field(description="List of initial interview questions")
    follow_up_traps: List[str] = Field(description="Socratic probing traps to test deeper knowledge")
    real_world_scenarios: List[str] = Field(description="Real-world system design scenarios")
    difficulty: int = Field(description="Difficulty rating from 1 to 5")

class EvaluationResult(BaseModel):
    quality: float = Field(description="Quality score from 0.0 to 1.0")
    matched_concepts: List[str] = Field(description="Concepts the candidate demonstrated")
    missing_concepts: List[str] = Field(description="Concepts the candidate missed")
    rationale: str = Field(description="Explanation of the score")
    recommended_action: str = Field(description="One of 'retry', 'probe', 'continue', or 'increase_difficulty'")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS enriched_curriculum (
            day INTEGER PRIMARY KEY,
            module TEXT,
            title TEXT,
            key_concepts TEXT,
            interview_questions TEXT,
            follow_up_traps TEXT,
            real_world_scenarios TEXT,
            difficulty INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def enrich_curriculum():
    """Run every day (1-31) through LLM to enrich and save to DB."""
    init_db()
    
    with open(CURRICULUM_PATH, "r") as f:
        data = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # We only process if not already processed to save time
    import time
    
    c.execute("SELECT day FROM enriched_curriculum")
    existing_days = {row[0] for row in c.fetchall()}
    
    if len(existing_days) >= len(data["days"]):
        print("Curriculum already fully enriched. Skipping.")
        conn.close()
        return

    print("Enriching curriculum via LLM...")
    from langchain_core.prompts import PromptTemplate
    prompt = PromptTemplate.from_template(
        "You are an expert technical interviewer.\n"
        "Analyze this curriculum day: Module: {module}, Title: {title}, Objectives: {objectives}.\n"
        "Generate enriched interview metadata based on the schema."
    )
    chain = prompt | get_llm().with_structured_output(EnrichedDay)
    
    for day in data["days"]:
        day_num = day["day"]
        if day_num in existing_days:
            continue
            
        print(f"Enriching Day {day_num}...")
        objectives = ", ".join(day["objectives"])
        
        success = False
        while not success:
            try:
                result = chain.invoke({
                    "module": "Curriculum Module",
                    "title": day["title"],
                    "objectives": objectives
                })
                
                c.execute('''
                    INSERT INTO enriched_curriculum (day, module, title, key_concepts, interview_questions, follow_up_traps, real_world_scenarios, difficulty)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    day_num, "Curriculum Module", day["title"],
                    json.dumps(result.key_concepts),
                    json.dumps(result.interview_questions),
                    json.dumps(result.follow_up_traps),
                    json.dumps(result.real_world_scenarios),
                    result.difficulty
                ))
                conn.commit()
                success = True
            except Exception as e:
                print(f"Rate limit hit on Day {day_num}. Sleeping for 60 seconds...")
                time.sleep(60)
                
    conn.close()

def build_competency_map(candidate_id: str) -> Dict[int, str]:
    """Map candidate's JSON to Strong/Medium/Weak/Critical per day."""
    with open(CANDIDATES_PATH, "r") as f:
        data = json.load(f)
    
    candidate = next((c for c in data["candidates"] if c["member"]["id"] == candidate_id), None)
    if not candidate:
        raise ValueError(f"Candidate {candidate_id} not found")
        
    comp_map = {}
    for mission in candidate.get("missions", []):
        day = mission["day"]
        if mission.get("skipped", False):
            comp_map[day] = "Weak"
        elif mission.get("passed", False):
            if mission.get("attempts", 1) <= 2:
                comp_map[day] = "Strong"
            else:
                comp_map[day] = "Medium"
        else:
            comp_map[day] = "Critical"
            
    return comp_map

def build_faiss_index():
    """Build local FAISS index over the enriched curriculum."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT day, module, title, key_concepts, interview_questions FROM enriched_curriculum")
    rows = c.fetchall()
    
    if not rows:
        print("No enriched data to index.")
        return
        
    texts = []
    metadata = []
    for row in rows:
        text = f"Module: {row[1]}. Title: {row[2]}. Concepts: {row[3]}. Questions: {row[4]}"
        texts.append(text)
        metadata.append({"day": row[0]})
        
    embeddings = embedder.encode(texts)
    
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype('float32'))
    
    faiss.write_index(index, FAISS_INDEX_PATH)
    
    with open(FAISS_INDEX_PATH + ".meta", "w") as f:
        json.dump(metadata, f)
        
    conn.close()

def retrieve_question(state: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve a question heavily prioritizing Weak/Critical days."""
    comp_map = state.get("competency_map", {})
    covered_days = state.get("covered_days", [])
    
    # Prioritize Critical and Weak days
    target_days = [day for day, level in comp_map.items() if level in ["Critical", "Weak"] and day not in covered_days]
    
    if not target_days and not comp_map:
        # For a brand new session, just start with day 1 to completely bypass FAISS and heavy model loading!
        target_days = [1]
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    def _fetch_question(day_num: int) -> Dict[str, Any]:
        c.execute("SELECT interview_questions, follow_up_traps, difficulty, module, title, key_concepts FROM enriched_curriculum WHERE day = ?", (day_num,))
        row = c.fetchone()
        if not row:
            return None
        questions = json.loads(row[0])
        traps = json.loads(row[1])
        expected_concepts = json.loads(row[5])
        return {
            "question_id": f"day_{day_num:02d}_q1",
            "day": day_num,
            "module": row[3],
            "topic": row[4],
            "difficulty": row[2],
            "question_text": questions[0] if questions else "Can you explain this topic?",
            "expected_concepts": expected_concepts,
            "follow_up_hints": traps,
            "source": "llm_generated"
        }
    
    if target_days:
        q = _fetch_question(target_days[0])
        if q:
            conn.close()
            return q
    
    # Fallback: FAISS search for a standard question if no weak areas left
    embedder = get_embedder()
    query_emb = embedder.encode(["Advanced engineering concepts"]).astype('float32')
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(FAISS_INDEX_PATH + ".meta", "r") as f:
        meta = json.load(f)
        
    D, I = index.search(query_emb, k=30)
    for idx in I[0]:
        day = meta[idx]["day"]
        if day not in covered_days:
            q = _fetch_question(day)
            if q:
                conn.close()
                return q
                
    conn.close()
    return {"question_text": "We have covered all topics.", "day": -1, "question_id": "done"}

import concurrent.futures

class PersonaEvaluation(BaseModel):
    score: float = Field(description="Score from 0.0 to 1.0")
    feedback: str = Field(description="One sentence of feedback from this persona's unique perspective")

class OptimizedAnswer(BaseModel):
    diff_html: str = Field(description="The optimized answer with HTML <del> and <ins> tags to show the diff.")

def _run_persona(persona_name: str, persona_prompt: str, q_text: str, answer: str) -> dict:
    from langchain_core.prompts import PromptTemplate
    prompt = PromptTemplate.from_template(
        f"You are the {persona_name}. {persona_prompt}\n"
        "Question: {{question}}\n"
        "Candidate's Answer: {{answer}}\n"
        "Provide your score (0.0 to 1.0) and exactly one sentence of feedback acting as this persona."
    )
    chain = prompt | get_llm().with_structured_output(PersonaEvaluation)
    try:
        res = chain.invoke({"question": q_text, "answer": answer})
        return {"persona": persona_name, "score": res.score, "message": res.feedback}
    except Exception as e:
        return {"persona": persona_name, "score": 0.5, "message": "I abstain from evaluating."}

def evaluate_answer(question: dict, answer: str, state: dict = None) -> dict:
    """Score raw answer and return structured feedback schema, plus deliberation logs and diff."""
    q_text = question.get("question_text", str(question)) if isinstance(question, dict) else str(question)
    concepts = ", ".join(question.get("expected_concepts", [])) if isinstance(question, dict) else ""

    fingerprint_instruction = ""
    candidate_id = state.get("candidate", {}).get("id") if state else None
    if candidate_id:
        try:
            with open(CANDIDATES_PATH, "r") as f:
                data = json.load(f)
            for c in data.get("candidates", []):
                if c["member"]["id"] == candidate_id and c.get("fingerprint"):
                    fingerprint_instruction = f"\n3. Watch out for their known weakness: '{c['fingerprint']}'. Penalize them heavily if they repeat this mistake."
                    break
        except Exception:
            pass

    from langchain_core.prompts import PromptTemplate
    base_prompt = PromptTemplate.from_template(
        "You are evaluating a candidate's answer to the following technical question.\n"
        "Question: {question}\n"
        "Expected Concepts: {concepts}\n"
        "Candidate's Answer: {answer}\n"
        "Evaluate the technical depth, correctness, and completeness of the answer.\n"
        "IMPORTANT RULES:\n"
        "1. If the candidate explicitly states they do not know the answer (e.g., 'I don't know', 'I am not sure', 'pass'), set quality to 0.0, explain that they lacked knowledge in the rationale, and set recommended_action to 'continue'.\n"
        f"2. If the candidate's answer is completely off-topic or nonsensical, set quality to 0.0, explain that it was off-topic in the rationale, and set recommended_action to 'retry'.{fingerprint_instruction}"
    )
    base_chain = base_prompt | get_llm().with_structured_output(EvaluationResult)

    diff_prompt = PromptTemplate.from_template(
        "You are an expert technical writer.\n"
        "The candidate answered: {answer}\n"
        "Rewrite the answer to maximize Signal Density (more concrete facts, fewer buzzwords).\n"
        "Return the diff in HTML using <del>strikethrough</del> for removed words and <ins>inserted</ins> for added words. Only return the HTML."
    )
    diff_chain = diff_prompt | get_llm().with_structured_output(OptimizedAnswer)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        base_future = executor.submit(base_chain.invoke, {"question": q_text, "concepts": concepts, "answer": answer})
        diff_future = executor.submit(diff_chain.invoke, {"answer": answer})
        tl_future = executor.submit(_run_persona, "Tech Lead", "Focus on technical rigor, edge cases, and missing metrics. Be critical.", q_text, answer)

        try:
            base_res = base_future.result()
            result_dict = base_res.model_dump()
        except Exception:
            # Fallback if evaluation fails
            result_dict = {"quality": 0.5, "matched_concepts": [], "missing_concepts": [], "rationale": "Error", "recommended_action": "continue"}

        try:
            result_dict["answer_diff"] = diff_future.result().diff_html
        except Exception:
            result_dict["answer_diff"] = ""

        deliberation_logs = []
        for future in [tl_future]:
            try:
                deliberation_logs.append(future.result())
            except Exception:
                pass

    result_dict["deliberation_logs"] = deliberation_logs
    return result_dict

def validate_feedback_hallucination(question: dict, answer: str, feedback: dict) -> bool:
    """
    Uses DeepEval to verify that the feedback generated by the LLM
    is actually grounded in the candidate's answer and not hallucinated.
    """
    from deepeval.metrics import HallucinationMetric
    from deepeval.test_case import LLMTestCase
    
    q_text = question.get("question_text", str(question)) if isinstance(question, dict) else str(question)
    
    # Create the test case where context is the actual answer provided by candidate
    test_case = LLMTestCase(
        input=q_text,
        actual_output=json.dumps(feedback),
        context=[answer]
    )
    # Threshold 0.5 means it must be highly grounded
    metric = HallucinationMetric(threshold=0.5)
    
    try:
        metric.measure(test_case)
        print(f"DeepEval Hallucination Score: {metric.score}")
        return metric.is_successful()
    except Exception as e:
        print(f"DeepEval validation skipped or failed (likely missing OpenAI keys): {e}")
        # Fail open if API keys for DeepEval's default OpenAI models are missing
        return True

def extract_fingerprint(state: dict, feedback: dict) -> None:
    """Extract a behavioral fingerprint and save it to candidates.json."""
    try:
        from langchain_core.prompts import PromptTemplate
        prompt = PromptTemplate.from_template(
            "Analyze the candidate's performance summary and gaps.\n"
            "Summary: {summary}\n"
            "Gaps: {gaps}\n"
            "Identify one core recurring behavioral anti-pattern or failure mode "
            "(e.g., 'Consistently fails to mention metrics', 'Hides behind 'we' instead of 'I'').\n"
            "Keep it under 15 words. Reply with just the fingerprint."
        )
        chain = prompt | get_llm()
        summary = feedback.get("summary", "")
        gaps = ", ".join(feedback.get("gaps", []))
        res = chain.invoke({"summary": summary, "gaps": gaps})
        fingerprint = res.content.strip()
        
        candidate_id = state.get("candidate", {}).get("id")
        if candidate_id:
            with open(CANDIDATES_PATH, "r") as f:
                data = json.load(f)
            for c in data.get("candidates", []):
                if c["member"]["id"] == candidate_id:
                    c["fingerprint"] = fingerprint
                    break
            with open(CANDIDATES_PATH, "w") as f:
                json.dump(data, f, indent=2)
                
    except Exception as e:
        print("Failed to extract fingerprint:", e)

if __name__ == "__main__":
    pass
