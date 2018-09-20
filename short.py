# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 10:03:23 2018

@author: Justin
"""

import cv2
import tkinter as tk
import threading
import queue

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
        
        cap = cv2.VideoCapture(input_file)
        fourcc = cv2.VideoWriter_fourcc(*'MP4V') #mp4 compression
        
        #Set output video parameters
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        framerate = cap.get(5)
        cap.set(0,start*1000) #Start at specified time
        
        out = cv2.VideoWriter(output_file,fourcc,framerate,(frame_width,frame_height))
        
        #Reads each frame and writes desired frames to output
        while(cap.isOpened()):
            ret, frame = cap.read()
            time = cap.get(0)/1000
            if ret == True and time <= stop and not exit_flag:
                out.write(frame)
            else:
                break
        #Clean up
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        if exit_flag:
            break
        
    outq.put(None)

class myApp:
    def __init__(self,root):

        #Make GUI
        self.root = root
        root.title("MP4 Batch Break")
        root.geometry('400x100')
        root.grid_columnconfigure(0,weight = 0)
        root.grid_columnconfigure(1,weight = 1)
        root.grid_columnconfigure(2,weight = 1)
        root.grid_rowconfigure(0,weight = 1)
        root.grid_rowconfigure(1,weight = 0)
        self.txt_file_entry = tk.Entry(root)
        self.txt_file_entry.grid(row = 0,column = 1,columnspan = 2,sticky = 'ew')
        tk.Label(root,text = 'Input Text File Path: ').grid(row = 0, column = 0,sticky = 'w')
        tk.Button(self.root, text='Begin', command= self.beginProgram).grid(row = 1,column = 1,sticky = 'new')
        
        self.progress = tk.Label(root,text = 'File: Not Started')

        self.progress.grid(row = 1, column = 2)
        
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
    app = myApp(root)
    
    #Run code
    root.mainloop()
    #Quit Process
    exit_flag = True
