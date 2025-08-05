from datetime import datetime, timedelta, timezone

# x minutes in the future
x = 0  # for example
y = 45
future_time = datetime.now(timezone.utc) + timedelta(minutes=x)

# x minutes in the past
past_time = datetime.now(timezone.utc) + timedelta(minutes=y)
print("\n")
print(f'"starting_time": "{future_time}", "ending_time":"{past_time}"')
