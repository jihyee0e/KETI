# 함수 하나를 여러 개 동시에 실행하면 진짜 병렬로 돌아가는지
import ray  # 병렬/분산 처리를 위한 핵심 라이브러리
import datetime
import time

# Ray 시스템 초기화
ray.init(include_dashboard=True, dashboard_port=8265)  # 백그라운드에서 여러 워커 프로세스가 실행 & 대시보드 서버도 함께 뜸
# -> 초기화하면 http://127.0.0.1:8265에서 실행 상태를 확인

@ray.remote  # 다른 프로세스에서 병렬로 실행 가능하도록 만들기 위한 Ray 데코레이터
def print_current_time():
    time.sleep(0.3)  # 0.3초 대기, 일부러 지연을 줘서 병렬 실행 여부를 눈에 띄게 하려는 의도
    current_datetime = datetime.datetime.now()  # 현재 시간 가져오기
    print(current_datetime)  # 현재 시간 출력
    return current_datetime  # 현재 시간 반환

if __name__ == "__main__":  
    # 4개의 작업을 병렬로 실행 -> 즉시 실행x 미래에 결과를 주겠다는 객체 반환
    futures = [print_current_time.remote() for _ in range(4)]  # .remote()를 붙여야 Ray()가 병렬로 실행
    results = ray.get(futures)  # 병렬로 실행된 작업 결과 모아서 실제값으로 동기적으로 가져옴
    print("결과: ", results)