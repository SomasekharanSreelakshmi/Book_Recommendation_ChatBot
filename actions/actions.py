import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List

# Initialize Spark session
spark = SparkSession.builder.appName("BookRecommendationBot").getOrCreate()

# Load book and review datasets
books_df = spark.read.csv('/home/sreelakshmi/Videos/chatbot/book/books_of_the_decade.csv', header=True, inferSchema=True)
reviews_df = spark.read.csv('/home/sreelakshmi/Videos/chatbot/book/user_reviews_dataset.csv', header=True, inferSchema=True)

class ActionRecommendBook(Action):

    def name(self) -> Text:
        return "action_recommend_book"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            # Recommend top-rated books (sorted by rating)
            top_books = books_df.orderBy(col("Rating").desc()).limit(3)
            top_books_list = top_books.collect()

            if not top_books_list:
                response = "Sorry, I couldn't find any top-rated books at the moment."
            else:
                response = "Here are some top-rated books:\n"
                for book in top_books_list:
                    response += f"{book['Book Name']} by {book['Author']} (Rating: {book['Rating']})\n"
        
        except Exception as e:
            response = "Here are some top-rated books:\n"
            
        dispatcher.utter_message(text=response)
        return []


class ActionGetBookDetails(Action):

    def name(self) -> Text:
        return "action_get_book_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the book name entity from the user's input
        book_name = next(tracker.get_latest_entity_values("book_name"), None)

        if book_name:
            # Search for the book in the dataset
            book_details = books_df.filter(col("Book Name") == book_name).collect()

            if book_details:
                book = book_details[0]
                response = f"Book: {book['Book Name']}\nAuthor: {book['Author']}\nRating: {book['Rating']}\nVotes: {book['Number of Votes']}"
            else:
                response = f"Sorry, I couldn't find any details for the book '{book_name}'."
        else:
            response = "Please provide the name of the book you'd like details for."

        dispatcher.utter_message(text=response)
        return []


class ActionGetUserReviews(Action):

    def name(self) -> Text:
        return "action_get_user_reviews"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the book name entity from the user's input
        book_name = next(tracker.get_latest_entity_values("book_name"), None)

        if book_name:
            # Find the book index using the book name
            book_data = books_df.filter(col("Book Name") == book_name).collect()
            if book_data:
                book_index = book_data[0]['Index']
                # Get user reviews based on book index
                reviews = reviews_df.filter(col("bookIndex") == book_index).collect()

                if reviews:
                    response = f"User reviews for {book_name}:\n"
                    for review in reviews:
                        response += f"User {review['userId']} gave a score of {review['score']}\n"
                else:
                    response = f"Sorry, there are no reviews available for {book_name}."
            else:
                response = f"Sorry, I couldn't find any details for the book '{book_name}'."
        else:
            response = "Please provide the name of the book you'd like reviews for."

        dispatcher.utter_message(text=response)
        return []

