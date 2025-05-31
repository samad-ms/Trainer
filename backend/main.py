import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from services.transcribe import transcribe_audio
from services.summarizer import summarize_transcript
from services.ailabeler import label_transcript_utterances, extract_prospect_questions_from_labels
from services.contextual_qa import answer_question_with_context
from services.contextual_qa import answer_question_with_vector_store
from services.vectorstore import build_vector_store
from services.tts import text_to_speech_file
from services.prospect_simulator import generate_prospect_question, get_feedback
import tempfile
import os

from ws_router import ws_router

app = FastAPI()
app.include_router(ws_router)

# CORS for frontend devs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend domain in prod!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    text = transcribe_audio(tmp_path)
    os.remove(tmp_path)
    return {"transcript": text}

@app.post("/summarize")
async def summarize(transcript: str = Form(...)):
    summary = summarize_transcript(transcript)
    return {"summary": summary}

@app.post("/label")
async def label(transcript: str = Form(...)):
    utterances = label_transcript_utterances(transcript)
    return {"utterances": utterances}


@app.post("/extract_questions")
async def extract_questions(labeled_utterances: list):
    questions = extract_prospect_questions_from_labels(labeled_utterances)
    return {"questions": questions}

@app.post("/qa")
async def qa(question: str = Form(...), context: str = Form(...)):
    answer = answer_question_with_context(question, context)
    return {"answer": answer}

@app.post("/tts")
async def tts(text: str = Form(...), voice: str = Form("onyx")):
    file_path = text_to_speech_file(text, voice)
    return FileResponse(file_path, media_type="audio/mp3", filename="speech.mp3")

@app.post("/generate_prospect_question")
async def generate_prospect(conversation_history: str = Form(...), context: str = Form(None)):
    question = generate_prospect_question(conversation_history, context)
    return {"question": question}

@app.post("/get_feedback")
async def feedback(prospect_question: str = Form(...), user_answer: str = Form(...), context: str = Form(None)):
    feedback = get_feedback(prospect_question, user_answer, context)
    return {"feedback": feedback}


@app.post("/upload-knowledge-base-file")
async def upload_knowledge_base_file(file: UploadFile = File(...)):
    """
    Build vector database from uploaded file and test with sample question
    """
    try:
        content = await file.read()
        text = content.decode('utf-8')
        vector_store = build_vector_store(text)
        
        # # Test question to retrieve from vector store
        # test_question = "whats the pricing of easify"
        # test_response = answer_question_with_vector_store(test_question, vector_store)
        
        return {
            "status": "success",
            "message": "File processed and vectorized successfully",
            "filename": file.filename,
            "vectors_created": True,
            # "test_question": test_question,
            # "test_response": test_response
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
            "vectors_created": False
        }

# @app.post("/process_transcript")
# async def process_transcript(transcript: str = Form(...)):
#     result = process_transcript_and_generate_qa(transcript)
#     return result