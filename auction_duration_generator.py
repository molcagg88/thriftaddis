from datetime import datetime, timedelta, timezone

# x minutes in the future
x = 15  # for example
y = 45
future_time = datetime.now(timezone.utc) + timedelta(minutes=x)

# x minutes in the past
past_time = datetime.now(timezone.utc) + timedelta(minutes=y)
print("\n")
print("start:", future_time)
print("end:", past_time)