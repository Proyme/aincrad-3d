from gradio_client import Client

for sp in ["trellis-community/TRELLIS", "JeffreyXiang/TRELLIS", "cavargas10/TRELLIS"]:
    print("=" * 60)
    print("SPACE:", sp)
    try:
        c = Client(sp, verbose=False)
        api = c.view_api(return_format="str")
        # n'affiche que les lignes des endpoints
        for line in str(api).splitlines():
            if "api_name=" in line:
                print("  ", line.strip()[:160])
    except Exception as e:
        print("  ECHEC:", type(e).__name__, str(e)[:160])
