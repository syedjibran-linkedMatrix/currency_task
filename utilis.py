import requests

def retry_on_failure(max_retries=3):
    """Decorator to retry a function call a specified number of times on failure."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    last_exception = e
                    print(f"Attempt {attempt + 1} failed: {e}")
            print(f"All {max_retries} attempts failed.")
            raise last_exception  # Raise the last exception after all attempts fail
        return wrapper
    return decorator
