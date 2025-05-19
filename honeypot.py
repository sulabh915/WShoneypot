import argparse
import os
import shutil
from ssh_honeypot import honeypot as ssh_honeypot
from web_honeypot import run_web_honeypot



def main():

    parser = argparse.ArgumentParser(
        description="Unified Honeypot Launcher",
        epilog="Examples:\n  python honeypot.py -s -a 0.0.0.0 -p 2223 -u root -w toor\n  python honeypot.py -wh -a 0.0.0.0 -p 5000",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-a', '--address', type=str, required=True, help="IP address to bind")
    parser.add_argument('-p', '--port', type=int, required=True, help="Port to bind")
    parser.add_argument('-u', '--username', type=str, help="Username for honeypot auth")
    parser.add_argument('-w', '--password', type=str, help="Password for honeypot auth")
    parser.add_argument('-s', '--ssh', action='store_true', help="Run SSH honeypot")
    parser.add_argument('-wh', '--http', action='store_true', help="Run HTTP WordPress honeypot")

    args = parser.parse_args()

    if not args.ssh and not args.http:
        print("[!] ERROR: You must specify one honeypot to launch with --ssh or --http.")
        parser.print_help()
        return

    if args.ssh and args.http:
        print("[!] ERROR: You cannot run both SSH and HTTP honeypots simultaneously.")
        return

    try:
        if args.ssh:
            if not args.username or not args.password:
                print("[!] SSH honeypot requires --username and --password.")
                return

            print("[-] Launching SSH Honeypot...")
            ssh_honeypot(args.address, args.port, args.username, args.password)

        elif args.http:
            username = args.username or 'admin'
            password = args.password or 'deeboodah'

            print("[-] Launching HTTP Honeypot...")
            run_web_honeypot(port=args.port, input_username=username, input_password=password)

    except KeyboardInterrupt:
        print("\n[!] Honeypot terminated.")

   


if __name__ == "__main__":
    main()

