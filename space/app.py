"""Manual one-call demo. No load-time API calls or timer that inflate usage."""
import json
import os
import urllib.request
import urllib.error
import gradio as gr


def load_levels():
    headers = {"Accept": "application/json", "User-Agent": "hunterkiller-space/0.1.0"}
    if os.environ.get("HK_INTERNAL_PROBE") == "1":
        headers["X-HK-Probe"] = "1"
    request = urllib.request.Request("https://hunterkiller.io/api/v1/levels/BTCUSDT", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.load(response)
        if data.get("ok") is not True:
            raise ValueError("The API did not return levels")
    except (urllib.error.URLError, ValueError) as exc:
        raise gr.Error("No ladder returned. " + str(exc)) from None
    rows = [[w.get(k) for k in ("side", "price", "usd", "distance_pct", "evidence")]
            for w in data.get("walls", [])]
    status = (f"Snapshot {data.get('as_of_iso')}. Age {data.get('age_sec')} seconds. "
              f"Tier {data.get('tier')}. Delay {data.get('delay_sec')} seconds.")
    return rows, status, data


with gr.Blocks() as demo:
    gr.Markdown("# Hunter Killer liquidation walls\nFree data is 2 hours behind on six coins. "
                "This demo reads BTCUSDT. No orders. Descriptive data, not advice. "
                "[Public record](https://hunterkiller.io/proof).")
    button = gr.Button("Read BTC walls")
    status = gr.Textbox(label="Snapshot and delay", interactive=False)
    ladder = gr.Dataframe(headers=["Side", "Price", "USD", "Distance pct", "Evidence"], interactive=False)
    raw = gr.JSON(label="Unchanged source response")
    button.click(load_levels, outputs=[ladder, status, raw], api_name=False, concurrency_limit=1)

if __name__ == "__main__":
    demo.launch()
