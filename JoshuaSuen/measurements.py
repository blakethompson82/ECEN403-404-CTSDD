# Used for signal data collection
from pylab import psd
from rtlsdr import RtlSdr

# Used for both GPS and signal data collection
from pathlib2 import Path

# Used for file location
import os


# File path function
def filePath():
    while True:
        storage = raw_input("Where do you want to export the data?"
                            "\n[1] Onboard storage \n[2] External drive \n")

        # Onboard storage
        if storage == "1":
            file_path = "/home/pi"
        # External drive
        elif storage == "2":
            drive_name = raw_input("Please enter the name of the external drive: ")
            file_path = "/media/pi/" + drive_name
            # Check for specified external drive
            while not os.path.exists(file_path) or not drive_name.strip():     
                drive_name = raw_input("%s is not an external drive. Export data "
                                       "to onboard storage? [Y/N] " % file_path)
                if drive_name == "Y" or drive_name == "y":
                    file_path = "/home/pi"
                    break
                elif drive_name == "N" or drive_name == "n":
                    drive_name = raw_input("Please enter the name of the external drive: ")
                    file_path = "/media/pi/" + drive_name
                else:
                    print("Please enter [Y] or [N].")
        else:
            print("Please enter [1] or [2].\n")
            continue
    
        # Confirm save location
        confirm = raw_input("Data will be exported to: %s [Y/N] " % file_path)
    
        if confirm == "Y" or confirm == "y":
            break
        elif confirm == "N" or confirm == "n":
            continue
        else:
            print("Error: Inavlid input")

    # Confirmation
    print("Exporting data to: %s" % file_path)
    
    return file_path
            
# Signal data collection function
def saveSignal(iteration, freq, file_path):
    # Define function for writing signal data into file
    def write_data(iteration, data_points, magnitudeData, frequencyData, mag_file, freq_file):
        i = 0
        mag_file.write('[%d, ' % iteration)
        freq_file.write('[%d, ' % iteration)
        while i < data_points-1:
            mag_file.write("%s, " % magnitudeData[i])
            freq_file.write("%s, " % frequencyData[i])
            i += 1
        mag_file.write('%s]\n' % magnitudeData[i])
        freq_file.write('%s]\n' % frequencyData[i])

    sdr = RtlSdr()

    # Configure SDR
    sdr.sample_rate = 2.4e6        # Hz
    sdr.center_freq = freq         # Hz
    sdr.freq_correction = 60       # PPM
    sdr.gain = 4                   # 'auto'

    # Initialize
    data_points = 1024
    samples = sdr.read_samples(256*data_points)
    mag_file_path = file_path + "/magData.txt"
    freq_file_path = file_path + "/freqData.txt"

    ### *** IMPORTANT *** (for later, when optimizing)
    ### I'm not sure if we should leave this outside of the function
    ### and move it to the end of the main code, after the flight path
    ### ends. Idk the impact of leaving the SDR open/on for an extended
    ### period of time. If we move sdr.close() outside, we have to
    ### remember to also move the above code outside as well.
    ### Leaving this line within this function should be fine for now.
    sdr.close()

    # PSD plot data
    psddata = psd(samples, NFFT=data_points, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)

    # Extracting pertinent information from the PSD plot calculation
    magnitudeData = psddata[0]
    frequencyData = psddata[1]

    # Check for .txt file and write data
    # For Ron: Magnitude has not been converted to dB yet. To convert, 10*log(magnitude).
    if Path(mag_file_path).is_file() and Path(freq_file_path).is_file():
        with open(mag_file_path, 'a') as mag_file, open(freq_file_path, 'a') as freq_file:
            write_data(iteration, data_points, magnitudeData, frequencyData, mag_file, freq_file)
    else:
        with open(mag_file_path, 'w') as mag_file, open(freq_file_path, 'w') as freq_file:
            write_data(iteration, data_points, magnitudeData, frequencyData, mag_file, freq_file)
    
    print("Data saved successfully.")



# CHANGELOG

# Feb 9, 2018
# Cleared up a few comments/notes to self and cleaned up code in [measurements.py]

# Feb 10, 2018
# Verified exchangeable formatting for sdr.center_freq (95.1e6 vs 95100000 vs 95100000.0)
# Added ability to allow user to choose save location [in Flight_Control_v2.py]
# Made code more robust by preventing user from inputting invalid arugments [in Flight_Control_v2.py]

# Feb 11, 2018
# Renamed functions from collectBlah to saveBlah for clarity
# Added ability to configure center frequency of SDR
# Modified saveSignal to save data dynamically based off of user input
# Added data save confirmation for verification
# Modified saveGPS to save data dynamically based off of user input

# Feb 23, 2018
# Created function to determine file path to clean up main script
# Made file path function more robust by adding ability to catch empty inputs
# Commented out saveGPS function in preparation for removal

# April 2, 2018
# Appended point # to front of lists for troubleshooting and tracking separate runs
# Removed GPS function and saved in a backup file
