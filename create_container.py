import subprocess
import json

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def is_container_running(container_name):
    result = subprocess.run(f"podman ps --filter name={container_name} --filter status=running", shell=True, capture_output=True, text=True)
    return container_name in result.stdout

def start_podman_machine():
    print("Starting podman machine 'podman-machine-default'...")
    if run_command("podman machine start podman-machine-default"):
        print("Podman machine started successfully.")
    else:
        print("Failed to start podman machine.")

def get_number_of_containers():
    while True:
        try:
            num = int(input("How many containers do you want to start? "))
            if num > 0:
                return num
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")

def get_container_names(count):
    container_names = []
    for i in range(count):
        while True:
            name = input(f"Enter name for container {i+1}: ").strip()
            if name and name not in container_names:
                container_names.append(name)
                break
            print("Please enter a unique container name.")
    return container_names

def start_container(container_name):
    print(f"Starting container '{container_name}'...")
    if run_command(f"podman run -d --name {container_name} nginx:latest"):
        print("Container started successfully.")
        return True
    print("Failed to start container.")
    return False

def stop_container(container_name):
    print(f"Stopping container '{container_name}'...")
    if run_command(f"podman stop {container_name}"):
        print("Container stopped successfully.")
        return True
    print("Failed to stop container.")
    return False

def remove_container(container_name):
    print(f"Removing container '{container_name}'...")
    if run_command(f"podman rm {container_name}"):
        print("Container removed successfully.")
        return True
    print("Failed to remove container.")
    return False

def remove_existing_containers(container_names):
    for name in container_names:
        if container_exists(name):
            stop_container(name)
            remove_container(name)

def container_exists(container_name):
    try:
        result = subprocess.run(['podman', 'ps', '-a', '--format', 'json'], capture_output=True, text=True, check=True)
        containers = json.loads(result.stdout)
        return any(container_name in container['Names'] for container in containers)
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Überprüfen des Containers: {e}")
        return False

if __name__ == "__main__":
    start_podman_machine()
    num_containers = get_number_of_containers()
    container_names = get_container_names(num_containers)
    
    remove_existing_containers(container_names)
    
    active_containers = []
    for name in container_names:
        if start_container(name):
            active_containers.append(name)
    
    if active_containers:
        print("\nActive containers:", ", ".join(active_containers))
        input("\nPress Enter to stop and remove all containers...")
        
        for name in active_containers:
            if stop_container(name):
                remove_container(name)