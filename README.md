This exercise is designed to help us evaluate your backend engineering skills, focusing on API design, concurrency handling, and problem-solving in a distributed environment.

The goal is to create a minimal URL shortener service that meets the outlined requirements. You are encouraged to spend a couple of hours on this, aiming for a functional MVP that you’ll demonstrate and discuss during your technical interview.

---

### **Project Description**

Implement a URL shortener service that exposes the following API endpoints:

- **`POST /url/shorten`**  
  Accepts a full URL (e.g., `https://www.reevv.com`) and returns a shortened URL (e.g., `http://localhost:8000/r/abc`).  
  - Input: JSON payload containing the `url` key
  - Output: JSON response with the `short_url` key, e.g., `{"short_url": "http://localhost:8000/r/abc"}`

- **`GET /r/<short_url>`**  
  Resolves the short URL to its original form.  
  - Output: HTTP 302 redirect to the original URL or 404 if the short URL is unknown.

### **Core Requirements**

1. **Data Persistence Across Instances**  
   The shortened URL should be retrievable from any instance of the service. For example, if a URL is shortened via one instance, it should be accessible from other instances. 

2. **Concurrency and Multiple Workers**  
   Design the service to handle multiple workers. For this, a distributed database or persistent storage is recommended.

3. **Performance and Scalability**  
   Use an efficient method for generating unique short URLs, keeping in mind scalability if the service were to grow over time.

4. **API Specifications**  
   Adhere to HTTP standards, including correct status codes and error messages.

### **Additional if you have time**

- **Custom Short URLs**: Allow users to specify a custom short URL slug (e.g., `/r/my-custom-url`).
- **Expiration**: Add an expiration mechanism for short URLs (e.g., URLs expire after a specified duration).
- **Analytics**: Include a tracking mechanism to record how many times each short URL is accessed.
- **Rate Limiting**: Prevent abuse by limiting the rate of URL shortening requests per user or IP address.

### **Creating venv**

python -m venv env_env
new_env\Scripts\activate ==> Windows
source env/bin/activate ==> Mac or Linux
pip install -r requirements.txt
deactivate

### **Runnthe app** ======> uvicorn app.main:app --reload

### **Process To Testing the APIs TESTING INSTRUCTIONS**

1. Sign-Up (POST)
   url = http://127.0.0.1:8000/url/signup
   Request = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "yourpassword"
    }

2. Log-in (POST)
   url = http://127.0.0.1:8000/url/login/
   Request = {
        "username": "testuser",
        "password": "yourpassword"
    }

3. URL shorten (Bearer Token Required) (POST)
   a. Auto-generate Slug
      url = http://127.0.0.1:8000/url/shorten
      Request = {
        "url": "https://github.com/ReevvResearch/Backend-Test"
      }

   b. Custom-generate Slug
      url = http://127.0.0.1:8000/url/shorten
      Request = {
        "url": "https://github.com/ReevvResearch/Backend-Test",
        "slug": "tyghTREGH789675"
      }

4. Actual URL (GET)
   url = http://localhost:8000/r/{slug}

5. Expiration ==> After 1hr URL can not be accessed 
