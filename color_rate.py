from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from pywinauto.timings import Timings
from PIL import Image
import time
import re
import os
import time
import json
import sys

CONNECT_APP_TIMEOUT = 1
PROCESS_APP_TIMEOUT = 1
START_APP_TIMEOUT   = 10
WAIT_GUI_TIMEOUT    = 60

def get_mainw(app, timeout):
    mainw = app.window(best_match = 'GTX Graphics Lab')
    mainw.wait('visible', timeout)
    mainw.wrapper_object()
    return mainw

def connect_glab():
    try:
        app = Application(backend='uia').connect(title_re = 'GTX Graphics Lab.*', timeout = 10) 
        return get_mainw(app, CONNECT_APP_TIMEOUT)
    except:
        return None

def start_glab(glab_path):
    try:
        app = Application(backend='uia').start(glab_path)
        return get_mainw(app, START_APP_TIMEOUT)
    except:
        return None

    
def size_to_region(size):
    return {
        'kids' : ['7x8', '7', '8'],
        'XS'   : ['10x12', '10', '12'],
        'S'    : ['14x16', '14', '16'],
        'M'    : ['14x16', '14', '16'],
        'L'    : ['16x18', '16', '18'],
        'XL'   : ['16x18', '16', '18'],
        'XXL'  : ['16x21', '16', '21'],
        'XXXL' : ['16x21', '16', '21']
    }[size]

def set_edit_text(edit, text):
    edit.type_keys('0')
    edit.type_keys('{BACKSPACE 10}' + text +'{ENTER}')
    
def get_float(string):
    return float(re.findall(r"[-+]?\d*\.\d+|\d+", string)[0])

def get_color_rate(mainw, image_path, size, color):
    #close old
    mainw.fileFileButton.click()
    mainw.NewButton.click()
    if mainw.child_window(best_match = "Don't Save").exists():
        mainw.child_window(best_match = "Don't Save").click()
    # set size region
    mainw.Button2.click()
    mainw.child_window(best_match = size_to_region(size)[0] + 'Static').click_input()
    # add image btn click
    mainw.addAdd_Image.click()
    # add image dlg
    imagew = mainw.child_window(best_match = 'Открытие')
    imagew.wait('visible', timeout = WAIT_GUI_TIMEOUT)
    imagew.wrapper_object()
    # set image path
    imagew.child_window(best_match = 'Имя файла:Edit').set_text(image_path)
    # load image
    send_keys('{ENTER}')
    imagew.wait_not('visible', timeout = WAIT_GUI_TIMEOUT)
    time.sleep(PROCESS_APP_TIMEOUT)
    #set size
    w, h = Image.open(image_path).size
    if w > h:
        set_edit_text(mainw.child_window(best_match = 'W:Edit'), size_to_region(size)[1])
    else:
        set_edit_text(mainw.child_window(best_match = 'H:Edit'), size_to_region(size)[2])
    # center
    mainw.centerButton.click()
    # print
    mainw.Print.click()
    time.sleep(PROCESS_APP_TIMEOUT)
    mainw.child_window(best_match = 'Print Settings').wait('visible', timeout = WAIT_GUI_TIMEOUT)
    
    # select ink
    #if color == 'black':
    #    index = '2'
    #elif color == 'white':
    #    index = '0'
    #else:
    #    index = '2'
    #mainw.ComboBox3.type_keys('{UP 10}{DOWN ' + index + '}')
    if color == 'black':
        index = '1'
    elif color == 'white':
        index = '3'
    else:
        index = '2'
    mainw.ComboBox2.type_keys('{UP 10}{DOWN ' + index + '}')
    
    mainw.Print2.click()
    preview = Application(backend='uia').connect(title_re = '.*Brother GTX pro File Output Preview window.*', timeout = WAIT_GUI_TIMEOUT)    
    previeww = preview.window(best_match = 'Brother GTX pro File Output Preview window')
    previeww.wrapper_object()
    if color == 'white':
        rate = [get_float(previeww.Static16.window_text()), 0]
    else:
        rate = [get_float(previeww.Static22.window_text()), get_float(previeww.Static24.window_text())]
    previeww.child_window(best_match = 'Закрыть').click()
    return rate

test_colors = ['black', 'white', 'color']
test_sizes = ['kids', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']

class ImageDesc:
    def __init__(self, image, size, color, rate):
        self.image = image
        self.size  = size
        self.color = color
        self.rate  = rate
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=None, separators=(',', ': '))

def image_rate(glab_path, image_path, size, color):
    if size not in test_sizes:
        return "[size error]"
    if color not in test_colors:
        return "[color error]"

    Timings.slow()
    mainw = connect_glab()
    if not mainw:
        mainw = start_glab(glab_path)
    if not mainw:
        return '[run error]'
        
    start_time = time.time()
    rate = get_color_rate(mainw, image_path, size, color)
    end_time = time.time()
    image = ImageDesc(image_path, size, color, rate)
    print(image.to_json() + ": " + str(end_time - start_time) + " sec")
    return image.to_json()

def folder_rate(glab_path, image_folder):
    Timings.slow()
    imgs = []
    valid_images = ['.jpg', '.gif', '.png', '.tga']
    for f in os.listdir(image_folder):
        ext = os.path.splitext(f)[1]
        if ext.lower() not in valid_images:
            continue
        imgs.append(f)
    
    mainw = connect_glab()
    if not mainw:
        mainw = start_glab(glab_path)
    if not mainw:
        return '[run error]'
    
    json_report =               '{\n'
    json_report = json_report + '    "images":\n'
    json_report = json_report + '    [\n'
    total_rate = [0, 0]
    for img in imgs:
        for size in test_sizes:
            for color in test_colors:
                start_time = time.time()
                rate = get_color_rate(mainw, image_folder + img, size, color)
                end_time = time.time()
                image = ImageDesc(image_folder + img, size, color, rate)
                json_report = json_report + '        ' + image.to_json() + ',\n'
                
                print(image.to_json() + ": " + str(end_time - start_time) + " sec")
                    
                total_rate[0] = total_rate[0] + rate[0]
                total_rate[1] = total_rate[1] + rate[1]
    json_report = json_report[:-1]
    json_report = json_report + '    ],\n'
    json_report = json_report + '    "total_rate": ' + str(total_rate) + '\n'
    json_report = json_report + '}'
    return json_report

if __name__ == "__main__":
    if len(sys.argv) == 5:
        print(image_rate(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
    elif len(sys.argv) == 3:
        print(folder_rate(sys.argv[1], sys.argv[2]))
    
    #print(image_rate(r'C:\GTX Graphics Lab\nw.exe', r'Z:\test картинки\1.png', 'XL', 'black'))
    #print(folder_rate(r'C:\\GTX Graphics Lab\\nw.exe', 'Z:\\test картинки\\'))


