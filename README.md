# Locum Genius AI 🧠

A premium RAG-based assistant for UK locum optometrists, powered by Google Gemini 2.5 Flash-Lite.

## Features
- **Knowledge-Grounded Chat**: Specialized in UK optical chains (Boots, Costco, etc.) and clinical guidelines.
- **Full RAG Pipeline**: Built with Gemini File Search.
- **Premium UI**: Clean, professional white-and-blue interface.

## Local Setup
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your `GOOGLE_API_KEY` to a `.env` file.
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Live Deployment
This app is designed to run on **Streamlit Community Cloud**. 
- Secrets: Ensure `GOOGLE_API_KEY` is added to your app's Secrets section.
