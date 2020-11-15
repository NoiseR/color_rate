from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from pywinauto.timings import Timings
from PIL import Image
import time
import re
import os

CONNECT_APP_TIMEOUT = 1
PROCESS_APP_TIMEOUT = 1
START_APP_TIMEOUT   = 10
WAIT_GUI_TIMEOUT    = 40

def get_mainw(app, timeout):
    mainw = app.window(best_match = 'GTX Graphics Lab')
    mainw.wait('visible', timeout)
    mainw.wrapper_object()
    return mainw

def connect_glab():
    try:
        app = Application(backend='uia').connect(title_re = '.*GTX Graphics Lab.*', timeout = 10)    
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
    if color == 'black':
        index = '2'
    elif color == 'white':
        index = '0'
    else:
        index = '2'
    mainw.ComboBox3.type_keys('{UP 10}{DOWN ' + index + '}')
    
    # use background
    #if color == 'black':
    #    mainw.Static7.click_input()
    #mainw.print_control_identifiers()
    #return 'test'
    
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

def test_rate(glab_path, image_folder):
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
        mainw = start_glab(r'C:\\GTX Graphics Lab\\nw.exe')
    if not mainw:
        return '[run error]'
    
    total_rate = [0, 0]
    for img in imgs:
        for size in test_sizes:
            for color in test_colors:
                rate = get_color_rate(mainw, image_folder + img, size, color)
                print(img + ' : ' + size + ' : ' + color + ' : ' + str(rate))
                total_rate = total_rate + rate
    return total_rate

if __name__ == "__main__":

    print(test_rate(r'C:\\GTX Graphics Lab\\nw.exe', 'Z:\\test картинки\\'))


