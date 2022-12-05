from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from threading import Thread
from tkcalendar import Calendar
from datetime import datetime

from scrapper import ScrapeTweets


window = Tk()
window.title('Tweets Scraper')
window.config(pady=20,padx=20)
window.resizable(False,False) # to disable the minimize/maximize buttons. 


#Username.
website_label = Label(text='Username:')
website_label.grid(column=0,row=1)

username_entry = Entry(width=35)
username_entry.focus() # to make the typer starts in the website entry when we start the program.
username_entry.insert(0,'@')
username_entry.grid(column=1,row=1)

#Email.
email_label = Label(text='Email:')
email_label.grid(column=0,row=2)

email_entry = Entry(width=35)
                        
email_entry.grid(column=1,row=2)


#Password.
Password_label = Label(text='Password:')
Password_label.grid(column=0,row=3)

Password_entry = Entry(show="*" , width=21)
Password_entry.grid(column=1,row=3)


#hashtags.
keywords_label = Label(text='Keyword(s):')
keywords_label.grid(column=0,row=4)
keywords_entry = Entry(width=50)
keywords_entry.grid(column=1,row=4)

#Web driver path.
chrome_webdriver_path = None

def get_webdriver_path():
    global chrome_webdriver_path
    chrome_webdriver_path_fd = filedialog.askopenfilename(title='Select Chrome WebDriver')
    chrome_webdriver_path = chrome_webdriver_path_fd


chrome_webdriver_path_label = Label(text='Chrome Web Driver Path:')
chrome_webdriver_path_label.grid(column=0,row=5)
chrome_webdriver_path_button = Button(text='Browse' ,command=get_webdriver_path)
chrome_webdriver_path_button.grid(column=1,row=5)


from_date = None
to_date = None

def start_scraping():
    global chrome_webdriver_path

    global from_date
    global to_date

    username = username_entry.get()
    email = email_entry.get()
    password = Password_entry.get()
    keywords = keywords_entry.get()

    if username == '' or email == '' or password == '' or keywords == '' or chrome_webdriver_path == None:
        messagebox.showerror('Missing failed(s)' , 'Be Sure to Fill Out all the Faileds and choese chrome WebDriver.')
    else:    
        if use_date_filter_varible.get() == True:
            if from_date == None:
                from_date = datetime(year=2006 , month= 1 , day= 1).date()
            if to_date == None:
                to_date = datetime.today().date()
                
            if to_date < from_date or to_date == from_date:
                messagebox.showerror('Dates Error' , 'The Start Date must be before the End Date ,also they can not be equivalent.')
        else:
            from_date = None
            to_date = None


        while True:
            scraper = ScrapeTweets(
                username = username,
                email = email,
                password = password,
                keywords = keywords, 
                chrome_webdriver_path = chrome_webdriver_path,
                from_date = from_date,
                to_date = to_date)
            try:
                scraper.login()         
                break
            except Exception  as e:
                messagebox.showerror(title='Login Failed click Ok to try again or check your internet connection',message=f'{e}')
                scraper.driver.quit()

        
        scraper.search()
        


def set_from_date():
    def print_sel():
        global from_date
        from_date = cal.selection_get()
        from_date_label.config(text = f'Sat To {cal.selection_get()}')
        top.destroy()
        top.update()

    top = Toplevel(window)

    cal = Calendar(top,
                   font="Arial 14", selectmode='day',
                   cursor="hand1", year=2018, month=2, day=5)
    cal.grid(row= 0 ,column = 0)
    Button(top, text="Set", command=print_sel).grid(row=1 , column=1)

def set_to_date():
    def print_sel():
        global to_date
        to_date = cal.selection_get()
        to_date_label.config(text = f'Sat To {cal.selection_get()}')
        top.destroy()
        top.update()

    top = Toplevel(window)

    cal = Calendar(top,
                   font="Arial 14", selectmode='day',
                   cursor="hand1", year=2018, month=2, day=5)
    cal.grid(row= 0 ,column = 0)
    Button(top, text="Set", command=print_sel).grid(row=1 , column=1)


def start_scraping_thread():
    Thread(target = start_scraping).start()


use_date_filter_varible = IntVar(value=True)
use_date_filter_checkbox = Checkbutton(window, text='Use dates filter',variable=use_date_filter_varible, onvalue=True, offvalue=False)
use_date_filter_checkbox.grid(column=0,row=7)

from_date_label = Label(text='From Date (Optional)')
from_date_label.grid(column=0,row=8)
Button(window, text='Set', command=set_from_date).grid(column=2, row=8)

to_date_label = Label(text='To Date (Optional)')
to_date_label.grid(column=0,row=9)
Button(window, text='Set', command=set_to_date).grid(column=2, row=9)


start_button = Button(text = 'Start' , command=start_scraping_thread)
start_button.grid(column=1,row=10)


window.mainloop()

