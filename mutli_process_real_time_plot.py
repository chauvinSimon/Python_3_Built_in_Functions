# script to plot stream of data coming from two different sources at a high rate

# implementation of Python multiprocessing with a Queue (Queues are thread and process safe):
# - two producers add new entries to the Queue
# - one consumer updates the plot figure

import time
import random
from collections import deque
from matplotlib import pyplot as plt
from multiprocessing import Process, Queue


class PlotConsumer:
    def __init__(self, max_entries):
        self.counter = 0
        self.fig = plt.figure()
        self.ax = None

        self.data_x = deque(maxlen=max_entries)
        self.data_y = deque(maxlen=max_entries)

    def add_data(self, consumer_queue, line):
        """ update the internal deque objects """
        try:
            while not consumer_queue.empty():
                # x-axis just holds the index
                self.counter += 1
                self.data_x.append(self.counter)

                # remove and return an item from the queue
                new_data = consumer_queue.get_nowait()
                self.data_y.append(new_data)

                line.set_data(self.data_x, self.data_y)

            plt.pause(0.005)  # to be tuned

            # Recompute the data limits
            self.ax.relim()
            self.ax.set_ylim([-0.5, 1.5])
            # Auto-scale the view limits using the data limits
            self.ax.autoscale_view(tight=None, scalex=True, scaley=False)

        except Exception as e:
            print("Exception = {}".format(e))
            pass

    def plot_update(self, consumer_queue):
        """ update the figure """

        # In the current figure, create an Axes object
        self.ax = self.fig.add_subplot(111)
        self.ax.grid()

        # Turn interactive mode on
        plt.ion()

        # create a Line2D object [matplotlib.lines.Line2D]
        line_object, = self.ax.plot([], [], 'c', linestyle="-.")  # Returns a tuple of line objects, thus the comma

        while True:
            self.add_data(consumer_queue, line_object)
            plt.xlabel('# data entry = {}'.format(self.counter), fontsize=18)
            plt.ylabel('data value [unit]', fontsize=18)
            plt.show()


def producer(producer_queue, name_producer=""):
    while True:
        time.sleep(0.1)
        new_value = random.random()
        producer_queue.put_nowait(new_value)
        print("producer {} added {:0.2f}".format(name_producer, new_value))
        print("queue has size = {}".format(producer_queue.qsize()))


def main():
    window_size = 30
    queue_size = 30

    data_queue = Queue(queue_size)
    display = PlotConsumer(window_size)

    serial_process_one = Process(target=producer, args=(data_queue, "one"))
    serial_process_two = Process(target=producer, args=(data_queue, "two"))
    plot_process = Process(target=display.plot_update, args=(data_queue,))

    serial_process_one.start()
    serial_process_two.start()
    plot_process.start()


if __name__ == "__main__":
    main()
