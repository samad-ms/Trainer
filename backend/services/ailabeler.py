import openai
import os
import re
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client (modern approach)
client = openai.OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

def get_suggestion_from_vectorstore(question, vectorstore, top_k=3):
    """Query Chroma vector store and generate a suitable answer using the retrieved context."""
    # Get similar passages
    results = vectorstore.similarity_search(question, k=top_k)
    if not results:
        return "No suggestion found."

    # Combine retrieved contexts
    context = "\n".join([doc.page_content for doc in results])
    
    # Create prompt for GPT to generate answer
    prompt = f"""Based on the following context, provide a concise and relevant answer to the question.
    Question: {question}
    Context: {context}
    Answer:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200,
        )
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        return f"Error generating answer: {str(e)}"

def label_transcript_utterances(transcript):
    
    try:
        vector_store = load_vector_store("/Users/basilrayees/Documents/iocod/hackathon/AI_Sales_Trainer/backend/chroma_db")
    except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            vector_store = None
    """
    Uses OpenAI to split the transcript into utterances and label each as 'Prospect' or 'Rep'.
    Returns a list of dicts: [{'speaker': 'Prospect'/'Rep'/'Unknown', 'text': ...}, ...]
    """
    if not transcript or not transcript.strip():
        print("Error: Empty transcript provided")
        return []
    
    prompt = (
    "Split the transcript into short utterances and label each utterance as either Rep (salesperson) or Prospect (customer).\n"
    "- Rep is selling or offering a product/service.\n" 
    "- Prospect is the customer asking questions or responding.\n"
    "**Use only the exact text from the transcript. Do not paraphrase, summarize, or invent new lines.**\n"
    "Format: [Label] Utterance\n\n"
    f"Transcript:\n{transcript}\n\n"
    "Labeled Utterances:"
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fixed model name - gpt-4.1-nano doesn't exist
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1500  # Increased token limit
        )
        
        text = response.choices[0].message.content.strip()
        print("OpenAI response:")
        print(text)
        print("-" * 50)
        
        utterances = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
                
            # More flexible regex pattern
            match = re.match(r"^\d+\.\s*\[(\w+)\]\s*(.+)", line)
            if match:
                speaker, utterance = match.groups()
                utterances.append({'speaker': speaker, 'text': utterance.strip()})
            else:
                # Try alternative format without numbering
                alt_match = re.match(r"^\[(\w+)\]\s*(.+)", line)
                if alt_match:
                    speaker, utterance = alt_match.groups()
                    utterances.append({'speaker': speaker, 'text': utterance.strip()})
        
        print(f"Extracted {len(utterances)} labeled utterances:")
        # Load vector store outside the loop
        

        for i, item in enumerate(utterances, 1):
            if item['speaker'].lower() == 'prospect':
                item['prospect'] = True
                # Get suggestion from Chroma DB for prospect's text
                if vector_store:
                    try:
                        suggestion = get_suggestion_from_vectorstore(item['text'], vector_store)
                        item['suggestion'] = suggestion
                    except Exception as e:
                        item['suggestion'] = f"Error getting suggestion from vector store: {str(e)}"
                else:
                    item['suggestion'] = "Vector store not available"

            print(f"{i}. [{item['speaker']}] {item['text']}")
            if 'suggestion' in item:
                print(f"   Suggestion: {item['suggestion']}")
            print(f"{i}. [{item['speaker']}] {item['text']}")
        print("-" * 50)


        
        return utterances
        
    except Exception as e:
        print(f"Error in label_transcript_utterances: {str(e)}")
        return []


def extract_prospect_questions_from_labels(labeled_utterances):
    """
    Uses OpenAI to extract all explicit and implicit questions from the prospect's utterances.
    Returns a list of question strings.
    """
    if not labeled_utterances:
        print("No labeled utterances provided")
        return []
    
    prospect_utterances = [item['text'] for item in labeled_utterances if item['speaker'].lower() == 'prospect']
    
    if not prospect_utterances:
        print("No prospect utterances found")
        return []
    
    joined = "\n".join(f"- {utterance}" for utterance in prospect_utterances)
    
    prompt = (
        "Below are utterances from a prospect in a sales call. "
        "Identify all explicit and implicit questions the prospect is asking, even if they are not phrased as a question or do not end with a question mark. "
        "For example, statements like 'I'm not sure about the pricing' should become 'What is the pricing?'. "
        "Return each question as a separate line starting with a dash (-). "
        "If there are no questions, return 'No questions found'.\n\n"
        f"Prospect Utterances:\n{joined}\n\n"
        "Extracted Questions:"
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=800
        )
        
        text = response.choices[0].message.content.strip()
        print("Questions extraction response:")
        print(text)
        print("-" * 50)
        
        if "no questions found" in text.lower():
            return []
        
        questions = []
        for line in text.splitlines():
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line)):
                # Clean up the question text
                question = re.sub(r'^[-•\d\.\s]+', '', line).strip()
                if question:
                    questions.append(question)
        
        print(f"Extracted {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}")
        print("-" * 50)
        
        return questions
        
    except Exception as e:
        print(f"Error in extract_prospect_questions_from_labels: {str(e)}")
        return []


# Example usage and testing function
def test_transcript_analysis(sample_transcript):
    """Test function to demonstrate usage"""
    print("Starting transcript analysis...")
    print("=" * 60)
    
    # Step 1: Label utterances
    labeled_utterances = label_transcript_utterances(sample_transcript)
    
    if not labeled_utterances:
        print("Failed to extract labeled utterances")
        return
    
    # Step 2: Extract questions
    questions = extract_prospect_questions_from_labels(labeled_utterances)
    
    print("FINAL RESULTS:")
    print("=" * 30)
    print(f"Total utterances: {len(labeled_utterances)}")
    print(f"Prospect questions found: {len(questions)}")
    
    return {
        'labeled_utterances': labeled_utterances,
        'prospect_questions': questions
    }


# Example usage
if __name__ == "__main__":
    # Test with sample transcript
    sample_transcript = """
    Hello, this is John from XYZ Company calling about our software solution.
    Hi John, I'm interested but I have some concerns about the cost.
    I understand your concern. Let me explain our pricing structure.
    How does your software compare to competitors?
    That's a great question. Our software offers unique features like...
    I'm not sure if this fits our budget. What's the minimum commitment?
    """
    
    results = test_transcript_analysis(sample_transcript)



# import openai
# import os
# import re
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


def load_vector_store(persist_directory="/Users/basilrayees/Documents/iocod/hackathon/AI_Sales_Trainer/backend/chroma_db"):
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    return vector_store

