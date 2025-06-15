import groq
import os
from dotenv import load_dotenv
import retriever
import traceback  # 👈 added for error trace

load_dotenv()

def get_groq_client():
    """Initialize Groq client with robust error handling"""
    try:
        api_key = os.getenv("GROQ_API_KEY", "your_fallback_key_here")
        print(f"✅ Loaded GROQ_API_KEY: {api_key[:6]}...")  # Masked for security
        return groq.Client(
            api_key=api_key,
            timeout=30.0
        )
    except Exception as e:
        print(f"❌ Error initializing Groq client: {e}")
        raise

client = get_groq_client()

def generate_response(user_query, user_data=None, top_k=3):
    """Generate response with error handling"""
    try:
        print(f"\n📥 Query received: {user_query}")
        
        retrieved_context = retriever.retrieve_similar(user_query, top_k=top_k)
        print(f"📄 Retrieved context:\n{retrieved_context}")

        prompt = f"""Context information:
        {retrieved_context}

        User question: {user_query}

        Please provide a concise and accurate answer based on the context above."""

        print("📤 Sending request to Groq API...")
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a concise marketing assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=120,
            top_p=0.8,
        )

        print("✅ Groq response object received.")
        print(response)  # 👈 print full response for inspection

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"❌ Exception while generating response: {e}")
        traceback.print_exc()  # 👈 show full error trace
        return "Sorry, I encountered an error processing your request."
