from Device import Device
from data.Constants import APP_NAME

devices_to_run: list[Device] = list()

# run app
if __name__ == '__main__':
    try:
        print(f'"{APP_NAME}" utility starting')
        __init_app_entities()
        __init_app()
        __start_app()
    except Exception as e:
        print(f'All functionality failed with exception - {e}, app exiting')
        __clean_app_entities()
    print(f'"{APP_NAME}" utility ending work, bye')
    exit(1)
