import ray

ray.init(address='http://ray-head:8265')
@ray.remote
def capitalize(text):
    return text.upper()

def main():
    frases = [f"mensaje número {i}" for i in range(100)]
    resultados = ray.get([capitalize.remote(f) for f in frases])
    for resultado in resultados[:10]:
        print(resultado)
    ray.shutdown()

if __name__ == "__main__":
    main()
