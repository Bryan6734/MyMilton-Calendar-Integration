# this will use tkinter to create a GUI window
# first we need to import TKinter
from tkinter import *
from tkinter import font


def main():
    root = Tk()
    root.title("My Milton Calendar Integration")

    # Create a new Times new Roman font that is bold
    title_font = font.Font(family='Times New Roman', size=50, weight='bold')
    # Create a new TImes new Roamn font that is italics and size 30 named "subtitle_font"
    subtitle_font = font.Font(family='Times New Roman', size=20, slant='italic')
    # Create a new Times new Roman font that is size 20
    body_font = font.Font(family='Times New Roman', size=20)

    # Create a frame to hold all labels and buttons
    frame = Frame(root)

    # don't allow the user to resize
    root.resizable(False, False)

    title = Label(frame, text="MyMilton Calendar Integration", font=title_font)
    title.grid(row=0, column=0, columnspan=4, padx=100, pady=(15, 0))
    subtitle = Label(frame, text="By Bryan Sukidi '24", font=subtitle_font)
    subtitle.grid(row=1, column=0, columnspan=4, pady=(0, 15))

    username_label = Label(frame, text="Username:", font=body_font)
    username_label.grid(row=2, column=0)

    password_label = Label(frame, text="Password:", font=body_font)
    password_label.grid(row=3, column=0)

    username_field = Entry(frame, width=20, name="username")
    username_field.grid(row=2, column=1, sticky=W)

    password_field = Entry(frame, width=20, name="password")
    password_field.grid(row=3, column=1, sticky=W)

    # submit_button = Button(frame, text="Submit", command=lambda: submit(username_field.get(), password_field.get()))
    # submit_button.grid(row=2, column=2, rowspan=2, columnspan=2)

    label1 = Label(frame, text="Test", font=body_font)
    label1.grid(row=2, column=2)

    label2 = Label(frame, text="Test", font=body_font)
    label2.grid(row=2, column=3)

    frame.pack()
    root.mainloop()


def submit(username=None, password=None):
    if username and password:
        print(username, password, sep="\n")


if __name__ == '__main__':
    main()
