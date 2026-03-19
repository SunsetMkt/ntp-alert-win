import argparse
import logging
import math
import time

import ntplib
import windows_toasts

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_ntp_time(ntp_server="time.cloudflare.com"):
    client = ntplib.NTPClient()
    response = client.request(ntp_server, version=3)
    return response.tx_time


def send_toast(title, messages):
    # Prepare the toaster for bread (or your notification)
    toaster = windows_toasts.WindowsToaster(title)
    # Initialise the toast
    newToast = windows_toasts.Toast()
    # Set the body of the notification
    newToast.text_fields = messages  # ["Hello", "World"]
    # And display it!
    toaster.show_toast(newToast)


def time_diff(expected_time, current_time):
    return expected_time - current_time


def machine_time():
    return time.time()


def check_time(expected_time, current_time, tolerance):
    return math.fabs(time_diff(expected_time, current_time)) < tolerance


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="time.cloudflare.com", help="NTP server")
    parser.add_argument("--interval", default=30, help="Check interval in seconds")
    parser.add_argument("--tolerance", default=10, help="Tolerance in seconds")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    config_info = f"Server: {args.server}, Interval: {args.interval}s, Tolerance: {args.tolerance}s, Once: {args.once}"

    logging.info(config_info)

    while True:
        try:
            expected_time = get_ntp_time(args.server)
            current_time = machine_time()

            logging.info(
                f"Expected time: {expected_time}, Current time: {current_time}"
            )

            if check_time(expected_time, current_time, args.tolerance) == False:
                msg = f"Time is off by {time_diff(expected_time, current_time)} seconds"
                logging.info(msg)
                send_toast("NTP Alert (ntp_alert_win)", [msg, config_info])
        except Exception as e:
            logging.error(e)

        if args.once:
            logging.info("Exiting")
            break

        time.sleep(args.interval)
