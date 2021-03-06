import argparse
import json
import numpy as np

from Receive import Receiver
from Plot import Plot
from Ephem import Coordinates


# Reads user parameters
def parser():
    parser = argparse.ArgumentParser(
        prog = 'H-line-observer',
        description = 'An interface to receive H-line data'
    )

    # Parsing options (receiver)
    parser.add_argument('-f', metavar = 'Frequency', type = int, help = 'Center tuning frequency in Hz', default = 1420400000, dest = 'frequency')
    parser.add_argument('-s', metavar = 'Sample rate', type = int, help = 'Tuner sample rate', default = 2400000, dest = 'sample_rate')
    parser.add_argument('-o', metavar = 'PPM offset', type = int, help = 'Set custom tuner offset PPM', default = 0, dest = 'ppm')
    parser.add_argument('-r', metavar = 'Resolution', type = int, help = 'Amount of samples = 2 raised to the power of the input', default = 10, dest = 'resolution')
    parser.add_argument('-n', metavar = 'Number of FFT\'s', type = int, help = 'Number of FFT\'s to be collected and averaged', default = 1000, dest = 'num_FFT')

    # Parsing options (observer)
    parser.add_argument('-l', metavar = 'Latitude', type = float, help = 'The latitude of the antenna\'s position as a float, north is positive', default = 0.0, dest = 'latitude')
    parser.add_argument('-g', metavar = 'Longitude', type = float, help = 'The latitude of the antenna\'s position as a float, east is positive', default = 0.0, dest = 'longitude')
    parser.add_argument('-z', metavar = 'Azimuth', type = float, help = 'The azimuth of the poting direction', default = 0.0, dest = 'azimuth')
    parser.add_argument('-a', metavar = 'Altitude', type = float, help = 'The elevation of the pointing direction', default = 0.0, dest = 'altitude')
    parser.add_argument('-c', help = 'Use lat, lon of QTH and antenna alt/az from config file', action = 'store_true', dest = 'use_config')
    parser.set_defaults(use_config = False)
    
    args = parser.parse_args()

    main(args)


# Main method
def main(args):

    # Get current observer location and antenna pointing direction
    if args.use_config:
        config = read_config()
        lat, lon = config['latitude'], config['longitude']
        alt, az = config['altitude'], config['azimuth']
        if "none" in (lat, lon, alt, az):
            print('Please check your config file or use command line arguments.')
            quit()
    else:
        lat, lon = args.latitude, args.longitude
        alt, az = args.altitude, args.azimuth
    

    # Get current equatorial and galactic coordinates of antenna RA and Declination
    Coordinates_class = Coordinates(lat = lat, lon = lon, alt = alt, az = az)
    ra, dec = Coordinates_class.equatorial()
    gal_lat, gal_lon = Coordinates_class.galactic()

    # Receives and writes data
    Receiver_class = Receiver(frequency = args.frequency, sample_rate = args.sample_rate, ppm = args.ppm, resolution = args.resolution, num_FFT = args.num_FFT)
    freqs, data, SNR = Receiver_class.receive()

    # Plots data
    print('Plotting data...')
    name = f'ra={ra},dec={dec},SNR={SNR}'
    Plot_class = Plot()
    Plot_class.plot(freqs = freqs, data = data, name = name)


# Reads the config file and returns JSON graph
def read_config():
    path = './config.txt'
    config = open(path, 'r')
    json_config = json.load(config)
    return json_config


if __name__ == "__main__":
    parser()
