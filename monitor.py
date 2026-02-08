import subprocess
import json
import os
from datetime import datetime

WORKSPACE = r"C:\Users\Ashok\.openclaw\workspace\cron-dashboard"
DATA_FILE = os.path.join(WORKSPACE, "data", "status.json")

def fetch_cron_status():
    try:
        # Run openclaw cron list --json
        # Using shell=True might be safer on Windows for finding the command if it's in path
        result = subprocess.run(["openclaw", "cron", "list", "--json"], capture_output=True, text=True, check=True, shell=True)
        jobs_raw = json.loads(result.stdout)
        jobs_list = jobs_raw.get("jobs", [])
        
        normalized_jobs = []
        for job in jobs_list:
            state = job.get("state", {})
            schedule = job.get("schedule", {})
            
            # Format schedule
            if schedule.get("kind") == "every":
                ms = schedule.get("everyMs", 0)
                if ms >= 86400000:
                    sched_str = f"every {ms // 86400000}d"
                elif ms >= 3600000:
                    sched_str = f"every {ms // 3600000}h"
                elif ms >= 60000:
                    sched_str = f"every {ms // 60000}m"
                else:
                    sched_str = f"every {ms}ms"
            else:
                sched_str = f"cron {schedule.get('expr', '')}"
                if schedule.get("tz"):
                    sched_str += f" @ {schedule.get('tz')}"

            # Format times
            def format_ms(ms):
                if not ms: return "-"
                dt = datetime.fromtimestamp(ms / 1000)
                # If it's more than 24h away, show date, else show time relative or absolute
                now = datetime.now()
                diff = dt - now
                if abs(diff.total_seconds()) < 86400:
                    return dt.strftime("%H:%M:%S")
                return dt.strftime("%Y-%m-%d %H:%M")

            normalized_jobs.append({
                "id": job.get("id"),
                "name": job.get("name"),
                "status": state.get("lastStatus", "idle"),
                "schedule": sched_str,
                "next": format_ms(state.get("nextRunAtMs")),
                "last": format_ms(state.get("lastRunAtMs")),
                "agent": job.get("agentId")
            })
        
        data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "jobs": normalized_jobs
        }
        
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
            
        print(f"Successfully updated {DATA_FILE}")
    except subprocess.CalledProcessError as e:
        print(f"Error running openclaw: {e.stderr}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_cron_status()
