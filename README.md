# 💸 FinChain: AI Multi-Agent Financial Advisor

**FinChain** is an advanced, stateful multi-agent financial system designed to serve as a personalized, AI-driven financial advisor. By leveraging the power of **LangChain** and **LangGraph**, FinChain intelligently routes queries, analyzes portfolios, and provides actionable, goal-based financial planning.

---

## 🌟 Key Features

- **🎯 Goal-Based Financial Planning:** Tell the agent your income, expenses, and goals (e.g., buying a car, saving for retirement), and it intelligently creates personalized financial strategies.
- **📈 Market Intelligence via RAG:** Retrieves real-time context and processes vast amounts of financial data using Retrieval-Augmented Generation to provide informed advice.
- **🛡️ Risk Management Agent:** Evaluates and analyzes investment risk, providing a robust smart portfolio analyzer that tracks and scores multiple assets.
- **📊 Expense Tracking & Memory:** Maintains conversational memory to understand your financial profile across multiple interactions, adapting to your specific financial situation over time.

---

## 🛠️ Architecture & Tech Stack

FinChain is built on a modern, powerful AI stack:

- **AI Orchestration:** [LangChain](https://python.langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/)
- **LLM Engine:** Gemini 2.5 Flash (`langchain-google-genai`)
- **Vector Database:** ChromaDB
- **API Server:** FastAPI
- **Language:** Python

---

## 🚀 Getting Started

### Prerequisites

Ensure you have Python 3.9+ installed and your API keys ready (e.g., Google Gemini API key, and any financial APIs you are using).

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd financial-ai-agent
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add your keys:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   # Add any other required API keys here
   ```

### Running FinChain

To start the interactive command-line agent:

```bash
python main.py
```

*To start the FastAPI web server:*
```bash
uvicorn app:app --reload
```

---

## 📂 Project Structure

- **`/graph`**: Contains the LangGraph builder logic that orchestrates the multi-agent workflow.
- **`/Memory`**: Memory extractors and user memory management to track goals and expenses.
- **`/Tools`**: Custom LangChain tools (Investment Calculator, Portfolio Analyzer, Stock Price Fetcher, News Fetcher).
- **`/vector_db` & `/RAG`**: Storage for embeddings and RAG components using ChromaDB.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.