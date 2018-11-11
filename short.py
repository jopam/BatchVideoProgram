# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 10:03:23 2018

@author: Justin
"""

from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import threading
import queue
import ffmpy3


exit_flag = False

def shortHelper(txt_file,outq):
    '''
    Function activated with a button to begin breaking mp4 files according
    to specified conditions in txt file
    Txt File Format:
        input_file,start,stop,output_file
        input_file,start,stop,output_file
        ...
    '''

    inputs = []
    #Reads txt file
    with open(txt_file,encoding='utf-8-sig') as file:
        data = file.readlines()
        for line in data:
            inputs.append(line.split(','))
    #Iterates through batch process
    for i,case in enumerate(inputs):
        input_file = case[0]
        start = float(case[1]) #Start time in s
        stop = float(case[2]) #Stop time in s
        output_file = case[3].strip('\n')
        
        #communicate with updateProgress
        outq.put((i+1,len(inputs)))
        
        
        ff = ffmpy3.FFmpeg(
                inputs = {input_file:None},
                outputs = {output_file:'-ss {} -to {} -c:v copy -c:a copy'.format(start,stop)}
                )
        ff.run()
        if exit_flag:
            break
        
    outq.put(None)

class myApp:
    def __init__(self,root):

        #Make GUI
        self.root = root
        self.create_widgets()
        
    def create_widgets(self):
        self.root.title("MP4 Batch Slice")
        self.root.geometry('600x150')
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        main = ttk.Notebook(self.root)
        main.grid(sticky='news')
        page1 = ttk.Frame(main)
        page1.grid_columnconfigure(1,weight=1)
        
        self.txt_file_entry = ttk.Entry(page1)
        self.txt_file_entry.grid(row = 0,column = 1,sticky = 'ew')
        ttk.Label(page1,text = 'Input Text File Path: ').grid(row = 0, column = 0)
        ttk.Button(page1, text='Begin', command= self.beginProgram).grid(row = 1,column = 1)
        ttk.Button(page1, text='Find', command= lambda: self.find_file(self.txt_file_entry)).grid(row = 0,column = 2)
        self.progress = ttk.Label(page1,text = 'File: Not Started')
        self.progress.grid(row = 1, column = 2)
        
        
        page2 = ttk.Frame(main)
        page2.grid_columnconfigure(1,weight=1)
        page2.grid_columnconfigure(4,weight=1)
        
        self.source_entry = ttk.Entry(page2)
        self.source_entry.grid(row = 0,column = 1,sticky='ew')
        ttk.Label(page2,text = 'Source File: ').grid(row = 0, column = 0)
        ttk.Button(page2, text='Find', command= lambda: self.find_file(self.source_entry)).grid(row = 0,column = 2)
        self.dest_entry = ttk.Entry(page2)
        self.dest_entry.grid(row = 1,column = 1,sticky='ew')
        ttk.Label(page2,text = 'Destination Folder: ').grid(row = 1, column = 0)
        ttk.Button(page2, text='Find', command= lambda: self.find_dir(self.dest_entry)).grid(row = 1,column = 2)
        self.dest_file_entry = ttk.Entry(page2)
        self.dest_file_entry.grid(row = 1,column = 4,sticky='ew')
        ttk.Label(page2,text = 'Destination File Name: ').grid(row = 1, column = 3)
        self.start_entry = ttk.Entry(page2)
        self.start_entry.grid(row = 2,column = 1)
        ttk.Label(page2,text = 'Start Time(s): ').grid(row = 2, column = 0)
        self.stop_entry = ttk.Entry(page2)
        self.stop_entry.grid(row = 2,column = 3)
        ttk.Label(page2,text = 'Stop Time(s): ').grid(row = 2, column = 2)
        self.txt_entry = ttk.Entry(page2)
        self.txt_entry.grid(row = 3,column = 1,sticky='ew')
        ttk.Label(page2,text = 'Txt File: ').grid(row = 3, column = 0)
        ttk.Button(page2, text='Find', command= lambda: self.find_file(self.txt_entry)).grid(row = 3,column = 2)
        
        ttk.Button(page2, text='Add to Txt File', command= lambda: self.append_txt()).grid(row = 3,column = 3)
        
        main.add(page1, text='Slicing Tab')
        main.add(page2, text='Text File Adder')
    def find_file(self,entry):
        entry.delete(0,tk.END)
        entry.insert(0,filedialog.askopenfilename())
    def find_dir(self,entry):
        entry.delete(0,tk.END)
        entry.insert(0,filedialog.askdirectory())
    def append_txt(self):
        try:
            field = ','.join([self.source_entry.get(),self.start_entry.get(),
                              self.stop_entry.get(),self.dest_entry.get()+'/'+self.dest_file_entry.get()])
        
            with open(self.txt_entry.get(),'a') as file:
                file.write('\n' + field)
        except:
            messagebox.showerror(title = 'ERROR',message='Oops, something went wrong')
            
    def beginProgram(self):
        
        outq = queue.Queue()
        #Start multithreaded process
        prog = threading.Thread(target=shortHelper, args=(self.txt_file_entry.get(), outq))
        prog.daemon = True
        prog.start()
        
        #Start Updating GUI periodically
        self.root.after(250,self.updateProgress, outq)
    def updateProgress(self,outq):
        #Recursive program that updates GUI
        try:
            file_num = outq.get_nowait()
            if file_num:
                self.progress['text'] = 'File: {}/{}'.format(*file_num)
                self.root.after(250,self.updateProgress, outq)
            else:
                self.progress['text'] = 'File: Completed. Start Again?'
                pass
        except queue.Empty:
            self.root.after(250,self.updateProgress, outq)
    
if __name__=='__main__':
    #Interface
    root = tk.Tk()
    s = ttk.Style()
    s.theme_use('clam')
    app = myApp(root)
    #Run code
    root.mainloop()
    #Quit Process
    exit_flag = True
