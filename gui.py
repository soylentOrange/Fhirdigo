import customtkinter as ctk
from tkinter import filedialog, messagebox
import csv
import os
import json
from fhir.resources.patient import Patient
# from fhirpy import SyncFHIRClient

class CSVDragDropApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Indigo FHIR Sync")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        # self.client = SyncFHIRClient(
        #     'https://fhir.myoncare.care/fhir',
        #     requests_config={
        #         "verify": False,
        #         "allow_redirects": True,
        #         "timeout": 60,
        #     }
        # )

        # Speicher für Patientendaten
        #self.patient_data

        # Theme & Appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Hauptframe
        self.main_frame = ctk.CTkFrame(root, corner_radius=10)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Label
        self.label = ctk.CTkLabel(
            self.main_frame,
            text="Klicke auf den Button, um eine CSV-Datei mit Patientendaten zu öffnen",
            font=("Arial", 14),
            wraplength=500,
            justify="center"
        )
        self.label.pack(pady=20)

        # Button zum Öffnen
        self.open_button = ctk.CTkButton(
            self.main_frame,
            text="📁 Patientendaten wählen und übertragen",
            font=("Arial", 12),
            command=self.open_files,
            width=200,
            height=40,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.open_button.pack(pady=10)

        # Frame für Textfeld + Scrollbar
        self.text_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        self.text_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Scrollbar
        self.scrollbar = ctk.CTkScrollbar(self.text_frame, orientation="vertical")
        self.scrollbar.pack(side="right", fill="y")

        # Textfeld
        self.text_area = ctk.CTkTextbox(
            self.text_frame,
            wrap="word",
            font=("Courier", 10),
            corner_radius=6,
            fg_color="#1e1e1e",
            text_color="white",
            scrollbar_button_color="#333",
            scrollbar_button_hover_color="#555",
            yscrollcommand=self.scrollbar.set
        )
        self.text_area.pack(side="left", fill="both", expand=True)

        # Scrollbar verbinden
        self.scrollbar.configure(command=self.text_area.yview)

        # Speichere die geladenen Dateien
        self.loaded_files = []


    def open_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Patientendaten zur Übertragung wählen",
            filetypes=[("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")]
        )

        if not file_paths:
            return

        for file_path in file_paths:
            self.load_csv(file_path)

        # Aktualisiere Label
        self.label.configure(text=f"{len(file_paths)} Datei(en) geladen")

    def connect(self):
        # Create an instance
        # client = AsyncFHIRClient(
        #    'https://fhir.myoncare.care/fhir'
        # )
        

        # Organisation anlegen
        # # Create Organization resource
        # organization = client.resource(
        #     'Organization',
        #     name='IndigoHL',
        #     active=False
        # )
        # await organization.save()
        # print(json.dumps(organization, indent=2, separators=(',', ': ')))

        # Organisation updaten
        # organization = await client.reference('Organization', '2341').to_resource()
        # print(json.dumps(organization, indent=2, separators=(',', ': ')))
        # if organization['active'] is False:
        #     organization.active = True
        # # if organization['active'] is True:
        # #     organization.active = False
        # await organization.save()
        # print(json.dumps(organization, indent=2, separators=(',', ': ')))

        # ID der Oragnisation IndigoHL abfragen
        # resources = self.client.resources('Organization')  # Return lazy search set
        # resources = resources.search(name='IndigoHL').limit(1).sort('name')
        # organizations = resources.fetch()
        # # print(json.dumps(organizations, indent=2, separators=(',', ': ')))
        # # print('IndigoHL - id ist: ' + organizations[0]['id'])
        # self.text_area.insert("end", f"\n\n{'='*60}\n")
        # self.text_area.insert("end", 'FHIR Sync')
        # self.text_area.insert("end", f"\n{'='*60}\n")
        # self.text_area.insert("end", '\nIndigoHL - id ist: ' + organizations[0]['id'])

        # Patienten anlegen
        #patient = client.resource(
        #    'Patient',
        #    name=[HumanName(text='Patient')]),
        #    active=True
        #)
        ## await organization.save()
        #print(json.dumps(patient, indent=2, separators=(',', ': ')))


        # client.resource()

        # resources = client.resources('Organization')  # Return lazy search set
        # resources = resources.search(name='IndigoHL').limit(1).sort('name')
        # organizations = await resources.fetch()
        # print(json.dumps(organizations, indent=2, separators=(',', ': ')))
        # organization = organizations.to_resource()
        # print(json.dumps(organization, indent=2, separators=(',', ': ')))
        #organizations[1].active = True
        #await organizations[1].save(fields=['active'])

        

        # # Search for patients
        # resources = client.resources('Patient')  # Return lazy search set
        # resources = resources.search(name='Marina').limit(10).sort('name')
        # patients = await resources.fetch()  # Returns list of AsyncFHIRResource
        #patient = await client.reference('Patient', '2').to_resource()
        #patient.serialize()
        #print(patient.serialize())

        #patient = Patient(name=[HumanName(text='Patient')])
        #print(json.dumps(patient, indent=2, separators=(',', ': ')))
        #print(patient.serialize())

        # Scroll nach unten
        self.text_area.see("end")

    def load_csv(self, file_path):
        try:
            with open(file_path, mode="r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)

                # Dateiname anzeigen
                filename = os.path.basename(file_path)
                self.text_area.insert("end", f"\n{'='*60}\n")
                self.text_area.insert("end", f"📁 {filename}\n")
                self.text_area.insert("end", f"{'='*60}\n")

                # Zeige ALLE Zeilen
                if rows:
                    for i, row in enumerate(rows):
                        self.text_area.insert("end", " | ".join(row) + "\n")
                    self.text_area.insert("end", f"\n✅ {len(rows)} Zeilen insgesamt\n")
                else:
                    self.text_area.insert("end", "Die CSV-Datei ist leer.\n")

                # Scroll nach unten
                self.text_area.see("end")

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Lesen von:\n{os.path.basename(file_path)}\n\n{str(e)}")

        # try:
        #     with open(file_path, mode="r", encoding="utf-8") as csvfile:
        #         reader = csv.reader(csvfile)
        #         rows = list(reader)

        #         # Dateiname anzeigen
        #         filename = os.path.basename(file_path)
        #         self.text_area.insert("end", f"\n{'='*60}\n")
        #         self.text_area.insert("end", f"Patienten\n")
        #         self.text_area.insert("end", f"{'='*60}\n")

        #         # Zeige die ersten 10 Zeilen
        #         if rows:
        #             for i, row in enumerate(rows[:10]):
        #                 self.text_area.insert("end", " | ".join(row) + "\n")
        #             if len(rows) > 10:
        #                 self.text_area.insert("end", f"... und {len(rows) - 10} weitere Zeilen\n")
        #         else:
        #             self.text_area.insert("end", "Die CSV-Datei ist leer.\n")

        #         # Scroll nach unten
        #         self.text_area.see("end")

        # except Exception as e:
        #     messagebox.showerror("Fehler", f"Fehler beim parsen von:\n{os.path.basename(file_path)}\n\n{str(e)}")
        #     # Pateinten parsen

        # # FHIR Verbindung herstellen
        # self.connect()
        

# Hauptprogramm starten
if __name__ == "__main__":
    root = ctk.CTk()
    app = CSVDragDropApp(root)
    root.mainloop()