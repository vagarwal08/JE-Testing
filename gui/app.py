import ttkbootstrap as tb
from tkinter import filedialog, messagebox
import threading
from core.loader import load_csv
from core.cleaner import clean_columns
from core.joiner import join_bkpf_bseg
from core.feature_engineering import add_features
from rules.sa315_rules import apply_sa315_rules
from ml.anomaly_model import run_ml_anomaly
from reports.excel_report import export_excel


class AuditApp:
    def __init__(self, root):
        self.root = root
        root.title("VA BSEG/BKPF Analyser")
        root.geometry("1100x700")
        root.resizable(True, True)

        self.bkpf = None
        self.bseg = None

        # Top title
        header = tb.Label(root, text="VA BSEG/BKPF Analyser", font=("Segoe UI", 20, "bold"))
        header.pack(pady=(10, 5))

        # Main frame
        main = tb.Frame(root)
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # Left tile frame for actions
        left = tb.Frame(main)
        left.pack(side="left", fill="y", padx=(0, 10))

        tb.Button(left, text="Load BKPF", bootstyle="primary", width=20, command=self.load_bkpf).pack(pady=8)
        tb.Button(left, text="Load BSEG", bootstyle="primary", width=20, command=self.load_bseg).pack(pady=8)
        tb.Button(left, text="Preview Join", bootstyle="secondary", width=20, command=self.preview_join).pack(pady=8)

        # Analysis options
        opts = tb.LabelFrame(left, text="Analysis Options")
        opts.pack(fill="x", pady=10, padx=4)
        self.analysis_var = tb.StringVar(value="complete")
        tb.Radiobutton(opts, text="Complete Analyses", variable=self.analysis_var, value="complete").pack(anchor="w")
        tb.Radiobutton(opts, text="Separate Analyses (Rules Only)", variable=self.analysis_var, value="separate").pack(anchor="w")

        tb.Button(left, text="Run Analytics", bootstyle="success", width=20, command=self.run_async).pack(pady=16)

        # Right frame for status and preview
        right = tb.Frame(main)
        right.pack(side="left", fill="both", expand=True)

        self.status_box = tb.LabelFrame(right, text="Status")
        self.status_box.pack(fill="both", expand=True, padx=6, pady=6)

        self.status_text = tb.Label(self.status_box, text="Waiting for actions...", anchor="nw", justify="left")
        self.status_text.pack(fill="both", expand=True, padx=6, pady=6)

        # Progress bar at bottom
        self.progress = tb.Progressbar(root, mode="determinate")
        self.progress.pack(fill="x", side="bottom", padx=20, pady=10)

    def _set_status(self, text):
        self.status_text.config(text=text)

    def _start_indeterminate(self):
        self.progress.config(mode="indeterminate", maximum=100)
        self.progress.start(20)

    def _stop_progress(self):
        try:
            self.progress.stop()
        except Exception:
            pass
        self.progress.config(mode="determinate", value=0)

    def load_bkpf(self):
        path = filedialog.askopenfilename(title="Select BKPF file", filetypes=[("CSV files", "*.csv"), ("All files", "*")])
        if not path:
            return
        self._set_status(f"Loading BKPF from: {path}")
        self._start_indeterminate()

        def task():
            try:
                df = load_csv(path)
                df = clean_columns(df)
                self.bkpf = df
                self.root.after(0, lambda: self._set_status("BKPF loaded successfully."))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load BKPF: {e}"))
            finally:
                self.root.after(0, self._stop_progress)

        threading.Thread(target=task, daemon=True).start()

    def load_bseg(self):
        path = filedialog.askopenfilename(title="Select BSEG file", filetypes=[("CSV files", "*.csv"), ("All files", "*")])
        if not path:
            return
        self._set_status(f"Loading BSEG from: {path}")
        self._start_indeterminate()

        def task():
            try:
                df = load_csv(path)
                df = clean_columns(df)
                self.bseg = df
                self.root.after(0, lambda: self._set_status("BSEG loaded successfully."))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load BSEG: {e}"))
            finally:
                self.root.after(0, self._stop_progress)

        threading.Thread(target=task, daemon=True).start()

    def preview_join(self):
        if self.bkpf is None or self.bseg is None:
            messagebox.showwarning("Preview Join", "Please load both BKPF and BSEG first.")
            return
        try:
            joined = join_bkpf_bseg(self.bkpf, self.bseg)
            n = len(joined)
            self._set_status(f"Preview: joined dataframe with {n} rows. Ready for analysis.")
        except Exception as e:
            messagebox.showerror("Error", f"Preview failed: {e}")

    def run_async(self):
        if self.bkpf is None or self.bseg is None:
            messagebox.showwarning("Run Analytics", "Please load BKPF and BSEG before running analytics.")
            return
        # disable buttons during run
        for child in self.root.winfo_children():
            child.config(state='disabled')
        self._set_status("Starting analysis...")
        self.progress.config(mode="determinate", maximum=5, value=0)

        def task():
            try:
                # Step 1: join
                self.root.after(0, lambda: self._set_status("Joining BKPF and BSEG..."))
                df = join_bkpf_bseg(self.bkpf, self.bseg)
                self.root.after(0, lambda: self.progress.step(1))

                # Step 2: features
                self.root.after(0, lambda: self._set_status("Adding features..."))
                df = add_features(df)
                self.root.after(0, lambda: self.progress.step(1))

                # Step 3: rules
                self.root.after(0, lambda: self._set_status("Applying SA315 rules..."))
                df = apply_sa315_rules(df)
                self.root.after(0, lambda: self.progress.step(1))

                if self.analysis_var.get() == "complete":
                    # Step 4: ML
                    self.root.after(0, lambda: self._set_status("Running ML anomaly detection..."))
                    df = run_ml_anomaly(df)
                    self.root.after(0, lambda: self.progress.step(1))

                    # Step 5: final score
                    self.root.after(0, lambda: self._set_status("Calculating final risk scores..."))
                    df["FINAL_RISK_SCORE"] = df.get("SA315_SCORE", 0) + df.get("ML_ANOMALY", 0) * 3
                    self.root.after(0, lambda: self.progress.step(1))
                else:
                    # For separate analyses just compute final risk as SA315_SCORE
                    df["FINAL_RISK_SCORE"] = df.get("SA315_SCORE", 0)
                    # update progress to complete
                    self.root.after(0, lambda: self.progress.step(2))

                # Prompt save
                self.root.after(0, lambda: self._set_status("Analysis complete. Asking where to save the output..."))
                save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], initialfile="VA_BSEG_BKPF_Report.xlsx")
                if save_path:
                    export_excel(df, save_path)
                    self.root.after(0, lambda: messagebox.showinfo("Exported", f"Report saved to: {save_path}"))
                    self.root.after(0, lambda: self._set_status(f"Report saved to: {save_path}"))
                else:
                    self.root.after(0, lambda: self._set_status("Save cancelled. Analysis complete."))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis failed: {e}"))
            finally:
                # re-enable UI
                def reenable():
                    for child in self.root.winfo_children():
                        try:
                            child.config(state='normal')
                        except Exception:
                            pass
                    self.progress.config(value=0)

                self.root.after(0, reenable)

        threading.Thread(target=task, daemon=True).start()

