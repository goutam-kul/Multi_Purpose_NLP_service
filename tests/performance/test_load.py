# Locust - Open source load testing tools written in python 
# It can simulate how real users will interact with the API
# Provide detaile statistics and graphs

from locust import HttpUser, task, between

class NLPUser(HttpUser):
    wait_time = between(1, 2)

    @task(3)  # Higher weight for sentiment analysis 
    def test_sentiment(self):
        self.client.post(
            "/api/v1/sentiment",
            json={"text": "I love this product!"}
        )
    
    @task(2)
    def test_ner(self):
        self.client.post(
            "/api/v1/ner",
            json={"text": "John works at Microsoft in Seattle"}
        )

    @task(2)
    def test_classify(self):
        self.client.post(
            "/api/v1/classify",
            json={
                "text": "Tesla announced new electric vehicle technology.",
                "options": {"multi_lable": True}
            }
        )

    @task(1)
    def test_summarization(self):
        self.client.post(
            "/api/v1/summarize",
            json={
                "text": "The quick brown fox jumps over the lazy dog." * 10,
                "options": {"max_length":10}
            }
        )