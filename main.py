from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

# Global dictionary to track active carts per session
inprogress_order = {}


@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()

    # Extract intent and parameters directly using bracket indexing []
    intent = payload["queryResult"]["intent"]["displayName"]
    parameters = payload["queryResult"]["parameters"]
    output_contexts = payload["queryResult"]["outputContexts"]

    # Comma unpacking for list: Extract the first context dictionary safely without brackets
    if output_contexts:
        (first_context,) = output_contexts[:1]  # Safely slices first element and unpacks it
        session_id = generic_helper.extract_session_id(first_context["name"])
    else:
        session_id = None

    # Routing table mapping
    intent_handlers = {
        "New-order": new_order,
        "Track-Order::context:ongoing-tracking": track_order,
        "Add-order::context:ongoing-order": add_order,
        "Complete-order::context:ongoing-order": complete_order,
        "Remove-order::context:ongoing-order": remove_order,
    }

    if intent in intent_handlers:
        return intent_handlers[intent](parameters, session_id)

    return JSONResponse(
        content={
            "fulfillmentText": "Sorry, I didn't understand that. Can you please rephrase?"
        }
    )


def new_order(parameters: dict, session_id: str):
    # Clean the session active cart when starting a fresh order flow
    if session_id in inprogress_order:
        del inprogress_order[session_id]

    return JSONResponse(
        content={
            "fulfillmentText": "Starting a new order! What would you like to have? You can specify items and their quantities (e.g. '2 pizzas and 1 mango lassi')."
        }
    )


def add_order(parameters: dict, session_id: str):
    food_items = parameters["Food-Item"]
    # food_items = parameters["food-Item"]
    quantities = parameters["number"]

    if not food_items or not quantities:
        return JSONResponse(
            content={
                "fulfillmentText": "Please provide both food items and their quantities."
            }
        )

    if len(food_items) != len(quantities):
        fulfilment_text = "The number of food items and quantities do not match. Please provide the same number of food items and quantities."
    else:
        try:
            quantities = [int(q) for q in quantities]
        except (ValueError, TypeError):
            return JSONResponse(
                content={
                    "fulfillmentText": "There was an issue processing your quantities. Please specify them using numbers."
                }
            )

        new_food_dict = dict(zip(food_items, quantities))

        if session_id in inprogress_order:
            inprogress_order[session_id].update(new_food_dict)
        else:
            inprogress_order[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(
            inprogress_order[session_id]
        )
        fulfilment_text = f"Current order: {order_str}. You can add more items or complete the order."

    return JSONResponse(content={"fulfillmentText": fulfilment_text})


def track_order(parameters: dict, session_id: str):
    order_id = parameters["number"]

    if order_id is None or order_id == "":
        return JSONResponse(
            content={
                "fulfillmentText": "Please provide a valid order ID so I can track your order."
            }
        )

    try:
        order_id_int = int(order_id)
    except (ValueError, TypeError):
        return JSONResponse(
            content={
                "fulfillmentText": f"The order ID '{order_id}' is invalid. Please enter a valid number."
            }
        )

    order_status = db_helper.get_order_status(order_id_int)

    if order_status:
        return JSONResponse(
            content={
                "fulfillmentText": f"Your order status for order {order_id_int} is: {order_status}"
            }
        )
    return JSONResponse(
        content={
            "fulfillmentText": f"No active order found with ID {order_id_int}."
        }
    )


def save_order_to_db(food_dict: dict):
    # Fetch next sequence order ID from database
    next_order_id = db_helper.get_next_orderid()

    # Insert individual items into the database
    for food_item, quantity in food_dict.items():
        rcode = db_helper.insert_order(food_item, quantity, next_order_id)
        if rcode == -1:
            return -1

    # Initialise the tracking status as "in progress"
    db_helper.insert_order_tracking(next_order_id, "in progress")
    return next_order_id


def complete_order(parameters: dict, session_id: str):
    if session_id in inprogress_order:
        order = inprogress_order[session_id]
        order_id = save_order_to_db(order)

        if order_id == -1:
            return JSONResponse(
                content={
                    "fulfillmentText": "There was an error saving your order. Please try again."
                }
            )
        else:
            order_total = db_helper.get_order_total(order_id)
            del inprogress_order[session_id]
            return JSONResponse(
                content={
                    "fulfillmentText": f"Your order has been completed! Your order ID is {order_id} and the total amount is ${order_total:.2f}."
                }
            )

    return JSONResponse(
        content={
            "fulfillmentText": "I'm having trouble finding your active order. Please make sure you've added items to your cart before completing the order."
        }
    )


def remove_order(parameters: dict, session_id: str):
    """Removes a list of food items from the active session cart."""
    if session_id not in inprogress_order:
        return JSONResponse(
            content={
                "fulfillmentText": "I couldn't find an active order for your session. Would you like to start a new order?"
            }
        )

    # food_items = parameters["Food-Item"]
    food_items = parameters["food-item"]
    if not food_items:
        return JSONResponse(
            content={
                "fulfillmentText": "Please specify the food items you want to remove."
            }
        )

    current_order = inprogress_order[session_id]
    removed_items = []
    no_such_items = []

    for item in food_items:
        if item in current_order:
            del current_order[item]
            removed_items.append(item)
        else:
            no_such_items.append(item)

    fulfillment_text = ""
    if removed_items:
        fulfillment_text += f"Removed {', '.join(removed_items)} from your order. "

    if no_such_items:
        fulfillment_text += (
            f"We couldn't find {', '.join(no_such_items)} in your current order. "
        )

    if len(current_order) == 0:
        fulfillment_text += "Your order is now empty!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f"Current order is: {order_str}."

    return JSONResponse(content={"fulfillmentText": fulfillment_text.strip()})