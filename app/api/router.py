from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/offers/{client_id}")
def get_offers(client_id: int):
    return {
        "client_id": client_id,
        "offers": [],
        "message": "placeholder — will return proactive offers",
    }


@api_router.post("/events")
def post_event(event: dict):
    return {"received": event, "message": "placeholder — will trigger rule engine"}


@api_router.post("/offers/{offer_id}/feedback")
def post_feedback(offer_id: int, feedback: dict):
    return {"offer_id": offer_id, "feedback": feedback, "message": "placeholder"}
