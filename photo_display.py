#!/usr/bin/python
""" Implements a photo viewer using cv2. """

import os
import cv2
import sys

# Only import what we need
from time import sleep
from random import shuffle
from optparse import OptionParser
from re import compile as re_compile
from multiprocessing import Pipe, cpu_count

def get_screen_resolution():
    """ Returns the resolution of the screen as reported by xrandr."""
    from subprocess import Popen, PIPE

    output = Popen(r'xrandr | grep "\*" | cut -d" " -f4', shell=True,
                   stdout=PIPE, stderr=PIPE).communicate()[0]
    resolution = output.split()[0].split(b'x')
    return (int(resolution[0]), int(resolution[1]))

def natural_sort_key(sort_element, _nsre=re_compile('([0-9]+)')):
    """ A function to do a natural sort. (Mixed alphanumeric and numerical)."""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, sort_element)]

def scale_image(img_to_scale, desired_size):
    """Scale an image until one (or both if the image is the correct
    aspect ratio) dimension is the desired size."""

    # Get tye current image size
    xpos, ypos = img_to_scale.shape[1::-1]

    # If the image is exactly the correct size already, just return
    if xpos == desired_size[0] and ypos == desired_size[1]:
        return img_to_scale

    # Get the scale factors
    x_scale_factor = float(desired_size[0])/xpos
    y_scale_factor = float(desired_size[1])/ypos

    # Figure out which scale factor to use
    if x_scale_factor > y_scale_factor:
        new_x_dimension = int(round(xpos * y_scale_factor))
        new_y_dimension = int(round(ypos * y_scale_factor))
        border_x, border_y = (desired_size[0] - new_x_dimension)/2, 0
    # Either work if they are the same, this works if wider
    else:
        new_x_dimension = int(xpos * x_scale_factor)
        new_y_dimension = int(ypos * x_scale_factor)
        border_x, border_y = 0, (desired_size[1] - new_y_dimension)/2

    if options.verbose:
        print "Dimensions: Orig:(%dx%d) Mod:(%dx%d) Border: (%dx%d) Desired: (%dx%d)" % (
            xpos, ypos, new_x_dimension, new_y_dimension, border_x, border_y, desired_size[0], desired_size[1])

    # Resize if necessary
    if xpos != new_x_dimension and ypos != new_y_dimension:
        img_to_scale = cv2.resize(img_to_scale, (new_x_dimension, new_y_dimension))
    # Add border if necessary
    if border_x > 0 or border_y > 0:
        img_to_scale = cv2.copyMakeBorder(img_to_scale, border_y, border_y, border_x, border_x, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    return img_to_scale

def load_image(photo):
    """ Load an image from disk and scale/border it."""
    loaded_img = cv2.imread(photo)
    if loaded_img is None:
        return photo, None
    else:
        return photo, scale_image(loaded_img, desired_size=options.dimensions)

def show_image(image_to_show, wait_time):
    """ Show an image on the screen for the set amount of time."""

    cv2.imshow('image', image_to_show)
    return cv2.waitKey(wait_time*1000)

def wait_for_photo(photo):
    """ Wait for a specific photo to finish. Add other finished photos to
    dictionary while at it."""

    # If we had already processed it don't do anything
    if photo in read_hash:
        return

    # Make sure we are waiting on a valid photo
    if photo is not None and photo not in in_processesing:
        raise ValueError("Waiting on a photo that isn't processing. This is a bug.")

    # We could have another photo finish before the one we are waiting for
    while len(busy_processes) > 0:
        sleep(.001)
        for position, proc in enumerate(busy_processes):
            if proc[0].poll():
                # Handle if the process died (only for shutdown)
                try:
                    data = proc[0].recv()
                except:
                    busy_processes.pop(position)
                    break
                read_hash[data[0]] = data[1]
                if data[0] in in_processesing:
                    del in_processesing[data[0]]
                ready_processes.append(busy_processes.pop(position))
                if photo == None or data[0] == photo:
                    return
                break

def process_photo(photo):
    """ Start processing a photo if we haven't already."""

    # Make sure the photo isn't already in process
    if photo in read_hash or photo in in_processesing:
        return

    if options.verbose:
        print "Going to add photo to process: %s" % photo

    # Wait until a process is ready
    if len(ready_processes) == 0:
        print "No threads available... waiting."
        wait_for_photo(None)

    # Get a free process and send it the photo to process
    proc = ready_processes.pop()
    proc[0].send(photo)
    busy_processes.append(proc)
    in_processesing[photo] = True

def manage_photos():
    """ Make sure we have options.cache_size photos forward and backwards."""

    # Make sure the next options.cache_size and previous
    #  options.cache_size photos are always loaded
    min_load = 0 if pos - options.cache_size < 0 else pos - options.cache_size
    max_load = pos + options.cache_size if pos + options.cache_size < len(to_show) else len(to_show)

    # Process all the photos in the range
    for position in xrange(min_load, max_load):
        process_photo(to_show[position])

    # Figure out which photos to delete from the cache
    need_delete = [x for x in to_show if x not in [to_show[y] for y in range(min_load, max_load)]]

    # Delete the photos we no longer need
    for delete in need_delete:
        if delete in read_hash:
            if options.verbose:
                print "Removing photo from cache: %s" % delete
            del read_hash[delete]

def clean_up():
    """ Prepare to quit. (Wait for the children to finish and kill all
    windows)."""

    # Reap the children
    while len(busy_processes) > 0:
        wait_for_photo(None)

    # Tell the children to die
    for each_thread in xrange(0, num_threads):
        # Tell the child to shut down
        try:
            ready_processes[each_thread][0].send("die")
            os.wait()
        except (IOError, IndexError):
            pass

    cv2.destroyAllWindows()

# Find out default size to scale to
screen_res = get_screen_resolution()

# Set up the option parser
parser = OptionParser(usage="usage: %prog", version="%prog 1", description="Show photos on the photo display.")
parser.add_option("--time", action="store", dest="time", default=10, type="int", help="The time to show each photo. (In seconds)")
parser.add_option("--order", action="store_true", dest="order", default=False, help="Show the photos in order.")
parser.add_option("--dimensions", action="store", dest="dimensions", type="int", nargs=2, default=screen_res, help="The x and y size to scale the image to.")
parser.add_option("--verbose", action="store_true", dest="verbose", default=False, help="Verbose")
parser.add_option("--cache-size", action="store", type="int", dest="cache_size", default=3, help="How many images to keep in the go-back and read-ahead caches.")

# Options, parse 'em
(options, selection) = parser.parse_args()

print "Show: " + selection[0]

if options.verbose:
    print options

# If they don't specify files on the command line ask them with zenity
if len(selection) == 0:
    from modules import pythonzenity
    selection = pythonzenity.FileSelection(directory=True, multiple=True)

to_show = []

# Get the file list
for adir in selection:
    for root, dirs, files in os.walk(adir):
        for one_file in files:
            to_show.append(os.path.join(root, one_file))

# Order the files
if options.order:
    to_show = sorted(to_show, key=natural_sort_key)
else:
    shuffle(to_show)

# If they specified the dimensions set the scale variable
options.scale = options.dimensions != (1920, 1080)

# If the desired dimensions match the screen then use fullscreen
if options.dimensions == screen_res:
    cv2.namedWindow("image", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)

# Do some initializations
pos = 0
read_hash = {}
paused = False

ready_processes = []
busy_processes = []
in_processesing = {}
num_threads = cpu_count() - 1

for thread in xrange(0, num_threads):

    # Set up the pipes
    parent_conn, child_conn = Pipe()
    # Start the process
    ready_processes.append([parent_conn, child_conn])

    # Use the fork to get through!
    newpid = os.fork()
    # Okay, we are the child
    if newpid == 0:

        while True:
            try:
                parent_message = child_conn.recv()

                if parent_message == "die":
                    child_conn.close()
                    parent_conn.close()
                    os._exit(0)

                child_conn.send(load_image(parent_message))
            except KeyboardInterrupt:
                child_conn.close()
                parent_conn.close()
                os._exit(0)

    # We are the parent, don't need the child connection
    else:
        child_conn.close()


# Wrap the photo display in this so that we can catch Keyboard interupts
try:
    # Keep showing things
    while pos < len(to_show):

        # Go through the photos in list order
        cur_photo = to_show[pos]

        # Start loading next photo if we aren't at the end, perhaps clear cache
        manage_photos()

        # Wait for our photo to be ready
        wait_for_photo(cur_photo)

        # Get the image from the loaded hash, if there is something there
        #  show it on the screen
        img = read_hash[cur_photo]

        # Only show images that process properly
        if not img is None:
            print "Showing: %s" % cur_photo

            # Infinite timeout if paused
            if paused:
                keycode = show_image(img, wait_time=0)
            else:
                keycode = show_image(img, wait_time=options.time)

            # Figure out what key they pressed
            key = chr(keycode%256) if keycode%256 < 128 else None

            # Check the keycode
            if key == "p":
                pos -= 2
            elif key == " ":
                paused = not paused
                if paused:
                    pos -= 1
                if options.verbose:
                    print {True:"Paused", False:"Unpaused"}[paused]
            elif key == "n":
                pass
            elif key == "q":
                clean_up()
                sys.exit(0)
        else:
            print "Skipping unreadable: %s" % cur_photo

        pos += 1

        # Can't go past start
        if pos < 0:
            pos = 0

except KeyboardInterrupt:
    print "Closing down photo processing threads..."
finally:
    clean_up()
    sys.exit(0)

# We are done
if options.verbose:
    print "Finished showing photos."

