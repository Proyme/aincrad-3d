from gradio_client import Client
c = Client("trellis-community/TRELLIS", verbose=False)
api = c.view_api(return_format="dict")
for name, info in api.get("named_endpoints", {}).items():
    ps = ", ".join(p.get("parameter_name", p.get("label", "?")) for p in info.get("parameters", []))
    print(f"{name}  ->  ({ps})")
