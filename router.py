import cmd
import os
import time
import re
import shlex

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
ENDC = '\033[0m'

class RouterState:
    def __init__(self):
        self.motd = "Welcome to the TRANSIT Cisco router. Please play nice."
        self.banner = "This system is for authorized users only."
        self.user_credentials = {'cisco': 'cisco'}
        self.enable_password = "cisco"
        self.user_logged_in = False
        self.privileged_mode = False
        self.config_mode = False
        self.hostname = "TRANSIT-router"
        
        self.command_outputs = {
            "show running-config": "\n".join([
                "HOSTNAME - Transit Router - 192.168.168.250",
                "Building configuration...",
                "version 12.4",
                "!",
                "hostname transit-router",
                "enable secret 5 $1$uEIa$nW34Vk0vqYqLTDjgwKUgP/",
                "enable password cisco",
                "!",
                "interface FastEthernet0/1",
                "ip address 192.168.168.250 255.255.255.0",
                "speed auto",
                "full-duplex",
                "snmp-server community public RO",
                "snmp-server community private RW",
                "!",
                "line con 0",
                "line aux 0",
                "line vty 0 4",
                "password cisco",
                "login",
                "!",
                "end"
            ]),
            "ip default-gateway 192.168.168.1": "gateway set to 192.168.168.1",
            "show version": "\n".join([
                "Cisco IOS Software, 2801 Software, Version 12.4(15)T10",
                "Copyright (c) 1986-2009 by Cisco Systems, Inc.",
                "Compiled Mon 14-Sep-09 14:49 by prod_rel_team",
                "---------------------------------------------",
                "ROM: System Bootstrap, Version 12.4(13r)T, RELEASE SOFTWARE (fc1)",
                "---------------------------------------------",
                "transit-router uptime is 21 minutes",
                "System returned to ROM by power-on",
                "System image file is flash:c2801-ipbase-mz.124-15.T10.bin",
                "---------------------------------------------",
                "Cisco 2801 (revision 7.0) with 352256K/40960K bytes of memory.",
                "Processor board ID FCZ140671LQ",
                "2 FastEthernet interfaces",
                "DRAM configuration is 64 bits wide with parity disabled.",
                "191K bytes of NVRAM.",
                "126000K bytes of ATA CompactFlash (Read/Write)",
                "--",
                "Configuration register is 0x2102"
            ]),
            "ip address 192.168.168.250 255.255.255.0": "FastEthernet 0/1 set",
            "interface FastEthernet": "Change to the relevant FE interface",
            "ping": "Sends ICMP echo requests to a network host - try pinging .1",
            "ping 192.168.168.1": "",
            "write mem": "",
            "cdp run": "Enables CDP (Cisco Discovery Protocol).",
            "show arp": "\n".join([
                "Protocol  Address          Age (min)  Hardware Addr   Type   Interface",
                "Internet  192.168.168.1          53   5070.4347.2c19  ARPA   FastEthernet0/1",
                "Internet  192.168.168.49          0   c03e.baaf.5435  ARPA   FastEthernet0/1",
                "Internet  192.168.168.200        45   ecc8.82da.bcc0  ARPA   FastEthernet0/1",
                "Internet  192.168.168.250         -   0064.4014.428b  ARPA   FastEthernet0/1"
            ]),
            "show mac address-table": "\n".join([
                "Mac Address Table",
                "-------------------------------------------",
                "Vlan    Mac Address       Type        Ports",
                "192.168.168.14           ether   46:72:9e:54:6b:50   C                     eno3",
                "192.168.168.107          ether   08:00:27:4e:27:e9   C                     eno3",
                "192.168.168.6            ether   08:12:a5:9a:00:fa   C                     eno3",
                "192.168.168.79           ether   5c:62:8b:a1:1c:c3   C                     eno3"
            ]),
            "show cdp": "\n".join([
                "Global CDP information:",
                "Sending CDP packets every 60 seconds",
                "Sending a holdtime value of 180 seconds",
                "Sending CDPv2 advertisements is enabled"
            ]),
            "show vlan": "Displays VLAN information.  Try 'show vlan brief'",
            "show vlan brief": "\n".join([
                "VLAN Name        Status    Ports",
                "--------- -------------------------------",
                "3    Finance     active    Fa0/1, Fa0/2,",
                " ",
                "1002 fddi-default          act/unsup",
                "1003 token-ring-default    act/unsup",
                "1004 fddinet-default       act/unsup"
            ]),
            "show vtp status": "\n".join([
                "VTP Version                     : 2",
                "Configuration Revision          : 0",
                "Maximum VLANs supported locally : 19",
                "Number of existing VLANs        : 5",
                "VTP Operating Mode              : Server",
                "VTP Domain Name                 :",
                "VTP Pruning Mode                : Disabled",
                "VTP V2 Mode                     : Disabled",
                "VTP Traps Generation            : Disabled",
                "MD5 digest                      : 0xBF 0x86 0x94 0x45 0xFC 0xDF 0xB5 0x70",
                "Configuration last modified by 0.0.0.0 at 0-0-00 00:00:00",
                "Local updater ID is 192.168.168.200 on interface Fa0/1 (first interface found)",
                "Displays VTP (VLAN Trunking Protocol) status."
            ]),
            "vlan 3": "Vlan 3 created for port.",
            "name Finance": "Vlan name Finance",
            "name": "Names the VLAN.",
            "switchport mode access": "mode set to access.",
            "switchport access vlan 3": "switchport access set.",
            "switchport trunk encapsulation dot1q": "dot1q set.",
            "switchport mode trunk": "trunk mode set.",
            "telnet 192.168.168.1": "Initiates a telnet session.",
            "enable": "",
            "line con 0": "Console port set for configuration",
            "exit": "",
            "conf t": "Enters configuration terminal mode.",
            "end": "Exits configuration terminal mode.",
            "motd play nice!": "MOTD set to good morning - play nice!",
            "banner": "Sets or displays the login banner.",
            "?": "Displays this help message.",
            "interface FastEthernet 0/2": "You have changed to interface FastEthernet 0/2.",
            "interface FastEthernet 0/1": "You have changed to interface FastEthernet 0/1.",
            "snmp-server community public RO": "Read Community String set to public - this is default!",
            "snmp-server community private RW": "Write Community String set to private - easily guessed!",
            "speed": "You have the choice of 10, 100, or AUTO",
            "speed auto": "Interface FastEthernet 0/2 set to Auto Negotiate",
            "no shut": "Interface FE 0/2 up",
            "hostname": "change the name of the router on config mode",
            "write memory": "Saves the current config - try write mem",
            "copy run start": "Saving to startup-config",
            "ip address": "ip address <address> <Subnet> this one is 192.168.168.250",
            "motd": "sets the MOTD - motd <message> try motd play nice!",
            "password 7 cisco": "password set encrypted",
            "tftp-server 192.168.168.50": "tftp server set to 192.168.168.50",
            "line vty 0 15": "\n".join([
                "You have changed to config vty you can set a password",
                "Type password - Options are:",
                "0     Specifies an UNENCRYPTED password will follow",
                "7     Specifies a HIDDEN password will follow",
                "LINE  The UNENCRYPTED (cleartext) line password"
           ]),
        }

        self.help_descriptions = {
            "show cdp": "Displays CDP neighbors.",
            "show vlan": "Displays VLAN information.",
            "show vlan brief": "Displays a brief overview of VLANs.",
            "show vtp status": "Displays VTP (VLAN Trunking Protocol) status.",
            "vlan vlan-id": "Creates a VLAN with the specified VLAN ID.",
            "telnet 192.168.168.1": "Initiates a telnet session.",
            "enable": "Enters privileged EXEC mode.",
            "exit": "Exits the current mode or the simulator.",
            "conf t": "Enters configuration terminal mode.",
            "end": "Exits configuration terminal mode.",
            "motd": "Sets or displays the Message of the Day.",
            "banner": "Sets or displays the login banner.",
            "?": "Displays this help message.",
            "interface FastEthernet 0/2": "Changes to the relevant interface.",
            "snmp-server community public RO": "Read Community String set to public - this is default!",
            "snmp-server community private RW": "Write Community String set to private - easily guessed!",
            "speed": "You have the choice of 10, 100, or AUTO",
            "speed auto": "Interface FastEthernet 0/1 set to Auto Negotiate",
            "hostname myrouter": "hostname changed to myrouter - but not really.",
            "hostname": "Change the name of the router",
            "write memory": "Saves the configuration - try 'write mem' ",
            "copy run start": "Also saves the configuration",
            "line": "this allows you to configure different consoles CON, VTY",
            "password": "Sets a password",
            "tftp-server": "Sets the tftp-server IP and file path.",
            "switchport mode access": "mode set to access.",
            "switchport access vlan 3": "assign the switchport to a specific vlan 3",
            "switchport trunk encapsulation dot1q": "set the encapsulation type",
            "switchport mode trunk": "Set the VLAN trunk mode.",
            "name": "names the interface",
        }

    def is_user_mode(self):
        return not self.privileged_mode and not self.config_mode

    def is_privileged_mode(self):
        return self.privileged_mode and not self.config_mode

    def is_config_mode(self):
        return self.config_mode


class CiscoSimulator(cmd.Cmd):
    intro = (
        RED + "This is a confidential TRANSIT system.\n"
        "Anyone attempting to access the system without authorisation\n"
        "will be subject to the penalties of grey beards pirate kingdom\n"
        "Fair warning is given!\n" + ENDC
    )

    # Mode-based commands
    user_commands = [
        "enable", "exit", "help", "show", "ping", "?"
    ]
    privileged_commands = [
        "conf t", "end", "write mem", "copy run start", "show", "ping", "exit", "enable", "help", "?",
        "cdp run", "telnet", "line con 0", "snmp-server", "interface", "vlan", "switchport", "name", "ip address", "ip default-gateway"
    ]
    config_commands = [
        "hostname", "banner motd", "motd", "exit", "end", "write mem", "copy run start", "interface", "snmp-server", "speed", "no shut",
        "switchport mode access", "switchport access vlan 3", "switchport trunk encapsulation dot1q", "switchport mode trunk",
        "tftp-server", "password", "line", "vlan", "name"
    ]

    def __init__(self):
        super().__init__()
        self.state = RouterState()
        self.update_prompt()

    def preloop(self):
        self.clear_screen()
        self.login()

    def clear_screen(self):
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def login(self):
        username = input("Username: ")
        password = input("Password: ")
        if self.state.user_credentials.get(username) == password:
            self.state.user_logged_in = True
            print(self.state.motd)
        else:
            print("Invalid username or password. Please try again.")
            exit()

    def update_prompt(self):
        if self.state.is_config_mode():
            self.prompt = f"{self.state.hostname}(config)# "
        elif self.state.is_privileged_mode():
            self.prompt = f"{self.state.hostname}# "
        else:
            self.prompt = f"{self.state.hostname}> "

    def display_response(self, response):
        for line in response.split('\n'):
            print(line)
            time.sleep(0.1)

    def precmd(self, line):
        # Handle config mode commands with regex (hostname, banner motd, motd)
        if self.state.is_config_mode():
            if line.startswith("hostname "):
                new_host = line.split(" ", 1)[1]
                self.state.hostname = new_host
                print(f"Hostname set to {new_host}.")
                self.update_prompt()
                return ''
            elif line.startswith("banner motd "):
                # Assume banner motd "message"
                match = re.search(r'banner motd "([^"]+)"', line)
                if match:
                    msg = match.group(1)
                    self.state.banner = msg
                    print("Banner MOTD updated.")
                else:
                    print("Banner MOTD not updated. Use banner motd \"Your message\"")
                return ''
            elif line.startswith("motd "):
                # motd "message"
                match = re.search(r'motd "([^"]+)"', line)
                if match:
                    msg = match.group(1)
                    self.state.motd = msg
                    print("MOTD updated.")
                else:
                    print("MOTD not updated. Use motd \"Your message\"")
                return ''
        return line

    def default(self, line):
        line = line.strip()
        if line == '?':
            return self.do_help(line)

        # Parse line with shlex for more sophisticated argument handling
        # This helps handle quoted strings or multiple arguments
        args = shlex.split(line)

        if not args:
            return

        cmd_word = args[0]

        # Handle mode transitions
        if cmd_word == 'enable':
            return self.handle_enable()
        if cmd_word == 'conf' and len(args) > 1 and args[1] == 't':
            return self.handle_conf_t()
        if cmd_word == 'end':
            return self.handle_end()
        if cmd_word == 'exit':
            return self.handle_exit()
        if cmd_word == 'write' and len(args) > 1 and args[1] == 'mem':
            return self.handle_write_mem()
        if cmd_word == 'copy' and len(args) > 2 and args[1] == 'run' and args[2] == 'start':
            return self.handle_copy_run_start()

        # Special ping handling
        if cmd_word == 'ping':
            return self.handle_ping(args)

        # If exact command in command_outputs
        if line in self.state.command_outputs:
            resp = self.state.command_outputs[line]
            self.display_response(resp)
            return

        # Try partial matches for commands that have a known pattern
        # e.g. "show version", "show running-config"
        if cmd_word == 'show':
            # reconstruct line minus 'show'
            remainder = ' '.join(args[1:])
            candidate = f"show {remainder}"
            if candidate in self.state.command_outputs:
                resp = self.state.command_outputs[candidate]
                self.display_response(resp)
                return

        # If command not recognized
        print("Command not recognized or not implemented in this simulator.")

    def handle_enable(self):
        if not self.state.privileged_mode:
            enable_pass = input("Password: ")
            if enable_pass == self.state.enable_password:
                self.state.privileged_mode = True
                print("Privileged mode enabled.")
            else:
                print("Incorrect password.")
        else:
            print("Already in privileged mode.")
        self.update_prompt()

    def handle_conf_t(self):
        if self.state.privileged_mode:
            self.state.config_mode = True
            print("Enter configuration commands, one per line. End with CNTL/Z.")
            self.update_prompt()
        else:
            print("You must be in privileged mode to enter config mode.")

    def handle_end(self):
        if self.state.config_mode:
            self.state.config_mode = False
            self.state.privileged_mode = True
            print("Exiting configuration mode...")
            self.update_prompt()
        else:
            print("Not in configuration mode.")

    def handle_exit(self):
        if self.state.config_mode:
            self.state.config_mode = False
            self.state.privileged_mode = True
            print("Exiting configuration mode...")
            self.update_prompt()
        elif self.state.privileged_mode:
            self.state.privileged_mode = False
            print("Exiting privileged mode...")
            self.update_prompt()
        else:
            print("Exiting simulator...")
            return True

    def handle_write_mem(self):
        print("Building Configuration")
        time.sleep(3)
        print("OK")

    def handle_copy_run_start(self):
        print("Saving to startup-config")
        time.sleep(1)
        print("OK")

    def handle_ping(self, args):
        # ping <target>
        if len(args) == 2:
            target = args[1]
            print(f"Sending 5, 100-byte ICMP Echos to {target}, timeout is 2 seconds:")
            for i in range(5):
                time.sleep(0.3)
                print(f"Reply from {target}: bytes=100 time<1ms TTL=64")
        else:
            print("Usage: ping <ip_address>")

    def do_help(self, line):
        # Print help messages from help_descriptions + a few additional lines
        print("Available commands (mode-dependent):")
        # Combine all known commands from help and outputs
        all_cmds = set(list(self.state.help_descriptions.keys()) + list(self.state.command_outputs.keys()))
        for cmd in sorted(all_cmds):
            if cmd in self.state.help_descriptions:
                print(f"{cmd}: {self.state.help_descriptions[cmd]}")
            else:
                # If no description, just list the command
                print(f"{cmd}")
        print("\n'?' displays this help message.\n"
              "Use 'enable' to enter privileged mode, 'conf t' to enter config mode, 'end' or 'exit' to leave modes.")
        return

    def completedefault(self, text, line, begidx, endidx):
        # Tab completion for unknown commands
        # Based on current mode, suggest commands
        suggestions = []
        if self.state.is_config_mode():
            cmd_list = self.config_commands
        elif self.state.is_privileged_mode():
            cmd_list = self.privileged_commands
        else:
            cmd_list = self.user_commands

        # Also include any command from the command_outputs or help_descriptions that might be relevant
        # Just to ensure all known commands can be tab-completed
        extra_cmds = set(list(self.state.help_descriptions.keys()) + list(self.state.command_outputs.keys()))
        # Merge them for completion
        all_possible = set(cmd_list) | extra_cmds

        # Filter based on the text typed
        for c in all_possible:
            if c.startswith(text):
                suggestions.append(c)
        return suggestions

    def complete_show(self, text, line, begidx, endidx):
        # Specific completion for show commands
        show_cmds = [cmd for cmd in self.state.command_outputs.keys() if cmd.startswith("show ")]
        return [c.split(' ', 1)[1] for c in show_cmds if c.startswith("show " + text)]

    def completenames(self, text, line, begidx, endidx):
        # Try completing known commands (show, enable, etc.)
        # If user typed 'show' then we use complete_show
        # else we use completedefault
        if line.strip().startswith("show"):
            # after typing 'show ' we provide show subcommands
            return self.complete_show(text, line, begidx, endidx)

        return self.completedefault(text, line, begidx, endidx)

    def postcmd(self, stop, line):
        self.update_prompt()
        return stop

if __name__ == "__main__":
    CiscoSimulator().cmdloop()








