import os

import gradio as gr
import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def check_backend() -> str:
    try:
        response = httpx.get(f"{BACKEND_URL}/health", timeout=5.0)
        return f"{response.status_code} {response.text}"
    except httpx.HTTPError as exc:
        return f"unreachable: {exc}"


with gr.Blocks(title="agent-system front") as demo:
    gr.Markdown(f"# agent-system front (skeleton)\nBackend: `{BACKEND_URL}`")
    status = gr.Textbox(label="backend status", interactive=False)
    gr.Button("Check backend health").click(fn=check_backend, outputs=status)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
