import os
def run():
    os.system("uvicorn --app-dir=. app.main:app --reload")


if __name__ == '__main__':

    run()