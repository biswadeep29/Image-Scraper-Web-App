import streamlit as st
import random
import os
import io
import time
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

st.title("Image downloader")

st.subheader("Want to download images from google images for your Deep Learning projects!? You are at the right place.")
st.markdown("**Here enter the name of the topic and it will web scrape the entire google images page for those pictures.**")

form_ = {
    'name':None,
    'max_images' : None,
    'path' : None
}

with st.form(key="enter"):
    form_['name'] = st.text_input("Enter name : ",placeholder="Type a name...")
    form_['max_images'] = st.number_input("Enter maximum number of images to download", value=None, placeholder="Type a number...")
    form_['path'] = st.text_input(
        "Enter path : ",
        placeholder=r"Type the absolute file path (e.g., E:\\USERS\\Downloads\\Images\\ {name of the folder} \\)"
    )


    submit_button = st.form_submit_button()
    if submit_button:
        if not all(form_.values()):
            st.warning("Properly Fill Up The Values!")
        else:
            st.write("Program Is Running!")

            path = r"D:\\python_lib\\chromedriver.exe"
            service = Service(path)
            options = Options()
            # options.add_argument("--headless=new") --> Browser window is not shown.
            options.headless = False                   # Browser window is shown.
            driver = webdriver.Chrome(service=service,options=options)

            driver.get("https://www.google.com/imghp")

            WebDriverWait(driver,5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,"gLFyf"))
            )

            input_ele = driver.find_element(By.CLASS_NAME,"gLFyf")
            input_ele.clear()
            input_ele.send_keys(form_["name"] + Keys.ENTER)

            def get_img_from_google(wd, delay, max_images):
                def scroll_down(wd):
                    wd.execute_script("window.scrollTo(0,document.body.scrollHeight);")
                    time.sleep(delay)

                image_urls = set()
                skips = 0

                while len(image_urls) < max_images:
                    scroll_down(wd)
                    thumbnails = wd.find_elements(By.CLASS_NAME, "YQ4gaf")
                    thumbnails = [img for img in thumbnails if "zr758c" not in img.get_attribute("class") and "wA1Bge" not in img.get_attribute("class")]

                    for img in thumbnails:
                        if len(image_urls) >= max_images:
                            break  # Stop once we have enough images

                        try:
                            img.click()
                            time.sleep(delay)
                        except:
                            continue

                        images = wd.find_elements(By.CLASS_NAME, "iPVvYb")
                        for image in images:
                            src = image.get_attribute("src")

                            if not src or "http" not in src or src in image_urls:
                                skips += 1  # Track skipped images
                                continue  # Skip duplicates

                            image_urls.add(src)
                            print(f"Image Found! - {len(image_urls)}")
                            st.write(f"Image Found! - {len(image_urls)}")

                return image_urls

            def download_img(download_path,url,file_name):
                try:
                    if not os.path.exists(download_path):
                        os.makedirs(download_path)

                    image_content = requests.get(url).content
                    image_file = io.BytesIO(image_content)
                    image = Image.open(image_file)
                    file_path = download_path + file_name

                    with open(file_path,"wb") as f:
                        image.save(f,"JPEG")

                    print(f"Downloaded: {file_path}")
                    st.write(f"Downloaded: {file_path}")
                except Exception as e:
                    print("Failed - ",e)
                    st.write("Failed - ",e)

            urls = get_img_from_google(driver,2,form_['max_images'])
            name = form_['name']
            base_path = form_['path']

            for i,url in enumerate(urls):
                i = (i+3)*random.randint(1000,2000)
                download_img(base_path,url,str(i)+".jpg")

            st.write("Done!")
            driver.close()
