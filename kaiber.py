import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from google_utils import create_album_with_authed_session, add_photo_to_album, find_last_file, upload_photo
from datetime import datetime

# Zoom In Up Down Left Right Rotate Counter-Clockwise
download_folder = '/Users/fvyshkov/Downloads'
subject_texts = ['Rainbow piano']
filenames = ['/Users/fvyshkov/Downloads/rain.jpg']
camera_movements_list = [
    #[],
    #['Rotate Clockwise'],
    #['Zoom In'],
    ['Zoom Out'],
]
styles = ['realistic', 'Kandinsky', 'Matisse', 'Van Gogh', 'Marc Chagall']

img_table = []
for subject_text in subject_texts:
    for filename in filenames:
        for camera_movement in camera_movements_list:
            for style in styles:
                img_table.append({
                    'time_in_sec': 5,
                    'default_duration': 8,
                    'sbj_text': subject_text,
                    'style_text': style,
                    'filename': filename,
                    'camera_movements': camera_movement,
                })


def create_image(row):
    sbj_text = row['sbj_text']
    style_text = row['style_text']
    time_in_sec = row['time_in_sec']
    default_duration = row['default_duration']
    camera_movements = row['camera_movements']
    filename = row['filename']

    def wait_for_element_by_xpath(xpath):
        return WebDriverWait(driver, 1000).until(EC.element_to_be_clickable((By.XPATH, xpath)))

    JS_DROP_FILE = """
        var target = arguments[0],
            offsetX = arguments[1],
            offsetY = arguments[2],
            document = target.ownerDocument || document,
            window = document.defaultView || window;
    
        var input = document.createElement('INPUT');
        input.type = 'file';
        input.onchange = function () {
          var rect = target.getBoundingClientRect(),
              x = rect.left + (offsetX || (rect.width >> 1)),
              y = rect.top + (offsetY || (rect.height >> 1)),
              dataTransfer = { files: this.files };
    
          ['dragenter', 'dragover', 'drop'].forEach(function (name) {
            var evt = document.createEvent('MouseEvent');
            evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
            evt.dataTransfer = dataTransfer;
            target.dispatchEvent(evt);
          });
    
          setTimeout(function () { document.body.removeChild(input); }, 25);
        };
        document.body.appendChild(input);
        return input;
    """

    def drag_and_drop_file(drop_target, path):
        driver = drop_target.parent
        file_input = driver.execute_script(JS_DROP_FILE, drop_target, 0, 0)
        file_input.send_keys(path)

    driver = webdriver.Chrome()
    driver.get("https://kaiber.ai/login")
    # login
    email_field = driver.find_element(By.ID, 'email')
    email_field.send_keys('fvyshkov@gmail.com')
    email_field.send_keys(Keys.ENTER)
    pwd_field = driver.find_element(By.ID, 'password')
    pwd_field.send_keys('i.Rdz73m667PD5k')
    pwd_field.send_keys(Keys.ENTER)
    # close message, we do not need it
    element = wait_for_element_by_xpath("//button[contains(@class, 'text-gray-400 rounded-full outline-none hover:text-gray-500')]")
    element.click()
    driver.get("https://kaiber.ai/create")
    # choose type of generation (there are 3 of them)
    type_element = wait_for_element_by_xpath("//img[@src = 'https://website-public-assets.kybercorp.org/web/flipbook/animation_2.webp']")
    #actions = ActionChains(driver)
    #actions.move_to_element(element).double_click().perform()
    time.sleep(1)
    type_element.click()
    # file uploading
    input_element = wait_for_element_by_xpath("//span[contains(text(),'upload file')]")
    path_to_image = filename
    drag_and_drop_file(input_element, path_to_image)
    edit_prompt_element = wait_for_element_by_xpath("//span[contains(text(),'Edit your prompt')]")
    edit_prompt_element.click()
    sbj_element = wait_for_element_by_xpath("//textarea[contains(text(),'(describe subject)')]")
    style_element = wait_for_element_by_xpath("//textarea[contains(text(),'(describe details)')]")
    time.sleep(1)
    sbj_element.click()
    sbj_element.send_keys(Keys.COMMAND + "a")  # Command on macOS
    for i in range(20):
        sbj_element.send_keys(Keys.BACK_SPACE)
    sbj_element.send_keys(sbj_text)

    style_element.click()
    style_element.send_keys(Keys.COMMAND + "a")  # Command on macOS
    for i in range(20):
        style_element.send_keys(Keys.BACK_SPACE)
    style_element.send_keys(style_text)

    wait_for_element_by_xpath("//button[contains(text(),'Video settings')]").click()
    print('setup video settings')

    decrease_time_btn = wait_for_element_by_xpath("//button[contains(@class,'w-12 h-8 text-lg font-semibold text-center bg-primary text-dark rounded-full focus:outline-none')]")
    # duration
    if default_duration > time_in_sec:
        for _ in range(8 - time_in_sec):
            time.sleep(0.5)
            decrease_time_btn.click()
    # camera_movements
    for camera_move in camera_movements:
        wait_for_element_by_xpath(f"//span[text()='{camera_move}']").click()
    slider = wait_for_element_by_xpath("//span[@class='bg-primary text-dark w-12 py-1 px-2 text-lg text-center font-semibold']")
    driver.execute_script("arguments[0].textContent = arguments[1];", slider, '0')
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    print('boomerang')
    time.sleep(1)
    checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
    checkboxes[1].click()
    gen_b = driver.find_elements(By.XPATH, "//*[contains(text(), 'Generate Previews')]")
    gen_b[1].click()
    print('waiting for previews')
    wait_for_element_by_xpath("//img[contains(@alt,'preview-')]").click()
    print('create!')
    wait_for_element_by_xpath("//span[@class='text-lg' and contains(text(), 'Create Video')]").click()

    download_path = "//span[@class='lg:inline text-[12px] sm:text-[14px]' and contains(text(), 'Download')]"
    download_b = wait_for_element_by_xpath(download_path)
    print('download!')
    download_b.click()
    time.sleep(3)
    wait_for_element_by_xpath(download_path)
    time.sleep(3)
    driver.quit()


album_id = create_album_with_authed_session(f'{datetime.now().strftime("%d%m%y")} AI AUTO')
t = time.time()
for image in img_table:
    create_image(image)
    print(f'iter = {time.time()-t}')
    result_filepath = Path(find_last_file(download_folder))
    upload_token = upload_photo(result_filepath)
    if upload_token:
        add_photo_to_album(upload_token, album_id)





