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
