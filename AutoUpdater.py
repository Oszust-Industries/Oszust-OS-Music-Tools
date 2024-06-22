## Oszust OS AutoUpdater - v4.1.0 (5.15.24) - Oszust Industries
import os, pathlib, requests, shutil, subprocess, threading, urllib.request, webbrowser, zipfile
import PySimpleGUI as sg

def setupUpdate(systemName, systemBuild, softwareVersion, newestVersion):
    if systemBuild.lower() in ["dev", "main"]: return ## STOPS THE UPDATER
    ## Setup Thread and Return to Main App
    global loadingStatus, loadingStep
    loadingPopup, loadingStatus, loadingStep = sg.Window("", [[sg.Text("Installing " + systemName, font='Any 16', background_color='#1b2838', key='updaterTitleText')], [sg.Text(newestVersion, font='Any 16', background_color='#1b2838', key='updaterVersionText')], [sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", background_color='#1b2838', key='updaterGIFImage')], [sg.Text("Starting Updater...", font='Any 16', background_color='#1b2838', key='updaterText')], [sg.Text("Step 0 of 7", font='Any 14', background_color='#1b2838', key='updaterStepText')], [sg.Button("Ok", font='Any 16', visible=False, key='doneButton')]], background_color='#1b2838', element_justification='c', no_titlebar=True, keep_on_top=True), "Starting Updater...", 0
    while True:
        event, values = loadingPopup.read(timeout=10)
        loadingPopup["updaterGIFImage"].UpdateAnimation(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=30) ## Load Loading GIF
        loadingPopup["updaterText"].update(loadingStatus)
        loadingPopup["updaterStepText"].update("Step " + str(loadingStep) + " of 7")
        if event == sg.WIN_CLOSED: exit()
        elif loadingStatus == "Starting Updater...":
                loadingStatus, loadingStep = "Checking Internet...", 1    
                OszustOSAutoUpdaterThread = threading.Thread(name="OszustOSAutoUpdater", target=OszustOSAutoUpdater, args=(systemName, systemBuild, softwareVersion, newestVersion,))
                OszustOSAutoUpdaterThread.start()
        elif "Error-" in loadingStatus:
            loadingPopup.close()
            crashMessage(str(loadingStatus[len("Error-"):]), systemName)
            break
        elif loadingStatus == "Done":
            loadingPopup["updaterGIFImage"].update(visible=False)
            loadingPopup['doneButton'].update(visible=True)
            loadingStatus = "Finished"
        elif event == 'doneButton':
            createBatFile(systemName)
            loadingPopup.close()
            break

def crashMessage(message, systemName):
    RightClickMenu = ['', ['Copy']] ## Right Click Menu - Crash Message
    errorWindow = sg.Window("AutoUpdater Error", [[sg.Text(systemName + " AutoUpdater has crashed.", font=("Any", 13))], [sg.Multiline(message, size=(50,5), font=("Any", 13), disabled=True, autoscroll=False, right_click_menu=RightClickMenu, key='crashMessageErrorCodeText')], [sg.Button("Report Error", button_color=("White", "Blue"), key='Report'), sg.Button("Quit", button_color=("White", "Red"), key='Quit')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
    errorLine:sg.Multiline = errorWindow['crashMessageErrorCodeText']
    ## Window Shortcuts
    errorWindow.bind('<Insert>', '_Insert')  ## Report Error shortcut
    errorWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
    ## Mouse Icon Changes
    for key in ['Report', 'Quit']: errorWindow[key].Widget.config(cursor="hand2") ## Hover icons
    while True:
        event, values = errorWindow.read(timeout=10)
        if event == sg.WIN_CLOSED or event == 'Quit' or (event == '_Delete'): return
        elif event == 'Report' or (event == '_Insert'): webbrowser.open("https://github.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/issues/new", new=2, autoraise=True)
        elif event in RightClickMenu[1]: ## Right Click Menu Actions
            try:
                if event == 'Copy': ## Copy Error Text
                    try:
                        errorWindow.TKroot.clipboard_clear()
                        errorWindow.TKroot.clipboard_append(errorLine.Widget.selection_get())
                    except: pass
            except: pass

def OszustOSAutoUpdater(systemName, systemBuild, softwareVersion, newestVersion):
    global current, loadingStatus, loadingStep
    try: urllib.request.urlopen("http://google.com", timeout=3) ## Test Internet
    except:
        loadingStatus = "Error-No Internet."
        return
    try: ## Start Main Update System
        current, loadingStatus, loadingStep, tempDownloadFolder = str(os.path.dirname(pathlib.Path(__file__).resolve().parent)), "Checking Newest Version...", 2, os.path.join(os.getenv('APPDATA'), "Oszust Industries")
        try: newestVersion = ((requests.get("https://api.github.com/repos/Oszust-Industries/" + systemName.replace(" ", "-") + "/releases/latest")).json())['tag_name'] ## Get Newest Release Tag
        except:
            loadingStatus = "Error-Bad API call was made to GitHub's releases." ## Bad API Call
            return
        if newestVersion != softwareVersion:
        ## Create Temp Folder for Update in Appdata
            loadingStatus, loadingStep = "Creating Temp Folder...", 3    
            if os.path.exists(tempDownloadFolder) == False: os.mkdir(tempDownloadFolder)
            if os.path.exists(os.path.join(tempDownloadFolder, "temp")) == False: os.mkdir(os.path.join(tempDownloadFolder, "temp"))
            else:
                shutil.rmtree(os.path.join(tempDownloadFolder, "temp"))
                os.mkdir(os.path.join(tempDownloadFolder, "temp"))
        ## Download Update
            loadingStatus, loadingStep = "Downloading Update...", 4
            urllib.request.urlretrieve("https://github.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/archive/refs/heads/" + systemBuild + ".zip", (tempDownloadFolder + "\\temp\\" + systemName.replace(" ", "_") + ".zip"))
            with zipfile.ZipFile(tempDownloadFolder + "\\temp\\" + systemName.replace(" ", "_") + ".zip", 'r') as zip_ref: zip_ref.extractall(tempDownloadFolder + "\\temp")
            os.remove(tempDownloadFolder + "\\temp\\" + systemName.replace(" ", "_") + ".zip")
        ## Update Required Files
            loadingStatus, loadingStep = "Installing Update...", 5 
            try:
                os.remove(os.path.join(current, "_internal", "AutoUpdater.py"))
                os.remove(os.path.join(current, "_internal", systemName.replace(" ", "_") + ".py"))
                shutil.rmtree(os.path.join(current, "_internal", "data"))
            except:
                loadingStatus = "Error-Unable to delete current files. You will have to remove them yourself."
                return
            os.rename(tempDownloadFolder + "\\temp\\" + systemName.replace(" ", "-") + "-" + systemBuild + "\\" + systemName.replace(" ", "_") + "\\" + systemName.replace(" ", "_") + ".exe", tempDownloadFolder + "\\temp\\" + systemName.replace(" ", "-") + "-" + systemBuild + "\\" + systemName.replace(" ", "_") + "\\" + systemName.replace(" ", "_") + "2.exe")
            try: copyFilesFolders((tempDownloadFolder + "\\temp\\" + systemName.replace(" ", "-") + "-" + systemBuild + "\\" + systemName.replace(" ", "_")), current)
            except:
                loadingStatus = "Error-Unable to copy update files. You will have to copy them yourself."
                return
        ## Clean Update
            loadingStatus, loadingStep = "Cleaning Update...", 6
            shutil.rmtree(os.path.join(tempDownloadFolder, "temp"))
        loadingStatus, loadingStep = "Done", 7 ## Update done or not needed
    except Exception as Argument:
        loadingStatus = "Error-" + str(Argument)
        return

def copyFilesFolders(source_dir, dest_dir):
    for item in os.listdir(source_dir):
        print(item)
        source_item = os.path.join(source_dir, item)
        dest_item = os.path.join(dest_dir, item)
        if os.path.isfile(source_item):
            try: shutil.copy2(source_item, dest_item)
            except: pass
        elif os.path.isdir(source_item):
            if os.path.isdir(dest_item): copyFilesFolders(source_item, dest_item)
            else:
                try: shutil.copytree(source_item, dest_item)
                except: pass

def createBatFile(systemName):
    try: os.remove(current + '\\commands.bat') ## Remove Old .bat File
    except: pass
    commands = [
        'timeout 1',
        'taskkill /f /im ' + systemName.replace(" ", "_") + '.exe"',
        'timeout 1',
        'del "' + current +'\\' + systemName.replace(" ", "_") + '.exe"',
        'cd "' + current + '"',
        'ren "' + systemName.replace(" ", "_") + '2.exe" "' + systemName.replace(" ", "_") + '.exe"'
    ]
    with open('commands.bat', 'w') as f:
        f.write('@echo off\n')
        for command in commands:
            f.write(command + '\n')
    subprocess.Popen(['cmd', '/k', current + '\\commands.bat'], shell=True)


## Start System
def main(systemName, systemBuild, softwareVersion, newestVersion):
    try: setupUpdate(systemName, systemBuild, softwareVersion, newestVersion)
    except Exception as Argument: print("AutoUpdater Error: " + str(Argument))