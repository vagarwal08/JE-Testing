import ttkbootstrap as tb
from gui.app import AuditApp

root = tb.Window(themename="flatly")
AuditApp(root)
root.mainloop()
