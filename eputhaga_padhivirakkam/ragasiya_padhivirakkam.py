import logging
import os
import re
import subprocess
from os.path import basename
from os.path import expanduser
from time import sleep, time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
error_prefix = 'Error: '


def download_book(asin, downloads=expanduser("~") + os.sep + 'Downloads'):
    """
    download book from cps
    :param asin:
    :param downloads:
    :return:
    """

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('download.default_directory=' + downloads)
    driver = webdriver.Chrome('/usr/local/bin/chromedriver')  # Optional argument, if not specified will search path.
    try:
        driver.get('https://cps-dashboard.amazon.com/downloadSource.jsp')
        sleep(10)
        elem = driver.find_element_by_xpath('/html/body/div[2]/form/input[1]')
        log.info('typing the ASIN {}'.format(asin))
        elem.send_keys(asin)
        sleep(5)
        try:
            if driver.find_element_by_xpath('/html/body/div[2]/label') or 'Could not find asin' in\
                    driver.find_element_by_xpath('/html/body/div[2]/label').text:
                log.critical('Could not find ASIN ' + asin)
                return error_prefix + 'Could not find ASIN ' + asin
        except Exception as e:
            log.info('ASIN is present in the repo!!!')

        driver.find_element_by_xpath('/html/body/div[2]/form/input[3]').click()
        sleep(10)
        els = driver.find_elements_by_id('fileSelect')
        if len(els) == 0:
            log.critical('Could not process download')
            return error_prefix + 'Could not process download'

        txt = els[len(els) - 1].get_attribute('value')
        # delete if existing files in the same name present
        txt = str(txt).replace(':', '_')
        p1 = subprocess.Popen(['ls ' + downloads + os.sep + '*' + txt[:10] + '*'], shell=True, stdout=subprocess.PIPE)

        # Run the command
        output = p1.communicate()[0]
        log.info(' listing filepath: {}'.format(output))
        for fil in output.split('\n'):
            if os.path.exists(fil):
                log.info('Removing file {}'.format(fil))
                os.remove(fil)

        log.info('/html/body/div[2]/form[' + str(len(els)) + ']/button')
        # //*[@id="fileSelect"]
        driver.find_element_by_xpath('/html/body/div[2]/form[' + str(len(els)) + ']/button').click()
        sleep(8)

        # waits for all the files to be completed and returns the paths
        try:
            paths = WebDriverWait(driver, 1500, 10).until(every_downloads_chrome)
        except TimeoutException as te:
            log.critical('TimeOut while waiting for download')
            return error_prefix + 'TimeOut while waiting for download'

        print(paths)
        txt = str(txt).replace(':', '_')
        p1 = subprocess.Popen(['ls ' + downloads + os.sep + '*' + txt[:10] + '*'], shell=True, stdout=subprocess.PIPE)

        # Run the command
        output = p1.communicate()[0]
        output = output.strip()
        log.info(' listing filepath: {}'.format(output))
        driver.quit()
        return output

        # sleep(5)
        # start_time = time()
        # timeout = 1000
        # txt = str(txt).replace(':', '_')
        # p1 = subprocess.Popen(['ls ' + downloads + os.sep + txt[:10] + '*'], shell=True, stdout=subprocess.PIPE)
        #
        # # Run the command
        # output = p1.communicate()[0]
        # log.info(' listing filepath: {}'.format(output))
        # while time() - start_time < timeout and 'crdownload' in output:
        #     sleep(10)
        #     # Run the command
        #     p1 = subprocess.Popen(['ls ' + downloads + os.sep + txt[:10] + '*'], shell=True, stdout=subprocess.PIPE)
        #     output = p1.communicate()[0]
        #     log.info(' Downloading filepath: {}'.format(output))
        #
        # # Run the command
        # p1 = subprocess.Popen(['ls ' + downloads + os.sep + txt[:10] + '*'], shell=True, stdout=subprocess.PIPE)
        # output = p1.communicate()[0]
        # if 'crdownload' in output:
        #     log.critical('Book is still downloading!! Increase timeout')
        #     return error_prefix + 'Book is still downloading!! Increase timeout'
        #
        # driver.quit()
        # file_name = basename(output)
        # if '.epub' in file_name:
        #     extn = '.epub'
        # elif '.mobi' in file_name:
        #     extn = '.mobi'
        # elif '.prc' in file_name:
        #     extn = '.prc'
        # elif '.kpf' in file_name:
        #     extn = '.kpf'
        # elif '.pdf' in file_name:
        #     extn = '.pdf'
        # else:
        #     extn = '.mobi'
        # file_path = output.strip()
        # rename_path = os.path.abspath(os.path.join(file_path, os.pardir)) + os.sep + asin + extn
        # log.info('Renaming file {} to {}'.format(file_path, rename_path))
        # os.rename(file_path, rename_path)
        # if not os.path.exists(rename_path):
        #     log.critical('File does not exist--{}---'.format(rename_path))
        #     return error_prefix + 'File does not exist--{}---'.format(rename_path)
        # return rename_path
    finally:
        if driver:
            log.info('Quitting driver------')
            #driver.quit()


def every_downloads_chrome(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    return driver.execute_script("""
        var items = downloads.Manager.get().items_;
        if (items.every(e => e.state === "COMPLETE"))
            return items.map(e => e.file_url);
        """)


def get_book_from_local(asin, file_path):
    """
    :param asin
    :param file_path
    :return:
    """

    sleep(5)
    start_time = time()
    timeout = 10000
    file_path = file_path.strip()
    file_name = basename(file_path)
    file_name = file_name[:10]
    while time() - start_time < timeout and 'crdownload' in file_path:
        sleep(10)
        # Run the command
        p1 = subprocess.Popen(['ls ' + os.path.abspath(os.path.join(file_path, os.pardir))
                               + os.sep + '*' + file_name + '*'], shell=True, stdout=subprocess.PIPE)
        file_path = p1.communicate()[0]
        file_path = file_path.strip()
        log.info(' Downloading filepath: {}'.format(file_path))

    # Run the command
    p1 = subprocess.Popen(['ls ' + os.path.abspath(os.path.join(file_path, os.pardir)) + os.sep + '*'
                           + file_name + '*'], shell=True, stdout=subprocess.PIPE)
    file_path = p1.communicate()[0]
    file_path = file_path.strip()

    if 'crdownload' in file_path:
        log.critical('Book is still downloading!! Increase timeout')
        return error_prefix + 'Book is still downloading!! Increase timeout'

    file_name = basename(file_path)
    if '.epub' in file_name:
        extn = '.epub'
    elif '.mobi' in file_name:
        extn = '.mobi'
    elif '.prc' in file_name:
        extn = '.prc'
    elif '.kpf' in file_name:
        extn = '.kpf'
    elif '.pdf' in file_name:
        extn = '.pdf'
    else:
        extn = '.mobi'
    rename_path = os.path.abspath(os.path.join(file_path, os.pardir)) + os.sep + asin + extn
    log.info('Renaming file {} to {}'.format(file_path, rename_path))
    os.rename(file_path, rename_path)
    if not os.path.exists(rename_path):
        log.critical('File does not exist--{}---'.format(rename_path))
        return error_prefix + 'File does not exist--{}---'.format(rename_path)
    return rename_path


def send_book_path():
    return '/Users/srinis/Downloads/A3C9QOQ7RTHJ9X_ATVPDKIKX0DER_9781351967891.prc-2016-10-14-14_59_15'


def test():
    output = '/Users/srinis/Downloads/A3C9QOQ7RTHJ9X_ATVPDKIKX0DER_9781351967891.prc-2016-10-14-14_59_15'
    extn = '.prc'
    asin = 'B01M4J9KLP'
    log.info('---{}--'.format(os.path.abspath(os.path.join(output, os.pardir))))
    log.info('Renaming file {} to {}'.format(output, os.path.abspath(os.path.join(output, os.pardir)) + os.sep + asin + extn))
    s = '/Users/srinis/Downloads/A3C9QOQ7RTHJ9X_ATVPDKIKX0DER_9781351967891.prc-2016-10-14-14_59_15\n'
    print '::::{}:::::'.format(s.rstrip())
    # os.rename(output, os.path.abspath(os.path.join(output, os.pardir)) + os.sep + asin + extn)
    pattern = re.compile('^B[a-zA-Z0-9]+$')
    gr = pattern.match(asin)
    print gr.group(0)


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(prog='Ebook Downloader')
    # parser.add_argument('--asin', help='10 digit asin', dest='asin')
    # parser.print_help()
    # res = parser.parse_args()
    # print res.asin
    test()
    #download_book(res.asin)
