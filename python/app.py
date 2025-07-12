import ray
import sys
import logging
import math
import time
import os


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Ray with retries
def init_ray():
    for attempt in range(5):
        try:
            logger.info("Attempting to connect to Ray cluster...")
            #ray.init(address='auto', ignore_reinit_error=True)
            ray_address = os.getenv("RAY_ADDRESS", "ray://ray-head:10001")
            ray.init(address=ray_address)

            logger.info(f"Connected to Ray cluster: {ray.cluster_resources()}")
            return
        except Exception as e:
            logger.error(f"Connection attempt {attempt + 1} failed: {str(e)}")
            time.sleep(3)
    raise Exception("Failed to connect to Ray cluster after 5 attempts")

# Check if a number is prime
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    print(f"Found prime: {n}")
    return True

# Remote function to find primes in a range
@ray.remote(num_cpus=1)
def find_primes_in_range(start, end):
    logger.info(f"Processing range {start} to {end}")
    primes = [n for n in range(max(2, start), end + 1) if is_prime(n)]
    return primes

def main(start_number=1000, num_batches=4, batch_size=1000):
    logger.info(f"Starting prime calculation from {start_number}, {num_batches} batches, size {batch_size}")
    try:
        init_ray()
        # Create ranges for batches
        ranges = [(start_number + i * batch_size, start_number + (i + 1) * batch_size - 1) for i in range(num_batches)]
        logger.info(f"Batch ranges: {ranges}")
        
        # Distribute tasks
        futures = [find_primes_in_range.remote(start, end) for start, end in ranges]
        results = ray.get(futures)
        
        # Combine results
        all_primes = sorted([prime for batch in results for prime in batch])
        logger.info(f"Found {len(all_primes)} primes: {all_primes[:10]}{'...' if len(all_primes) > 10 else ''}")
        logger.info(f"Total primes: {len(all_primes)}")
    except Exception as e:
        logger.error(f"Error in computation: {str(e)}")
    finally:
        ray.shutdown()
        logger.info("Ray shutdown")
        time.sleep(10)  # Ensure logs are captured


if __name__ == "__main__":
    try:
        # Use defaults if arguments are missing or invalid
        try:
            start_number = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1
            num_batches = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 20
            batch_size = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 1_00
            logger.info("Usando argumentos desde línea de comandos")
        except IndexError:
            start_number_ = int(os.getenv("START_NUMBER", 1))
            num_batches_ = int(os.getenv("NUM_BATCHES", 20))
            batch_size_ = int(os.getenv("BATCH_SIZE", 100))
            logger.info("Usando argumentos desde variables de entorno")
        
        # Validate arguments
        if start_number < 0 or num_batches < 1 or batch_size < 1:
            logger.error("Arguments must be positive integers; using defaults")
            start_number, num_batches, batch_size = 1, 20, 100
        
        logger.info(f"Using arguments: start_number={start_number}, num_batches={num_batches}, batch_size={batch_size}")
        main(start_number, num_batches, batch_size)
    except Exception as e:
        logger.error(f"Invalid arguments: {str(e)}; using defaults")
        main()
