import requests

BASE_URL = "http://localhost:8000"

def shorten_url(original_url: str) -> str:
    """Send a request to shorten a URL."""
    response = requests.post(f"{BASE_URL}/url/shorten", json={"url": original_url})
    if response.status_code == 200:
        short_url = response.json().get("short_url")
        print(f"Shortened URL: {short_url} {response.status_code}")
        return short_url
    else:
        print(f"Error shortening URL: {response.status_code}")
        return None

def get_original_url(short_url: str) -> str:
    """Send a request to retrieve the original URL from a shortened URL."""
    response = requests.get(f"{BASE_URL}/r/{short_url}")
    print(response.url)
    if response.status_code == 302:
        original_url = response.url  # Redirects give the target URL in response.url
        print(f"Original URL: {original_url} {response.status_code}")
        return original_url
    elif response.status_code == 404:
        print(f"Error: Short URL not found. {response.status_code}")
        return None
    else:
        print(f"Error retrieving original URL: {response.status_code}")
        return None

# Example usage
if __name__ == "__main__":
    # Shorten a URL
    short_url = shorten_url("https://github.com/DopplerHQ/awesome-interview-questions?tab=readme-ov-file#database-technologies")

    # Get the original URL
    if short_url:
        get_original_url(short_url.split("/")[-1])  # Pass only the short URL part
