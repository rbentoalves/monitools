import PySimpleGUI as sg
import os
import sys
import windows as windows
import pandas as pd
import re
import inputs as inputs

# This is a sample Python script.
# TODO add a select all button for sites
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def main():
    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.
    font1 = ('Helvetica', 10, "bold")
    font2 = ('Helvetica', 1)

    layout = [[sg.Text('Please choose your geography', pad=((10, 10), (5, 5)), font=font1)],
              [sg.Button("USA", pad=((10, 10), (4, 4)), font=font2, image_filename=resource_path("USA.png"), image_subsample=6),
               sg.Push(),
               sg.Button("ES", pad=((10, 10), (4, 4)), font=font2, image_filename=resource_path("ES.png"), image_subsample=6),
               sg.Push()],
              [sg.Button("AUS", pad=((10, 10), (4, 4)), font=font2, image_filename=resource_path("AUS.png"), image_subsample=6),
               sg.Push(),
               sg.Button("UK", pad=((10, 10), (4, 4)), font=font2, image_filename=resource_path("UK.png"), image_subsample=6),
               sg.Push()],
              [sg.Push(), sg.Exit(pad=(1, 10), size=(10, 1))]]

    # Create the Window
    window = sg.Window('LSbp GP&M tool-kit', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read(timeout=100)

        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks exit+
            break
        if event == "USA" or event == "UK" or event == "ES" or event == "AUS":
            # geofolder_path = os.path.join(os.path.join(os.environ['USERPROFILE'])) + \
            #                "/OneDrive - Lightsource BP/Desktop/Daily Monitoring Report/" + event


            print(os.getcwd())
            desktop_path = (os.path.join(
                os.path.join(os.environ['USERPROFILE']), 'Desktop').
                            replace('\\', "/").
                            replace("/Desktop", "/OneDrive - LIGHTSOURCE HOLDINGS 2 LIMITED/Desktop"))

            print("Desktop folder: ", desktop_path)
            geofolder_path = desktop_path + "/Daily Monitoring Report/" + event

            general_info_path = geofolder_path + "/Info&Templates/General Info " + event + ".xlsx"
            pre_selection_path = geofolder_path + "/Info&Templates/site_selection.txt"

            print("General Info path: ", general_info_path)
            print("Pre-selection path: ", pre_selection_path)

            try:
                site_list = pd.read_excel(general_info_path, sheet_name='Site Info', engine='openpyxl')["Site"].to_list()
            except FileNotFoundError:
                general_info_path = inputs.input_file(desktop_path)
                geofolder_path = re.search(r'C.*Report/' + event, general_info_path).group().replace('\\',
                                                                                                     "/")

                pre_selection_path = geofolder_path + "/Info&Templates/site_selection.txt"

                print("\nFailure in fecthing general info, new paths are:", general_info_path)
                print("General Info path: ", general_info_path)
                print("Pre-selection path: ", pre_selection_path)

                site_list = pd.read_excel(general_info_path, sheet_name='Site Info', engine='openpyxl')["Site"].to_list()
            print("Full site list read successfully")


            try:
                pre_selection = pd.read_csv(pre_selection_path, header=None)[0].to_list()
            except pd.errors.EmptyDataError:
                pre_selection = site_list

            #print(pre_selection)

            windows.process_selection(geofolder_path, event, site_list, pre_selection, pre_selection_path)

            #sg.popup(general_info_path)

    window.close()

    return


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
