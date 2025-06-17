import time
from concurrent.futures import ProcessPoolExecutor

# 느린 함수 정의
def slow_function(x):
    time.sleep(1)
    return x * 2

if __name__ == "__main__":
    # ===== 1. 직렬 처리 =====
    start = time.time()

    serial_results = []
    for i in range(5):
        serial_results.append(slow_function(i))

    end = time.time()
    print("직렬 처리 결과:", serial_results)
    print("직렬 처리 시간: {:.2f}초".format(end - start))

    # ===== 2. 병렬 처리 =====
    start = time.time()

    with ProcessPoolExecutor(max_workers=5) as executor:
        parallel_results = list(executor.map(slow_function, [0, 1, 2, 3, 4]))

    end = time.time()
    print("병렬 처리 결과:", parallel_results)
    print("병렬 처리 시간: {:.2f}초".format(end - start))
