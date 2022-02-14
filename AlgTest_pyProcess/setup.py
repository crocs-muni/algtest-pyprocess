import subprocess
import sys

RESULTS_REPOSITORY = "https://github.com/crocs-muni/jcalgtest_results.git"


def pip_install(pkg):
    try:
        print(f"Installing package {pkg} with pip ", end="")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        print("done.")
    except Exception as ex:
        print(f"Error installing package {pkg}")
        print(f"{ex}")
        return False
    return True


def download_results(repo_link):
    try:
        print("Downloading measurement results with git clone ", end="")
        subprocess.check_call(["git", "clone", repo_link])
        print("done.")
    except Exception as ex:
        print("Error downloading measurement results")
        print(f"{ex}")
        return False
    return True


if __name__ == '__main__':
    success = True

    with open("requirements.txt") as f:
        for package in f:
            success = success and pip_install(package)

    success = success and download_results(RESULTS_REPOSITORY)

    if not success:
        print("Something went wrong")
        sys.exit(1)
    sys.exit(0)
