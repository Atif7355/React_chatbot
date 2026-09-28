import os
import numpy as np
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import ollama

app = FastAPI()

# 1. Initialize Embedding Model & Vector Store (In-Memory)
print("Loading embedding model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Sample documents for our RAG knowledge base
DOCUMENTS = [
    "Our company policy allows 20 days of paid time off (PTO) per year, accrued monthly.",
    "To reset your corporate VPN password, visit portal.company.com/reset or IT support.",
    "Project Orion's Q3 deliverables focus on migrating legacy databases to AWS cloud.",
    "Office snacks and catered lunches are provided every Tuesday and Thursday in the main cafeteria.",
]

# Pre-compute embeddings for documents
doc_embeddings = embedder.encode(DOCUMENTS)


def retrieve_context(query: str, top_k: int = 2) -> str:
  """Retrieve top-k relevant documents based on cosine similarity."""
  query_embedding = embedder.encode(query)
  # Calculate cosine similarity
  similarities = np.dot(doc_embeddings, query_embedding) / (
      np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding)
  )
  top_indices = np.argsort(similarities)[::-1][:top_k]
  return "\n".join([f"- {DOCUMENTS[i]}" for i in top_indices])


# 2. API Schemas & Endpoints
class ChatRequest(BaseModel):
  message: str


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
  # RAG Step 1: Retrieve context
  context = retrieve_context(req.message)

  # RAG Step 2: Construct prompt with context
  prompt = f"""You are a helpful AI assistant. Answer the user's question using ONLY the provided context below. If you do not know the answer based on the context, say "I don't know based on my documents."

Context:
{context}

User Question: {req.message}
Answer:"""

  # RAG Step 3: Generate response via Ollama (using llama3 by default)
  try:
    response = ollama.chat(
        model="llama3", messages=[{"role": "user", "content": prompt}]
    )
    answer = response["message"]["content"]
  except Exception as e:
    answer = f"Error connecting to Ollama: {str(e)}. Make sure Ollama is running."

  return {"answer": answer, "context": context}


# 3. Single-File React Frontend (Served via HTML)
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
  return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Simple RAG Chatbot</title>
        <!-- Tailwind CSS for styling -->
        <script src="https://cdn.tailwindcss.com"></script>
        <!-- React and Babel via CDN -->
        <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    </head>
    <body class="bg-gray-100 h-screen flex flex-col">
        <div id="root" class="h-full flex flex-col"></div>

        <script type="text/babel">
            function App() {
                const [messages, setMessages] = React.useState([
                    { sender: 'bot', text: 'Hello! Ask me anything about company policies, projects, or office perks.' }
                ]);
                const [input, setInput] = React.useState('');
                const [loading, setLoading] = React.useState(false);

                const sendMessage = async (e) => {
                    e.preventDefault();
                    if (!input.trim() || loading) return;

                    const userMessage = input;
                    setInput('');
                    setMessages(prev => [...prev, { sender: 'user', text: userMessage }]);
                    setLoading(true);

                    try {
                        const res = await fetch('/api/chat', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ message: userMessage })
                        });
                        const data = await res.json();
                        setMessages(prev => [...prev, { sender: 'bot', text: data.answer, context: data.context }]);
                    } catch (err) {
                        setMessages(prev => [...prev, { sender: 'bot', text: 'Error communicating with server.' }]);
                    } finally {
                        setLoading(false);
                    }
                };

                return (
                    <div className="max-w-2xl w-full mx-auto h-full flex flex-col p-4 bg-white shadow-lg">
                        <header className="border-b pb-3 mb-4">
                            <h1 className="text-xl font-bold text-gray-800">Single-File RAG Chatbot</h1>
                            <p className="text-sm text-gray-500">Powered by FastAPI, Sentence-Transformers, & Ollama</p>
                        </header>
                        
                        <div className="flex-1 overflow-y-auto space-y-4 pr-2">
                            {messages.map((msg, index) => (
                                <div key={index} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                                    <div className={`max-w-lg p-3 rounded-lg text-sm ${msg.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
                                        {msg.text}
                                    </div>
                                    {msg.context && (
                                        <div className="text-xs text-gray-400 mt-1 italic">
                                            Retrieved Context: {msg.context}
                                        </div>
                                    )}
                                </div>
                            ))}
                            {loading && <div className="text-sm text-gray-400 italic">Thinking...</div>}
                        </div>

                        <form onSubmit={sendMessage} className="mt-4 flex gap-2 border-t pt-3">
                            <input
                                type="text"
                                className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
                                placeholder="Type your question..."
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                            />
                            <button type="submit" className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700">
                                Send
                            </button>
                        </form>
                    </div>
                );
            }

            ReactDOM.createRoot(document.getElementById('root')).render(<App />);
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
  import uvicorn

  uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
  
