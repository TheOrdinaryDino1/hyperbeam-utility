import os
import requests
import subprocess


def get_vm_sessions(api_key):
    url = "https://engine.hyperbeam.com/v0/vm"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()["results"]
    else:
        print(f"Error: {response.status_code}")
        return None


def terminate_vm(api_key, session_id):
    url = f"https://engine.hyperbeam.com/v0/vm/{session_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print(f"Session ID {session_id} terminated successfully.")
    else:
        print(f"Error: {response.status_code}")


def main():
    api_key = os.getenv("CHILDREN")
    if not api_key:
        print("API key not found. Please set the environment variable 'CHILDREN'.")
        return

    vm_sessions = get_vm_sessions(api_key)

    if vm_sessions is not None:
        print("Existing VM Sessions:")
        for index, session in enumerate(vm_sessions):
            print(f"{index + 1}. ID: {session['id']}")

        session_choice = input(
            "Enter the number of the session you want to terminate (0 to cancel): "
        )

        try:
            session_index = int(session_choice) - 1
            if session_index == -1:
                print("Termination canceled.")
            elif 0 <= session_index < len(vm_sessions):
                session_id = vm_sessions[session_index]["id"]
                confirmation = input(
                    f"Are you sure you want to terminate session ID {session_id}? (Y/N): "
                )
                if confirmation.upper() == "Y":
                    terminate_vm(api_key, session_id)
                else:
                    print("Termination canceled.")
            else:
                print("Invalid session number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


if __name__ == "__main__":
    main()

subprocess.run(["python", "main.py"])

