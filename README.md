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

6. Every time any changes is made in the any app file or somehow the app gets reloaded, login is required
