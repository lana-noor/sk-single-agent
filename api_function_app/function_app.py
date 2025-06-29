import azure.functions as func
import os
import json
import logging

app = func.FunctionApp()

@app.route(route="seaworld_shops_inventory", auth_level=func.AuthLevel.ANONYMOUS)
def seaworld_shops_inventory_new(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Serving Seaworld Shops Inventory JSON data.')

    # Always use the path relative to this script
    json_path = os.path.join(os.path.dirname(__file__), "seaworld_shops_inventory.json")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return func.HttpResponse(
            json.dumps(data, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error loading JSON: {e}")
        return func.HttpResponse(
            f"Error loading inventory data: {e}",
            status_code=500
        )
