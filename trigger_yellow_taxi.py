import requests
import time

MAGE_TRIGGER_URL = "http://localhost:6789/api/pipeline_schedules/1/pipeline_runs/461d0bd40f4f495a9f91dcbe7d970f22"
HEADERS = {"Content-Type": "application/json"}


def trigger_pipeline(service, year, month):
    data = {
        "pipeline_run": {
            "variables": {
                "service_type": service,  
                "year": year,
                "month": f"{month:02d}",
            }
        }
    }
    response = requests.post(MAGE_TRIGGER_URL, headers=HEADERS, json=data)
    if response.status_code == 200:
        run_info = response.json()
        run_id = run_info.get("pipeline_run", {}).get("id")
        print(f" Triggered {service} {year}-{month:02d} | run_id={run_id}")
        return run_id
    else:
        print(f" Error {response.status_code}: {response.text}")
        return None


def wait_for_completion(run_id, poll_interval=30):
    status_url = f"http://localhost:6789/api/pipeline_runs/{run_id}"
    while True:
        r = requests.get(status_url, headers=HEADERS)
        if r.status_code != 200:
            print(f" Error consultando estado: {r.status_code}")
            time.sleep(poll_interval)
            continue

        status = r.json().get("pipeline_run", {}).get("status")
        print(f" Run {run_id} estado={status}")
        if status in ["completed", "failed", "canceled"]:
            return status
        time.sleep(poll_interval)


def main():
    service = "yellow"
    year = 2024

    for month in range(1, 13):
        run_id = trigger_pipeline(service, year, month)
        if run_id:
            status = wait_for_completion(run_id)
            print(f" Run {run_id} terminó con estado {status}")
        else:
            print(" No se pudo disparar el pipeline, saltando al siguiente mes.")

if __name__ == "__main__":
    main()