#!/cm/local/apps/python39/bin/python
import sys
import time
import paramiko
import subprocess
import os

#Should move the below credentials to environment or other solution
pdu_ip = "192.168.1.1"
USERNAME = "xxx"
PASSWORD = "xxx"
outlet_id = 1
pdu_id = 4
powerFile = '/var/spool/cmd/cmdaemon.power.example.dat'

# Simulated power state storage
power_states = {}

def control_pdu(action, hostname):
    # Build the command dynamically
    COMMANDS = {
        "ON": f"dev outlet {outlet_id} {pdu_id} on",
        "OFF": f"dev outlet {outlet_id} {pdu_id} off",
        "RESET": f"dev outlet {outlet_id} {pdu_id} reboot"
    }

    command = COMMANDS[action]
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=pdu_ip, username=USERNAME, password=PASSWORD)
        
        # Use interactive shell
        shell = ssh.invoke_shell()
        shell.send(f"{command}\n")
        time.sleep(2)  # Allow the command to execute
        
        # Read output
        #output = shell.recv(65535).decode()
        #print(f"Output:\n{output}")

        ssh.close()
        if action == 'ON' or 'OFF':
            _changeStatus_(action, hostname)
            sys.exit(0)
        else:
            sys.exit(0)
        
    except paramiko.AuthenticationException:
        sys.exit(1)
    except paramiko.SSHException as ssh_error:
        sys.exit(1)
    except Exception as e:
        sys.exit(1)

def get_status(hostname):
    try:
        with open(powerFile, 'r') as file:
            for line in file:
                # Split each line into hostname and status
                parts = line.strip().split()
                if len(parts) == 2:
                    current_hostname, status = parts
                    if current_hostname == hostname:
                        print(status)
                        sys.exit(0)
    except FileNotFoundError:
        sys.exit(1)

def set_power(action, hostname):
    if hostname in power_states:
        control_pdu(action, hostname)

def reset_power(hostname):
    if hostname in power_states:
        power_states[hostname] = "OFF"
        time.sleep(3)  # Simulate delay
        power_states[hostname] = "ON"
        sys.exit(0)
    sys.exit(1)

def main():
    if len(sys.argv) < 3:
        print("arguments input error")
        sys.exit(1)

    #verify the position of the arguments and the hostname

    action = sys.argv[1].upper()
    hostname = sys.argv[2]
    
    #Determine the action and operation

    if action == "STATUS":
        get_status(hostname) #Function get_status
    elif action in ["ON", "OFF", "RESET"]:
        set_power(action, hostname)  #Function set_power
    else:
        sys.exit(1)

def _changeStatus_(afterStatus, hostname):
    try:
        with open(powerFile, 'r') as file:
            power_states = file.readlines()
            
            updated_lines = []
            for line in power_states:
                parts = line.strip().split()
                if len(parts) == 2:
                    current_hostname, status = parts
                    if hostname == current_hostname and afterStatus != status:
                        updated_lines.append(f"{hostname} {afterStatus}\n")
                        print (status, '->', afterStatus)
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
            
            with open(powerFile, 'w') as file:
                file.writelines(updated_lines)
                
    except Exception as e:
        sys.exit(1)
        

if __name__ == "__main__":
    try:
        with open(powerFile, 'r') as file:
            power_states = file.read()
    
    except PermissionError:
        sys.exit(1)
    except FileNotFoundError:
        sys.exit(1)
    except Exception as e:
        sys.exit(1)
        
    main()
