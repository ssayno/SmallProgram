import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


br = webdriver.Chrome()
wait = WebDriverWait(br, 10)
br.get('https://www.bilibili.com/')
login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                      '#i_cecream > div.bili-feed4 > div.bili-header.large-header > '
                                                      'div.bili-header__bar > ul.right-entry > li:nth-child(1) > li > '
                                                      'div.right-entry__outside.go-login-btn > div > span')))
login_button.click()
account_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div.bili-mini-mask > div > '
                                                                            'div.bili-mini-login-right-wp > '
                                                                            'div.login-pwd-wp > form > div:nth-child('
                                                                            '1) > input[type=text]')))
password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div.bili-mini-mask > div > '
                                                                             'div.bili-mini-login-right-wp > '
                                                                             'div.login-pwd-wp > form > '
                                                                             'div:nth-child(3) > input['
                                                                             'type=password]')))
account_input.send_keys('17347468806')
password_input.send_keys("271xufei.")

# submit_login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'body > div.bili-mini-mask > div > '
#                                                                               'div.bili-mini-login-right-wp > '
#                                                                               'div.login-pwd-wp > div.btn_wp > '
#                                                                               'div.btn_primary.disabled')))
# submit_login_button.click()
time.sleep(1000)
