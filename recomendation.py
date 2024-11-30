# >>>>  Reading the Dataset

from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS # reco
from pyspark.ml.evaluation import RegressionEvaluator # reco
from pyspark.sql import functions as F # reco
# Initialize a Spark session
spark = SparkSession.builder.appName("BookRecommendation").getOrCreate()

# Load the datasets (CSV, JSON, etc.)
books_df = spark.read.csv("/home/sreelakshmi/Videos/chatbot/dataset/books_of_the_decade.csv", header=True, inferSchema=True)
reviews_df = spark.read.csv("/home/sreelakshmi/Videos/chatbot/dataset/user_reviews_dataset.csv", header=True, inferSchema=True)

# Show a few records
books_df.show(5)
reviews_df.show(5)

# >>>> Data Preprocessing

# Handling missing values
books_df = books_df.na.drop()
reviews_df = reviews_df.na.drop()

# Aggregating the ratings and number of votes for each book
aggregated_reviews = reviews_df.groupBy("bookIndex").agg({
    "score": "mean",  # Calculate the average score (rating)
    "score": "count"  # Calculate the total number of reviews
}).withColumnRenamed("avg(score)", "average_score").withColumnRenamed("count(score)", "review_count")

# Join with books dataset to get the details
book_ratings = books_df.join(aggregated_reviews, books_df.Index == aggregated_reviews.bookIndex)
book_ratings.show(5)

# >>>> Recommendation System


# Preparing the data for the ALS algorithm
training_data = reviews_df.select("userId", "bookIndex", "score")

# Initialize the ALS model
als = ALS(
    maxIter=10, 
    regParam=0.1, 
    userCol="userId", 
    itemCol="bookIndex", 
    ratingCol="score", 
    coldStartStrategy="drop"
)

# Fit the model to the training data
model = als.fit(training_data)

# Generate top 10 book recommendations for each user
user_recommendations = model.recommendForAllUsers(10)
user_recommendations.show(5)