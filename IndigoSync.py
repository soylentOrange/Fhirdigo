import customtkinter as ctk
from tkinter import filedialog, messagebox
import csv
import json
import os
import requests
from datetime import datetime

def load_env_file(filepath=".env"):
    """Lädt Umgebungsvariablen aus einer .env-Datei ohne externe Abhängigkeiten."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filepath)
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = val

load_env_file()

# Drag & Drop Unterstützung über tkinterdnd2 (optional)
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES  # type: ignore
    HAS_DND = True
except (ImportError, ModuleNotFoundError):
    HAS_DND = False
    DND_FILES = None

# CustomTkinter CTk-Fenster mit optionaler Drag & Drop-Erweiterung
if HAS_DND:
    class AppRoot(ctk.CTk, TkinterDnD.DnDWrapper):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.TkdndVersion = TkinterDnD._require(self)
else:
    class AppRoot(ctk.CTk):
        pass

class CSVtoFHIRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV zu FHIR Upload")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        self.base_url = os.getenv("FHIR_BASE_URL", "https://token.myoncare.care/firebaseManager/fhir")
        auth_key = os.getenv("FHIR_AUTH_KEY", "")
        self.fhir_auth = f"?key={auth_key}" if auth_key else ""

        # Theme & Appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Hauptframe
        self.main_frame = ctk.CTkFrame(root, corner_radius=10)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Titel
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="🏥 CSV zu FHIR Upload",
            font=("Arial", 16, "bold"),
            justify="center"
        )
        self.title_label.pack(pady=20)

        # Info-Label
        self.info_label = ctk.CTkLabel(
            self.main_frame,
            text="CSV-Datei mit Patientendaten öffnen\nund via FHIR exportieren",
            font=("Arial", 12),
            text_color="#888",
            justify="center"
        )
        self.info_label.pack(pady=10)

        # Button Frame
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(pady=20)

        # Button zum Öffnen
        self.open_button = ctk.CTkButton(
            self.button_frame,
            text="📁 CSV-Datei öffnen",
            font=("Arial", 12),
            command=self.open_file,
            width=200,
            height=45,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.open_button.pack(side="left", padx=10)

        # Export Button
        self.export_button = ctk.CTkButton(
            self.button_frame,
            text="🔥 FHIR upload",
            font=("Arial", 12),
            command=self.export_json,
            width=200,
            height=45,
            corner_radius=8,
            fg_color="#2196F3",
            hover_color="#1976D2",
            state="disabled"
        )
        self.export_button.pack(side="left", padx=10)

        # Status Label (zeigt Anzahl der Patienten)
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="⏳ Keine Datei geladen",
            font=("Arial", 14, "bold"),
            text_color="#888"
        )
        self.status_label.pack(pady=30)

        # Patienten-Daten speichern
        self.fhir_patients = []
        self.loaded_file = None

        # Drag & Drop aktivieren
        if HAS_DND and DND_FILES:
            try:
                self.root.drop_target_register(DND_FILES)
                self.root.dnd_bind('<<Drop>>', self.on_drop)
                print("✅ Drag & Drop aktiviert!")
            except Exception as e:
                print(f"⚠️ Drag & Drop Initialisierungsfehler: {e}")
        else:
            print("⚠️ Drag & Drop nicht verfügbar (tkinterdnd2 nicht installiert)")

    def on_drop(self, event):
        try:
            # tk.splitlist handhabt Pfade mit Leerzeichen auf macOS & Windows sicher
            file_paths = self.root.tk.splitlist(event.data)
            for path in file_paths:
                path = path.strip("{}")
                if path.lower().endswith(".csv"):
                    self.load_csv(path)
                    break
        except Exception as e:
            print(f"❌ Fehler bei Drag & Drop: {e}")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="CSV-Datei öffnen",
            filetypes=[("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")]
        )
        if file_path:
            self.load_csv(file_path)

    def detect_delimiter(self, file_path):
        """Erkennt automatisch das Trennzeichen"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                first_line = f.readline()
                if ';' in first_line and ',' not in first_line:
                    return ';'
                return ','
        except:
            return ','

    def convert_date_format(self, date_str):
        """Konvertiert DD.MM.YYYY zu YYYY-MM-DD (FHIR Standard)"""
        if not date_str:
            return None
        try:
            date_part = date_str.split()[0] if ' ' in date_str else date_str
            dt = datetime.strptime(date_part, "%d.%m.%Y")
            return dt.strftime("%Y-%m-%d")
        except:
            return date_str

    def convert_gender(self, gender_str):
        """Konvertiert M/W zu FHIR gender codes"""
        if not gender_str:
            return "unknown"
        gender_map = {
            "M": "Male",
            "m": "Male",
            "W": "Female",
            "w": "Female",
            "male": "Male",
            "female": "Female",
            "divers": "",
            "D": ""
        }
        return gender_map.get(gender_str.strip(), "unknown")

    def create_fhir_patient(self, row, index):
        """Erstellt ein FHIR Patient Objekt aus CSV Zeile"""

        patient_object = {
            "resourceType": "Patient",
            "gender": self.convert_gender(row.get("GESCHLECHT", "")),
            "birthDate": self.convert_date_format(row.get("Geb_Datum", "")),
            "name": [
                {
                    "use": "official",
                    "family": row.get("Name", "").strip(),
                    "given": [row.get("Vorname", "").strip()]
                }
            ],
            "active": True,
            "managingOrganization": {
                "reference": "Organization/1"
            },
            "identifier": [
                {
                    "use": "usual",
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                "code": "MR"
                            }
                        ]
                    },
                    "system": "urn:oid:1.2.36.146.595.217.0.1",
                    "value": row.get("Hauptfall", "").strip(),
                    "period": {
                        "start": self.convert_date_format(row.get("Aufnahme", ""))
                    },
                    "assigner": {
                        "display": "UKSH"
                    }
                },
                {
                    "use": "usual",                    
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                "code": "MR"
                            }
                        ]
                    },
                    "system": "urn:oid:1.2.36.146.595.217.0.1",
                    "value": row.get("Hauptfall", "").strip(),
                    "period": {
                        "start": self.convert_date_format(row.get("Aufnahme", ""))
                    },
                    "assigner": {
                        "display": "MyOncare"
                    }
                }
            ]
        }
        
        # patient = {
        #     "resourceType": "Patient",
        #     "id": f"patient-{index + 1}",
        #     "meta": {
        #         "profile": ["http://hl7.org/fhir/StructureDefinition/Patient"]
        #     },
        #     "identifier": [
        #         {
        #             "use": "official",
        #             "type": {
        #                 "coding": [
        #                     {
        #                         "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
        #                         "code": "MR",
        #                         "display": "Medical Record Number"
        #                     }
        #                 ]
        #             },
        #             "system": "http://hospital.example.org/patients",
        #             "value": row.get("Hauptfall", "").strip()
        #         }
        #     ],
        #     "name": [
        #         {
        #             "use": "official",
        #             "family": row.get("Name", "").strip(),
        #             "given": [row.get("Vorname", "").strip()]
        #         }
        #     ],
        #     "gender": self.convert_gender(row.get("GESCHLECHT", "")),
        #     "birthDate": self.convert_date_format(row.get("Geb_Datum", ""))
        # }

        # # Zusätzliche Identifier (DRG, ICD)
        # additional_ids = []
        
        # if row.get("DRG", "").strip():
        #     additional_ids.append({
        #         "use": "secondary",
        #         "type": {
        #             "coding": [
        #                 {
        #                     "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
        #                     "code": "DN",
        #                     "display": "Diploma Number"
        #                 }
        #             ]
        #         },
        #         "system": "http://hospital.example.org/drg",
        #         "value": row.get("DRG", "").strip()
        #     })

        # if row.get("ICD_HD", "").strip():
        #     additional_ids.append({
        #         "use": "secondary",
        #         "type": {
        #             "coding": [
        #                 {
        #                     "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
        #                     "code": "DIAG",
        #                     "display": "Diagnosis Number"
        #                 }
        #             ]
        #         },
        #         "system": "http://hl7.org/fhir/sid/icd-10",
        #         "value": row.get("ICD_HD", "").strip()
        #     })

        # if additional_ids:
        #     patient["identifier"].extend(additional_ids)

        # # Extension für OPS-Prozedur
        # if row.get("ICPM", "").strip() or row.get("Datum_OPS", "").strip():
        #     patient["extension"] = [
        #         {
        #             "url": "http://hospital.example.org/fhir/StructureDefinition/procedure-info",
        #             "extension": [
        #                 {
        #                     "url": "procedureCode",
        #                     "valueCodeableConcept": {
        #                         "coding": [
        #                             {
        #                                 "system": "http://fhir.de/CodeSystem/bps/ops",
        #                                 "code": row.get("ICPM", "").strip(),
        #                                 "display": "OPS Code"
        #                             }
        #                         ]
        #                     }
        #                 }
        #             ]
        #         }
        #     ]
            
        #     if row.get("Datum_OPS", "").strip():
        #         patient["extension"][0]["extension"].append({
        #             "url": "procedureDate",
        #             "valueDateTime": row.get("Datum_OPS", "").strip()
        #         })

        # # Extension für Krankenhaus-Informationen
        # hospital_info = []
        
        # if row.get("OE_DFD", "").strip():
        #     hospital_info.append({
        #         "url": "department",
        #         "valueString": row.get("OE_DFD", "").strip()
        #     })
        
        # if row.get("OE_Fall", "").strip():
        #     hospital_info.append({
        #         "url": "caseUnit",
        #         "valueString": row.get("OE_Fall", "").strip()
        #     })

        # if row.get("Aufnahme", "").strip():
        #     hospital_info.append({
        #         "url": "admissionDate",
        #         "valueDateTime": row.get("Aufnahme", "").strip()
        #     })

        # if row.get("Entlassung", "").strip():
        #     hospital_info.append({
        #         "url": "dischargeDate",
        #         "valueDateTime": row.get("Entlassung", "").strip()
        #     })

        # if hospital_info:
        #     patient["extension"].append({
        #         "url": "http://hospital.example.org/fhir/StructureDefinition/hospital-encounter",
        #         "extension": hospital_info
        #     })

        return patient_object

    def load_csv(self, file_path):
        try:
            self.fhir_patients = []
            
            delimiter = self.detect_delimiter(file_path)
            print(f"🔍 Erkanntes Trennzeichen: '{delimiter}'")

            encodings = ['utf-8-sig', 'utf-8', 'windows-1252', 'iso-8859-1']
            success = False

            for encoding in encodings:
                try:
                    with open(file_path, mode="r", encoding=encoding, newline='') as csvfile:
                        reader = csv.DictReader(csvfile, delimiter=delimiter)
                        
                        if reader.fieldnames:
                            reader.fieldnames = [f.strip() for f in reader.fieldnames]
                            print(f"📋 Gefundene Spalten: {reader.fieldnames}")

                        index = 0
                        for row in reader:
                            if not row or not any(row.values()):
                                continue
                            
                            hauptfall = row.get("Hauptfall", "").strip()
                            if not hauptfall:
                                continue

                            fhir_patient = self.create_fhir_patient(row, index)
                            self.fhir_patients.append(fhir_patient)
                            index += 1
                    
                    success = True
                    print(f"✅ Kodierung erfolgreich: {encoding}")
                    break

                except UnicodeDecodeError:
                    continue

            if not success:
                raise Exception("Keine passende Kodierung gefunden.")

            if not self.fhir_patients:
                messagebox.showwarning("Warnung", "Keine gültigen Patienten-Daten gefunden!")
                return

            # Nur Anzahl anzeigen (keine Vorschau)
            filename = os.path.basename(file_path)
            self.loaded_file = file_path
            self.status_label.configure(
                text=f"✅ {len(self.fhir_patients)} Patienten erkannt",
                text_color="#4CAF50"
            )
            self.info_label.configure(
                text=f"Datei: {filename}",
                text_color="#888"
            )

            # Export-Button aktivieren
            self.export_button.configure(state="normal")

            print(f"✅ {len(self.fhir_patients)} FHIR-Patienten erkannt")

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Lesen der CSV:\n{str(e)}")
            print(f"❌ Fehler: {str(e)}")
            self.status_label.configure(
                text="❌ Fehler beim Laden",
                text_color="#F44336"
            )

    def export_json(self):
        if not self.fhir_patients:
            messagebox.showwarning("Warnung", "Keine Patienten-Daten zum Exportieren.")
            return

        try:
            # Hier per FHIR exportieren
            for patient in self.fhir_patients:
                response = requests.post(self.base_url + '/Patient' + self.fhir_auth, json=patient)                
                print(json.dumps(patient, indent=2, separators=(',', ': ')))
                print('Status:' + str(response.status_code))
                print(response.content)

            messagebox.showinfo(
                "Erfolg", 
                f"✅ {len(self.fhir_patients)} FHIR Patient(en) erfolgreich exportiert\n"
            )
            self.status_label.configure(
                text=f"✅ Exportiert: {len(self.fhir_patients)} Patienten",
                text_color="#4CAF50"
            )

            # deactivate export button
            self.export_button.configure(state="disabled")

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim FHIR-Upload:\n{str(e)}")


# Hauptprogramm starten
if __name__ == "__main__":
    root = AppRoot()
    app = CSVtoFHIRApp(root)
    root.mainloop()