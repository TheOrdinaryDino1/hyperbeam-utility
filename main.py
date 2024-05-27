import requests
import threading
import webbrowser
import os
import http.server
import socketserver
import subprocess
import os

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'about_blank_embed.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def serve_html(server_reference, port):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler_object = MyHttpRequestHandler
    with socketserver.TCPServer(("0.0.0.0", port), handler_object) as httpd:
        server_reference['server'] = httpd
        print(f"Serving at port {port}")
        httpd.serve_forever()

def stop_server(server_reference):
    if 'server' in server_reference and server_reference['server']:
        server_reference['server'].shutdown()
        server_reference['server'].server_close()
        print("Previous server stopped.")

def open_about_blank(embed_link, server_reference):
    html_content = f"""
    <html>
      <head>
      </head>
      <body>
        <script>
          var url = "{embed_link}";
          var isInIFrame = window.self !== window.top;
          if (isInIFrame) {{
            alert("You are viewing this page in an embedded frame. For the best experience, please open it in a separate browser tab.");
          }} else {{
            if (url) {{
              var win = window.open();
              win.document.body.style.margin = '0';
              win.document.body.style.height = '100vh';
              var iframe = win.document.createElement('iframe');
              iframe.style.border = 'none';
              iframe.style.width = '100%';
              iframe.style.height = '100%';
              iframe.style.margin = '0';
              iframe.src = url;
              win.document.body.appendChild(iframe);
            }}
          }}
        </script>
      </body>
    </html>
    """
    with open("about_blank_embed.html", "w") as f:
        f.write(html_content)
    stop_server(server_reference)
    port = 8000
    while True:
        try:
            server_thread = threading.Thread(target=serve_html, args=(server_reference, port))
            server_thread.start()
            webbrowser.open(f"http://localhost:{port}")
            break
        except OSError:
            print(f"Port {port} is in use. Trying next port...")
            port += 1

def get_vm_sessions(api_key):
    url = "https://engine.hyperbeam.com/v0/vm"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        print(f"Error: {response.status_code}")
        return None

def login_to_vm(api_key, session_id):
    url = f"https://engine.hyperbeam.com/v0/vm/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        embed_url = data["embed_url"]
        print("Login successful!")
        print(f"Session ID: {session_id}")
        print(f"Embed URL: {embed_url}")
        return embed_url
    else:
        print(f"Error: {response.status_code}")
        return None

def delete_vm(session_id):
    try:
        subprocess.run(["python", "arm.py", session_id], check=True)
        print(f"VM with session ID {session_id} deleted successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error running arm.py: {e}")

def run_create_script():
    try:
        subprocess.run(["python", "backup.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running backup.py: {e}")

def run_remove_script():
    try:
        subprocess.run(["python", "arm.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running arm.py: {e}")

def main():
    api_key = os.getenv("CHILDREN")
    if not api_key:
        print("Replit secret key not found. Please set the environment variable 'CHILDREN'.")
        return

    server_reference = {}
    vm_sessions = get_vm_sessions(api_key)
    if vm_sessions is not None:
        print("Existing VM Sessions:")
        for index, session in enumerate(vm_sessions):
            print(f"{index + 1}. ID: {session['id']}")
        print("Select an option:")
        print("1. Login to a VM")
        print("2. Delete a VM")
        print("3. Create a VM")
        option = input()
        if option == "1":
            session_choice = input("Enter the number of the session you want to login to: ")
            try:
                session_index = int(session_choice) - 1
                if 0 <= session_index < len(vm_sessions):
                    session_id = vm_sessions[session_index]["id"]
                    confirmation = input(f"Are you sure you want to login to session ID {session_id}? (Y/N): ")
                    if confirmation.upper() == "Y":
                        embed_url = login_to_vm(api_key, session_id)
                        if embed_url:
                            open_about_blank(embed_url, server_reference)
                    else:
                        print("Login canceled.")
                else:
                    print("Invalid session number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif option == "2":
            run_remove_script()
        elif option == "3":
            run_create_script()
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
