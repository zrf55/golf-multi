#!/usr/bin/env python
# coding: utf-8

# In[2]:


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import smtplib
import ssl
from email.message import EmailMessage



class GolfMulti:
    #ctor
    def __init__(self, date, facility, num_players, time_of_day, num_holes, email): 
        #entered in strings separated by commas wo spaces
        """self.date = date.split(",") if "," in date else [date] #array of strings
        self.facility = facility.split(",") if "," in facility else [facility] #array of strings
        self.num_players = num_players.split(",") if "," in num_players else [num_players] #array of strings
        self.time_of_day = time_of_day.split(",") if "," in time_of_day else [time_of_day] #string OR array - FIXME
        self.num_holes = num_holes.split(",") if "," in num_holes else [num_holes] #array of strings"""
        
        #now all passed as arrays
        self.date = date
        self.facility = facility
        self.num_players = num_players
        self.time_of_day = time_of_day
        self.num_holes = num_holes
        self.email = email
                
        self.driver = webdriver.Chrome() 
        self.driver.get("https://foreupsoftware.com/index.php/booking/21265/7483#/teetimes")
        self.driver.minimize_window()
        public_tee_times = self.driver.find_element(By.XPATH, "//button[text()='Public Tee Times']").click()
        time.sleep(5)

        self.original = [] #empty array of dicts
        for d in self.date:
            for f in self.facility:
                for p in self.num_players:
                    for t in self.time_of_day:
                        for h in self.num_holes:
                            self.select_options(d, f, p, t, h)
                            time.sleep(5)
                            self.original += self.get_available()
        
        #for o in self.original: print(o)        
        print(f"Original created of length {len(self.original)} at {self.get_now()}")

        result = []

        while(len(result) == 0):
            time.sleep(60*10)
            self.refresh()
            print("refresh success")
            result = self.check_diff(self.original)
            print(f"No difference found at {self.get_now()}")

        print(result)
        self.driver.quit()

        for res in result:
            print(res)
            self.send_email(res)
            print(f"Email successfully Sent at {self.get_now()}")

            
            
    def select_options(self,d,f,p,t,h): #all variables passed are strings 
        #print(d,f,p,t,h)
        facility = Select(self.driver.find_element(By.ID, "schedule_select")).select_by_visible_text(f)

        date = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "date-field")))
        for i in range(10): date.send_keys(Keys.BACK_SPACE)
        date.send_keys(d)


        players = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "players")))
        players = players.find_element(By.PARTIAL_LINK_TEXT, p)
        players.click() #misc click to reset after date selected
        players2 = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "players")))
        players2.click()

        if t == "All":
            time = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "All"))).click()
        else:
            time = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, t))).click()

        holes = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "holes")))
        holes.find_element(By.LINK_TEXT, h).click()


    def get_available(self):
        tiles_array = []

        time_tiles = self.driver.find_elements(By.CLASS_NAME, "time-tile")
        for tile in time_tiles:
            tile_dict = {
                "time" : tile.find_element(By.CLASS_NAME, "booking-start-time-label").text,
                "location": tile.find_element(By.CLASS_NAME, "js-booking-side-name").text,
                "num_players" : tile.find_element(By.CLASS_NAME, "booking-slot-players").text,
                "num_holes" : tile.find_element(By.CLASS_NAME, "booking-slot-holes").text,
                "price" : tile.find_element(By.CLASS_NAME, "booking-slot-pricing-information").text, #remove $
                "start" : tile.find_element(By.CLASS_NAME, "js-booking-side-name").text
            }    
            tiles_array.append(tile_dict)

        if len(tiles_array) == 0: print("No available times found for these parameters")
        else:
            print(f"Appended {len(tiles_array)} elements")#for tile in tiles_array: print(tile)

        return tiles_array


    #refresh by clicking any of the selection buttons
    def refresh(self):
        self.driver.refresh()
        public_tee_times = self.driver.find_element(By.XPATH, "//button[text()='Public Tee Times']").click()
        time.sleep(5)


    def check_diff(self, original):
        later = []
        
        for d in self.date:
            for f in self.facility:
                for p in self.num_players:
                    for t in self.time_of_day:
                        for h in self.num_holes:
                            self.select_options(d, f, p, t, h)
                            time.sleep(5)
                            later += self.get_available()
        print(len(later))
        if (later == original): #NOT length bc can be removed and added
            #print("No change")
            return []

        else:        
            diff = []

            for tile in later:
                if tile not in original:
                    diff.append(tile)

            return diff


    def send_email(self, result):
        email_sender = 'soccerpro4234@gmail.com'
        email_password = 'qddevprvjlcusqnb'
        
        email_receiver = self.email#['brian_fleisch@yahoo.com','soccerpro4234@gmail.com']

        subject = f'Tee Time Opening at {result["time"]} on {self.date}'
        body = f'''
        A new tee time is available at {result["time"]} on {self.date} at {self.facility}
        This opening is for {result["num_players"]} players for {result["num_holes"]} holes and costs {result["price"]}
        Sign up now at https://foreupsoftware.com/index.php/booking/21265/7483#/teetimes
        '''

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())


    def get_now(self): return datetime.now().strftime("%I:%M:%S %p, %x")
    
        
    #toString method (print(p1))
    def __str__(self):
        return f"{self.time_of_day} tee time on {self.date} at {self.facility} for {self.num_players} players for {self.num_holes} holes"

#g1 = GolfMulti("08-05-2023, 08-06-2023", "Osprey Point", "4", "Morning", "18")

