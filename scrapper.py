from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import re
from datetime import datetime , timedelta
from time import sleep
from random import randint
from bs4 import BeautifulSoup


class ScrapeTweets:
    def __init__(self, username, email , password ,  hashtags , chrome_webdriver_path , from_date, to_date):
        self.username = username
        self.email = email
        self.password = password
        
        self.hashtags = hashtags.replace('\n','') # Clear self.search_query from any unexpacted chars
        
        delta:timedelta = to_date - from_date

        self.search_range = []

        for i in range(delta.days + 1):
            self.search_range.append(from_date + timedelta(days=i))

        self.search_range.reverse() # to start searching from newest to oldest date
        
        self.tweets_buffer = []


        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument("--disable-notifications")


        csv_file = pd.DataFrame({
                    'username': [],
                    'handle': [],
                    'date': [],
                    'text': [],
                    'reply_count': [],
                    'retweet_count': [],
                    'like_count': [],
                    })
        
        try:
            self.data_file_name = self.hashtags
            csv_file.to_csv(f'{self.data_file_name}.csv' , index=False)
        except OSError: # Sometimes hashtags names may contain symbols that aren't allowed as a file name.
            self.data_file_name = randint(10000,1000000)
            csv_file.to_csv(f'{self.data_file_name}.csv' , index=False)       

        
        self.driver = webdriver.Chrome(chrome_webdriver_path , options=options)
        self.driver.implicitly_wait(30)

        self.driver.get('https://twitter.com/login')

    def __repr__(self):
        return f'{self.__class__.__name__}(Data Entries={len(self.df)})'

    def login(self):
        print('Logging in')
        
        # Username
        login_email_input = self.driver.find_element(By.XPATH,"//input[@name='text']")
        login_email_input.send_keys(self.email)
        next_button = self.driver.find_element(By.XPATH,"//span[contains(text(),'Next')]")
        next_button.click()

        sleep(2)
        # If verfcation needed
        visable_spans = self.driver.find_elements(By.TAG_NAME , 'span')
        visable_texts = []
        for text in visable_spans:
            visable_texts.append(text.text)

        if 'There was unusual login activity on your account. To help keep your account safe, please enter your phone number or username to verify it’s you.' in visable_texts:
            username_verfcation_input = self.driver.find_element(By.TAG_NAME , 'input')
            username_verfcation_input.send_keys(self.username)
            username_verfcation_input.send_keys(Keys.RETURN)
        
        # Password
        login_password_input = self.driver.find_element(By.XPATH,"//input[@name='password']")
        login_password_input.send_keys(self.password)
        log_in = self.driver.find_element(By.XPATH,"//span[contains(text(),'Log in')]")
        log_in.click()
    
        print(f'[*] Logged In As {self.username}\n')

    def search(self):
        for date in self.search_range:
            query_from_date = date - timedelta(days=1)
            query_to_date = date

            if query_from_date.month < 10:
                from_month = f'0{query_from_date.month}'
            else:
                from_month = f'{query_from_date.month}'
            
            if query_from_date.day < 10:
                from_day = f'0{query_from_date.day}'
            else:
                from_day = f'{query_from_date.day}'


            if query_to_date.month < 10:
                to_month = f'0{query_to_date.month}'
            else:
                to_month = f'{query_to_date.month}'
            
            if query_to_date.day < 10:
                to_day = f'0{query_to_date.day}'
            else:
                to_day = f'{query_to_date.day}'
            
            self.search_query = f'{self.hashtags} until:{query_to_date.year}-{to_month}-{to_day} since:{query_from_date.year}-{from_month}-{from_day}'

            search_input = self.driver.find_element(By.XPATH , '//input[@aria-label="Search query"]')
            search_input.send_keys(Keys.CONTROL + 'a')
            search_input.send_keys(Keys.DELETE)

            search_input.send_keys(self.search_query)
            search_input.send_keys(Keys.RETURN) # Press Enter

            sleep(3)
            self.scroll()


    def scroll(self):
        # get all tweets on the page
        last_position = self.driver.execute_script("return window.pageYOffset;")
        scrolling = True

        while scrolling:
            tweet_cards = BeautifulSoup(self.driver.execute_script('return document.documentElement.outerHTML'), 'html.parser').select('[data-testid="tweet"]')
             
            for tweet_card in tweet_cards[-10:]: # In the normal situation twitter won't load more than ten tweets except in a large or vertical monitors or zoomed out browser (I am note sure), 10 was perfect for me ,feel free to play around with the number to be sure that it reaches every twwet in the timeline
                self.get_tweet_data(tweet_card)

            scroll_attempt = 0
            while True:
                self.driver.execute_script('window.scrollBy(0, 800);')
                curr_position = self.driver.execute_script("return window.pageYOffset;")
                if last_position == curr_position:
                    scroll_attempt += 1
                    # end of scroll region
                    if scroll_attempt >= 3: 
                        scrolling = False
                        self.save_tweet_to_csv()
                        break
                    else:
                        sleep(2) # attempt another scroll
                else:
                    last_position = curr_position
                    break

    def get_tweet_data(self , tweet_card): 
            """Extract data from tweet card"""
            user_data = tweet_card.find_all('span', attrs={"class" : "css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0"})
            username = user_data[0].text

            try:
                handle = user_data[1].text
            except NoSuchElementException: # If it's a sponsored tweet
                handle = None 

            try:
                postdate_and_time = tweet_card.find('time').attrs['datetime']
            except NoSuchElementException:
                postdate_and_time = None
            
            tweet_text = tweet_card.select('[data-testid="tweetText"]')[0].find_all('span')
            text = ''

            for word in tweet_text:
                text += word.text

            reply_count = tweet_card.select('[data-testid="reply"]')[0].text
            retweet_count = tweet_card.select('[data-testid="retweet"]')[0].text
            like_count = tweet_card.select('[data-testid="like"]')[0].text
            
            tweet = [username, handle, postdate_and_time ,text , reply_count, retweet_count, like_count]

                        
            if tweet not in self.tweets_buffer: # to exclude repeated tweets
                self.tweets_buffer.append(tweet) 

    def save_tweet_to_csv(self):
        for tweet in self.tweets_buffer:
            df = pd.DataFrame({
                    'username': [tweet[0]],
                    'handle': [tweet[1]],
                    # Convert date and time from string to datetime object i.e '2022-11-28T23:59:09.000Z'
                    'date': datetime.strptime(tweet[2] , '%Y-%m-%dT%H:%M:%S.%fZ'),
                    'text': [tweet[3]],
                    'reply_count': [tweet[4]],
                    'retweet_count': [tweet[5]],
                    'like_count': [tweet[6]]
                })
            df.to_csv(f'{self.data_file_name}.csv', mode='a',index=False ,header=False)
        self.tweets_buffer.clear()
