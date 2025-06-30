import azure.functions as func
import os
import json
import logging

app = func.FunctionApp()

@app.route(route="shops_inventory", auth_level=func.AuthLevel.ANONYMOUS)
def seaworld_shops_inventory_final(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Serving Shops Inventory JSON data.')

    # Always use the path relative to this script
    json_path = os.path.join(os.path.dirname(__file__), "shops_inventory.json")

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


@app.route(route="shops_inventory_final", auth_level=func.AuthLevel.ANONYMOUS)
def seaworld_shops_inventory_final(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )