from fastapi import Query
from db.models import Fetch_ended_truth, TimeGenResponse
from datetime import datetime, timezone, timedelta

def update_if_changed(model_instance, data: dict):
    changed = False
    for key, new_value in data.items():
        if hasattr(model_instance, key):
            current_value = getattr(model_instance, key)
            if current_value != new_value:
                print(f"changed:{current_value} to {new_value}")
                setattr(model_instance, key, new_value)
                changed = True
                
    return changed


def fetchEnded(fe: bool=Query(False, description="Fetched ended auctions")):
    return Fetch_ended_truth(truth=fe)

async def generate_auction_times(duration: int):
    x = 0  
    y = duration
    time_now = datetime.now(timezone.utc) + timedelta(minutes=x)

    time_future = datetime.now(timezone.utc) + timedelta(minutes=y)
    return TimeGenResponse(starting_time=time_now, ending_time=time_future)
