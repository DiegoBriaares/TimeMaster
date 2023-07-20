import tkinter as tk
from tkinter import simpledialog  # Import simpledialog from tkinter
from datetime import datetime, timedelta
import pygame

class Timer:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.start_time = None
        self.elapsed_time = timedelta(seconds=0)
        self.rest_time = timedelta(seconds=0)  # Added rest_time to track rest time
        self.last_rest_time = timedelta(seconds=0)  # Added last_rest_time to track last rest time
        self.is_running = False
        self.is_resting = False  # Added is_resting to track whether the timer is in rest mode
        self.sub_timers = []

    def start(self):
        self.is_running = True
        if not self.is_resting:  # Start time only if not resting
            self.start_time = datetime.now()

    def stop(self):
        if self.is_running:
            if not self.is_resting:  # Only update elapsed_time if not resting
                self.elapsed_time += datetime.now() - self.start_time
            self.is_running = False

    def reset(self):
        self.elapsed_time = timedelta(seconds=0)
        self.rest_time = timedelta(seconds=0)  # Reset rest time on reset
        self.is_running = False

    def rest(self):
        if self.is_running and not self.is_resting:
            self.is_resting = True
            self.rest_start_time = datetime.now()

    def resume(self):
        if self.is_running and self.is_resting:
            rest_duration = datetime.now() - self.rest_start_time
            self.last_rest_time = self.rest_time  # Save the current rest_time as last_rest_time
            self.rest_time += rest_duration
            self.is_resting = False

    def add_sub_timer(self, sub_timer):
        self.sub_timers.append(sub_timer)

    def remove_sub_timer(self, sub_timer):
        self.sub_timers.remove(sub_timer)

    def get_total_time(self):
        total_time = self.elapsed_time - self.rest_time  # Subtract rest time from elapsed time
        for sub_timer in self.sub_timers:
            total_time += sub_timer.get_total_time()
        return total_time

    def get_time_passed(self):
        if self.is_running:
            if not self.is_resting:  # Calculate time passed only if not resting
                return self.elapsed_time + (datetime.now() - self.start_time) - self.rest_time
            else:  # If in rest mode, return elapsed time without counting rest time
                return self.elapsed_time
        return self.elapsed_time - self.rest_time  # Return elapsed time - rest time when not running

    def adjust_elapsed_time(self, rest_time):
        self.elapsed_time -= rest_time

    def adjust_sub_timers(self):
        total_rest_time = self.rest_time - self.last_rest_time  # Use last_rest_time for adjustment
        for sub_timer in self.sub_timers:
            sub_timer.adjust_elapsed_time(total_rest_time)

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timer Application")

        self.current_timer = None
        self.sound_playing = False

        self.main_timer_label = tk.Label(root, text="Main Timer")
        self.main_timer_label.pack()

        self.start_button = tk.Button(root, text="Start Timer", command=self.start_timer)
        self.start_button.pack()

        self.rest_button = tk.Button(root, text="Rest", command=self.rest_timer)
        self.rest_button.pack()

        self.resume_button = tk.Button(root, text="Resume", command=self.resume_timer)
        self.resume_button.pack()

        self.start_sub_timer_button = tk.Button(root, text="Start Sub-Timer", command=self.start_sub_timer)
        self.start_sub_timer_button.pack()

        self.update_timer_label()

    def start_timer(self):
        if self.current_timer:
            self.current_timer.stop()

        self.current_timer = Timer("Main Timer")
        self.current_timer.start()

        self.update_timer_label()

        self.root.after(1000, self.update_timer_label)  # Update label every 1 second

    def rest_timer(self):
        if self.current_timer:
            self.current_timer.rest()

    def resume_timer(self):
        if self.current_timer:
            self.current_timer.resume()
            self.adjust_sub_timers()  # Adjust sub-timers after resuming from rest

    def adjust_sub_timers(self):
        self.current_timer.adjust_sub_timers()

    def start_sub_timer(self):
        if self.current_timer:
            sub_timer_name = simpledialog.askstring("Sub-Timer Name", "Enter Sub-Timer Name:")
            if sub_timer_name is not None:
                sub_timer = Timer(sub_timer_name, self.current_timer)
                sub_timer.start()
                self.current_timer.add_sub_timer(sub_timer)

                sub_timer_frame = tk.Frame(self.root)
                sub_timer_frame.pack()

                sub_timer_label = tk.Label(sub_timer_frame, text=f"{sub_timer.name}: {sub_timer.get_time_passed()}")
                sub_timer_label.pack(side=tk.LEFT)

                stop_sub_timer_button = tk.Button(sub_timer_frame, text="Stop Sub-Timer", command=lambda: self.stop_sub_timer(sub_timer, sub_timer_frame))
                stop_sub_timer_button.pack(side=tk.LEFT)

                self.update_sub_timer_label(sub_timer, sub_timer_label, stop_sub_timer_button)

    def stop_sub_timer(self, sub_timer, frame):
        sub_timer.stop()
        self.current_timer.remove_sub_timer(sub_timer)
        frame.destroy()

        # Save sub-timer details to a text file
        with open("subtimer_details.txt", "a") as f:
            f.write(f"{sub_timer.name}, Time Count: {sub_timer.get_time_passed()}\n")

    # Add a method to handle saving sub-timer details manually
    def save_sub_timer_details(self):
        if self.current_timer:
            with open("subtimer_details.txt", "a") as f:
                f.write(f"{self.current_timer.name}, Time Count: {self.current_timer.get_time_passed()}\n")
            for sub_timer in self.current_timer.sub_timers:
                with open("subtimer_details.txt", "a") as f:
                    f.write(f"{sub_timer.name}, Time Count: {sub_timer.get_time_passed()}\n")

    def update_timer_label(self):
        if self.current_timer:
            time_passed = self.current_timer.get_time_passed()
            time_passed_str = str(time_passed).split('.')[0]

            self.main_timer_label.config(text=f"Main Timer: {time_passed_str}")

            if self.current_timer.is_running:
                self.root.after(1000, self.update_timer_label)  # Update label every 1 second
                self.check_sound(time_passed)

    def check_sound(self, time_passed):
        seconds = int(time_passed.total_seconds())
        if seconds % 1500 == 0 and not self.sound_playing and seconds > 0:
            pygame.mixer.init()
            pygame.mixer.music.load('beep.wav')  # Replace 'beep.wav' with your desired sound file
            pygame.mixer.music.play()
            self.sound_playing = True
            self.root.after(8000, self.stop_sound)  # Stop sound after 5 seconds

    def stop_sound(self):
        pygame.mixer.music.stop()
        self.sound_playing = False

    def update_sub_timer_label(self, timer, label, stop_button):
        if timer.is_running:
            time_passed = timer.get_time_passed()
            time_passed_str = str(time_passed).split('.')[0]
            label.config(text=f"{timer.name}: {time_passed_str}")
            self.root.after(1000, self.update_sub_timer_label, timer, label, stop_button)
        else:
            label.pack_forget()
            stop_button.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
