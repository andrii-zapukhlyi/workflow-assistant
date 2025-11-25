import gradio as gr
import requests

API_URL = "http://localhost:8000/api/chat_qa"

def chat_fn(message, history):
    try:
        r = requests.post(API_URL, json={
            "user_email": "az@gmail.com",
            "query": message
        })

        if r.status_code == 200:
            response = r.json()
            answer = response.get("answer", "No answer found.")
        else:
            try:
                response = r.json()
                detail = response.get("detail", "")
                answer = detail.splitlines()[0] if detail else f"Error {r.status_code}"
            except Exception:
                answer = f"Error {r.status_code}"

    except Exception as e:
        answer = f"Unexpected error: {str(e)}"

    return answer

gr.ChatInterface(chat_fn).launch(server_name="0.0.0.0", server_port=7860, share=False)