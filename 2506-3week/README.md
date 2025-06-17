
## 📄 파일명: 0617_Ray-test.py

### ✅ 실행 순서
1. 가상환경 생성 및 실행
```bash
    python -m venv ray_env
    source ray_env/bin/activate  # Windows: ray_env\Scripts\activate
```

2. Ray 설치
```bash
    pip install -U "ray[default]"
```

3. Ray 설치 확인
```bash
    python -c "import ray; print(ray.__version__)"   # 2.46.0
```

4. 파일 실행
```bash
    python3 0617_Ray-test.py    
```

### 🔗 출력 예시

```
2025-06-17 15:07:38,358 INFO worker.py:1879 -- Started a local Ray instance. View the dashboard at 127.0.0.1:8265 
(print_current_time pid=4754) 2025-06-17 15:07:46.837682
(print_current_time pid=4756) 2025-06-17 15:07:46.837779
(print_current_time pid=4755) 2025-06-17 15:07:46.837728
(print_current_time pid=4753) 2025-06-17 15:07:46.837768
결과:  [datetime.datetime(2025, 6, 17, 15, 7, 46, 837728), 
       datetime.datetime(2025, 6, 17, 15, 7, 46, 837779), 
       datetime.datetime(2025, 6, 17, 15, 7, 46, 837682), 
       datetime.datetime(2025, 6, 17, 15, 7, 46, 837768)]
```

📌 .remote()를 통해 병렬 실행된 함수들이 거의 동시에 실행되었음을 확인할 수 있음
📌 ray.get()으로 ObjectRef에서 실제 결과를 동기적으로 수집함
📌 Dashboard는 기본적으로 http://127.0.0.1:8265에서 실행됨 (에러 발생 시 include_dashboard=False로 끌 수 있음)