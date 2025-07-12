import ray, sys, logging, math, time, os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_ray():
    for _ in range(5):
        try:
            addr = os.getenv("RAY_ADDRESS", "ray://ray-head:10001")
            ray.init(address=addr)
            logger.info(f"Connected to Ray: {ray.cluster_resources()}")
            return
        except Exception as e:
            logger.error(f"Ray init failed: {str(e)}")
            time.sleep(3)
    raise Exception("Ray init failed")

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0: return False
    print(f"Found prime: {n}")
    return True

@ray.remote(num_cpus=1)
def find_primes(start, end):
    return [n for n in range(max(2, start), end + 1) if is_prime(n)]

def main(start=1000, batches=4, size=1000):
    logger.info(f"Starting from {start}, batches={batches}, size={size}")
    init_ray()
    ranges = [(start + i * size, start + (i + 1) * size - 1) for i in range(batches)]
    futures = [find_primes.remote(s, e) for s, e in ranges]
    primes = sorted([p for r in ray.get(futures) for p in r])
    logger.info(f"Found {len(primes)} primes: {primes[:10]}{'...' if len(primes) > 10 else ''}")
    ray.shutdown()
    time.sleep(10)

if __name__ == "__main__":
    try:
        args = [int(arg) for arg in sys.argv[1:4] if arg.isdigit()]
        if len(args) < 3:
            env = lambda k, d: int(os.getenv(k, d))
            args = [env("START_NUMBER", 1000), env("NUM_BATCHES", 4), env("BATCH_SIZE", 1000)]
        s, b, z = args
        if s < 0 or b < 1 or z < 1: s, b, z = 1000, 4, 1000
        main(s, b, z)
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        main()
