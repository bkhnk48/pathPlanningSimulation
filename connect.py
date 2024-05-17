import subprocess
import re
def run_command(command, shell=False, capture_output=True):
    try:
        result = subprocess.run(command, shell=shell, capture_output=capture_output, text=True, check=True)
        if capture_output:
            return result.stdout.strip()
        else:
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

def extract_time_values(output):
    s_values = []
    matches = re.finditer(r's (\d+)', output)
    for match in matches:
        s_values.append(int(match.group(1)))
    return s_values