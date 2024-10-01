import redis
import psycopg2
import json
import time


# Step 1: Connect to Redis
def get_redis_connection():
    try:
        return redis.StrictRedis(host='localhost', port=5432, db=0)
    except redis.ConnectionError as e:
        print(f"Could not connect to Redis: {e}")
        return None


# Step 2: Connect to PostgreSQL
def get_postgres_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="psql"
        )
        return connection
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return None


# Function to process tasks from Redis
def process_tasks():
    cache = get_redis_connection()
    if not cache:
        return  # Exit if Redis connection failed

    while True:
        try:
            task_data = cache.lpop('task_queue')  # Pop task from Redis
            if task_data:
                task_data = json.loads(task_data)  # Deserialize task data
                task = task_data['task']
                print(f"Processing Task: {task}")
                response = f"Processed: {task}"  # Simulate processing response

                # Save response to PostgreSQL
                connection = get_postgres_connection()
                if connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE user SET response = %s, status = %s WHERE task = %s",
                            (response, 'submitted', task)
                        )
                        connection.commit()
                    connection.close()
                else:
                    print("Failed to connect to PostgreSQL.")
            else:
                time.sleep(1)  # Sleep to prevent tight loop
        except redis.ConnectionError as e:
            print(f"Redis connection error: {e}")
            time.sleep(5)  # Wait before retrying
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)  # Wait before retrying


if __name__ == "__main__":
    process_tasks()
