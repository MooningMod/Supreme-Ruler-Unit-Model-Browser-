#!/usr/bin/env python3
"""
Supreme Ruler Unit Model Browser (Multi-Instance & Quick Switch)
==============================================================
Features:
- Quick Switch Dropdown in main toolbar.
- Multiple 3D Viewer instances allowed.
- JSON configuration.
- Auto-cleanup of viewer processes on exit.
- FIXED: Settings radio buttons now work correctly.

Author: SR Modding Community
"""

import sys
import os
import subprocess
import csv
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, List

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem, QLabel,
    QGroupBox, QGridLayout, QComboBox, QMessageBox, QFileDialog,
    QSplitter, QTextEdit, QRadioButton, QButtonGroup, QFrame,
    QTabWidget
)

# =============================================================================
# CONFIGURATION MANAGER (Invariato)
# =============================================================================

class ConfigManager:
    FILENAME = "config.json"
    
    DEFAULTS = {
        "mode": "SR2030",
        "SRU": {
            "unit_file": r"C:\Program Files (x86)\Steam\steamapps\common\Supreme Ruler Ultimate\Maps\DATA\default.unit",
            "meshes_path": r"C:\Program Files (x86)\Steam\steamapps\common\Supreme Ruler Ultimate\Graphics\Meshes",
            "viewer_path": "mview.exe"
        },
        "SR2030": {
            "unit_file": r"C:\Program Files (x86)\Steam\steamapps\common\Supreme Ruler 2030\Maps\DATA\default.unit",
            "meshes_path": r"C:\Program Files (x86)\Steam\steamapps\common\Supreme Ruler 2030\Graphics\Meshes",
            "viewer_path": "DirectXTKModelViewer.exe"
        }
    }

    def __init__(self):
        self.data = self.DEFAULTS.copy()
        self.load()

    def load(self):
        if os.path.exists(self.FILENAME):
            try:
                with open(self.FILENAME, 'r') as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except Exception as e:
                print(f"Error loading JSON: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(self.FILENAME, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving JSON: {e}")

    def get_game_config(self, mode):
        return self.data.get(mode, self.DEFAULTS["SR2030"])

    def update_game_config(self, mode, unit_file, meshes_path, viewer_path):
        if mode not in self.data:
            self.data[mode] = {}
        self.data[mode]["unit_file"] = unit_file
        self.data[mode]["meshes_path"] = meshes_path
        self.data[mode]["viewer_path"] = viewer_path
        self.save()

    def set_mode(self, mode):
        self.data["mode"] = mode
        self.save()

# =============================================================================
# DATA PARSER (Invariato)
# =============================================================================

@dataclass
class SimpleUnit:
    id: int
    name: str
    picnum: int = 0
    unit_class: int = 0
    category: str = "unknown"
    regions: str = ""  # Region codes (e.g., "M", "G", "US")

def parse_units_robust(filepath: str) -> List[SimpleUnit]:
    units = []
    start_parsing = False
    
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            reader = csv.reader(lines)
            
            for row in reader:
                if not row: continue
                
                # Check for marker
                if len(row) > 0 and "&&UNITS" in row[0]:
                    start_parsing = True
                    continue
                
                if not start_parsing: continue
                if len(row) < 4: continue
                
                # Skip comments
                if row[0].strip().startswith('//') or not row[0].strip().isdigit():
                    continue
                    
                try:
                    unit_id = int(row[0])
                    name = row[1].strip()
                    u_class = int(row[2].strip()) if row[2].strip() else 0
                    pic = int(row[3].strip()) if row[3].strip() else 0
                    
                    # Regions is column 12 (index 12)
                    regions = row[12].strip() if len(row) > 12 else ""
                    
                    if u_class <= 6: category = "land"
                    elif u_class <= 12: category = "air"
                    else: category = "naval"
                    
                    units.append(SimpleUnit(unit_id, name, pic, u_class, category, regions))
                except ValueError:
                    continue
    except Exception as e:
        print(f"[Parser Error] {e}")
    
    return units

# =============================================================================
# MAIN WINDOW
# =============================================================================

class UnitModelBrowser(QMainWindow):
    
    # Region codes for SR2030 (supports lowercase)
    REGIONS_SR2030 = [
        ("All Regions", None),
        ("*/@ (Global/Export)", "*"),
        ("── UPPERCASE ──", None),
        ("A (South Africa)", "A"),
        ("B (Argentina)", "B"),
        ("C (China)", "C"),
        ("D (Netherlands)", "D"),
        ("E (Europe/Ireland)", "E"),
        ("F (France)", "F"),
        ("G (Germany)", "G"),
        ("H (Italy)", "H"),
        ("I (Israel)", "I"),
        ("J (Japan)", "J"),
        ("K (South Korea)", "K"),
        ("L (North Korea)", "L"),
        ("M (UK/British)", "M"),
        ("N (Canada)", "N"),
        ("O (Other)", "O"),
        ("P (Philippines)", "P"),
        ("Q (India)", "Q"),
        ("R (Russia)", "R"),
        ("S (Sweden)", "S"),
        ("T (Czech)", "T"),
        ("U (USA)", "U"),
        ("V (Taiwan)", "V"),
        ("W (World Export)", "W"),
        ("X (Balkans/Yugoslavia)", "X"),
        ("Y (Singapore)", "Y"),
        ("Z (Arab)", "Z"),
        ("── LOWERCASE ──", None),
        ("a (Austria)", "a"),
        ("b (Brazil)", "b"),
        ("c (Belgium)", "c"),
        ("d (Denmark)", "d"),
        ("e (Spain)", "e"),
        ("f (Finland)", "f"),
        ("g (Greece)", "g"),
        ("h (Poland)", "h"),
        ("i (Iran)", "i"),
        ("j (Romania)", "j"),
        ("k (Norway)", "k"),
        ("l (Indonesia)", "l"),
        ("m (Pakistan)", "m"),
        ("n (Australia)", "n"),
        ("o (E. Europe Generic)", "o"),
        ("p (Portugal)", "p"),
        ("q (Iraq)", "q"),
        ("r (Former Soviet/Belarus)", "r"),
        ("s (Switzerland)", "s"),
        ("t (Turkey)", "t"),
        ("u (Ukraine)", "u"),
        ("v (Oceania/Pacific)", "v"),
        ("w (Sub-Saharan Africa)", "w"),
        ("x (SE Asia Generic)", "x"),
        ("z (New Zealand)", "z"),
        ("── OTHER ──", None),
        ("Custom...", "CUSTOM"),
    ]
    
    # Region codes for SRU (uppercase only)
    REGIONS_SRU = [
        ("All Regions", None),
        ("*/@ (Global/Export)", "*"),
        ("A (South Africa)", "A"),
        ("B (Brazil/Argentina)", "B"),
        ("C (China)", "C"),
        ("D (BeNeLux)", "D"),
        ("E (Europe/Ireland/Spain/Portugal/Turkey/Greece)", "E"),
        ("F (France)", "F"),
        ("G (Germany)", "G"),
        ("H (Italy)", "H"),
        ("I (Israel)", "I"),
        ("J (Japan)", "J"),
        ("K (South Korea)", "K"),
        ("L (North Korea)", "L"),
        ("M (UK/British)", "M"),
        ("N (Canada/Australia)", "N"),
        ("O (Other)", "O"),
        ("Q (India)", "Q"),
        ("R (Russia/Ukraine/Soviet/Belarus)", "R"),
        ("S (Sweden/Swiss/Denmark/Norway)", "S"),
        ("T (Czech/Austria/Yugoslavia/Finland/Poland/Romania)", "T"),
        ("U (USA)", "U"),
        ("V (Taiwan/Philippines)", "V"),
        ("W (World Export)", "W"),
        ("X (Yugoslav)", "X"),
        ("Y (Pacific/Singapore)", "Y"),
        ("Z (Arab/Iran/Iraq/Pakistan)", "Z"),
        ("── OTHER ──", None),
        ("Custom...", "CUSTOM"),
    ]
    
    def __init__(self):
        super().__init__()
        
        # Config & State
        self.config = ConfigManager()
        self.current_mode = self.config.data.get("mode", "SR2030")
        self.units: List[SimpleUnit] = []
        
        # List to keep track of multiple open viewers
        self.active_viewers = [] 
        self.selected_mesh_path = None
        
        self.init_ui()
        
        # Sync UI with config state
        self.sync_combo_box()     # Set main dropdown
        self.sync_settings_radio() # Set settings radio buttons
        self.refresh_settings_ui() # Load text fields
        
        # Auto-load on startup
        if os.path.exists(self.path_unit.text()):
            self.load_data(switch_tab=False)
        
        # Timer to update viewer count (in case users close viewers manually)
        self.viewer_timer = QTimer()
        self.viewer_timer.timeout.connect(self.update_viewer_count)
        self.viewer_timer.start(2000)  # Every 2 seconds

    def init_ui(self):
        self.setWindowTitle(f"Supreme Ruler Unit Browser - {self.current_mode}")
        self.resize(1200, 800)
        
        # Main Tab Widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # --- TAB 1: BROWSER ---
        self.tab_browser = QWidget()
        self.setup_browser_tab()
        self.tabs.addTab(self.tab_browser, "🔍 Browser")
        
        # --- TAB 2: SETTINGS ---
        self.tab_settings = QWidget()
        self.setup_settings_tab()
        self.tabs.addTab(self.tab_settings, "⚙️ Settings")

    def setup_browser_tab(self):
        layout = QVBoxLayout(self.tab_browser)
        
        # Top Bar (Quick Switch + Reload)
        top_bar = QHBoxLayout()
        
        top_bar.addWidget(QLabel("<b>Current Profile:</b>"))
        
        # Quick Switch Combo Box
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["SR 2030", "SR Ultimate"])
        self.combo_mode.setMinimumWidth(150)
        self.combo_mode.activated.connect(self.on_quick_switch)
        
        top_bar.addWidget(self.combo_mode)
        top_bar.addStretch()
        
        btn_reload = QPushButton("🔄 Reload Data")
        btn_reload.clicked.connect(lambda: self.load_data(switch_tab=False))
        top_bar.addWidget(btn_reload)
        
        layout.addLayout(top_bar)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # LEFT: List & Filter
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0,0,0,0)
        
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Unit Name or ID...")
        self.search_input.textChanged.connect(self.filter_list)
        
        self.cat_combo = QComboBox()
        self.cat_combo.addItems(["All", "Land", "Air", "Naval"])
        self.cat_combo.currentTextChanged.connect(self.filter_list)
        
        filter_layout.addWidget(self.search_input, 3)
        filter_layout.addWidget(self.cat_combo, 1)
        left_layout.addLayout(filter_layout)
        
        # Second row: Sort and Region filter
        filter_row2 = QHBoxLayout()
        
        # Sort dropdown
        filter_row2.addWidget(QLabel("Sort:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["ID ↑", "ID ↓", "Name A-Z", "Name Z-A", "Class", "Picnum"])
        self.sort_combo.currentTextChanged.connect(self.filter_list)
        filter_row2.addWidget(self.sort_combo)
        
        # Region filter (will be populated based on game)
        filter_row2.addWidget(QLabel("Region:"))
        self.region_combo = QComboBox()
        self.region_combo.currentTextChanged.connect(self.filter_list)
        filter_row2.addWidget(self.region_combo, 1)
        
        left_layout.addLayout(filter_row2)
        
        # Reverse Picnum Lookup
        picnum_layout = QHBoxLayout()
        picnum_layout.addWidget(QLabel("🔍 Find by Picnum:"))
        self.picnum_input = QLineEdit()
        self.picnum_input.setPlaceholderText("Enter picnum (e.g. 450)")
        self.picnum_input.setMaximumWidth(120)
        self.picnum_input.returnPressed.connect(self.search_by_picnum)
        picnum_layout.addWidget(self.picnum_input)
        btn_picnum = QPushButton("Search")
        btn_picnum.clicked.connect(self.search_by_picnum)
        picnum_layout.addWidget(btn_picnum)
        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self.clear_picnum_search)
        picnum_layout.addWidget(btn_clear)
        picnum_layout.addStretch()
        left_layout.addLayout(picnum_layout)
        
        self.unit_list = QListWidget()
        self.unit_list.setFont(QFont("Consolas", 10))
        self.unit_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.unit_list.itemDoubleClicked.connect(self.launch_viewer)
        left_layout.addWidget(self.unit_list)
        
        self.lbl_count = QLabel("0 units loaded")
        left_layout.addWidget(self.lbl_count)
        
        # Format indicator
        self.lbl_format = QLabel("")
        self.lbl_format.setStyleSheet("color: #888; font-style: italic;")
        left_layout.addWidget(self.lbl_format)
        self.update_format_label()
        
        splitter.addWidget(left_widget)
        
        # RIGHT: Details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10,0,0,0)
        
        # Info Group
        info_grp = QGroupBox("Unit Information")
        info_grid = QGridLayout(info_grp)
        
        self.lbl_name = QLabel("-")
        self.lbl_name.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_id = QLabel("-")
        self.lbl_class = QLabel("-")
        self.lbl_picnum = QLabel("-")
        self.lbl_picnum.setStyleSheet("color: #42A5F5; font-weight: bold;")
        self.lbl_regions = QLabel("-")
        self.lbl_regions.setStyleSheet("color: #FFA726;")
        self.lbl_mesh_file = QLabel("-")
        
        info_grid.addWidget(QLabel("Name:"), 0, 0); info_grid.addWidget(self.lbl_name, 0, 1)
        info_grid.addWidget(QLabel("ID:"), 1, 0); info_grid.addWidget(self.lbl_id, 1, 1)
        info_grid.addWidget(QLabel("Class:"), 2, 0); info_grid.addWidget(self.lbl_class, 2, 1)
        info_grid.addWidget(QLabel("Picnum:"), 3, 0); info_grid.addWidget(self.lbl_picnum, 3, 1)
        info_grid.addWidget(QLabel("Regions:"), 4, 0); info_grid.addWidget(self.lbl_regions, 4, 1)
        info_grid.addWidget(QLabel("Mesh File:"), 5, 0); info_grid.addWidget(self.lbl_mesh_file, 5, 1)
        
        right_layout.addWidget(info_grp)
        
        # Status Box
        self.status_mesh = QLabel("Select a unit")
        self.status_mesh.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.status_mesh.setAlignment(Qt.AlignCenter)
        self.status_mesh.setMinimumHeight(40)
        self.status_mesh.setStyleSheet("background: #444; color: #AAA; font-weight: bold;")
        right_layout.addWidget(self.status_mesh)
        
        # View Button
        self.btn_view = QPushButton("🎮 Launch 3D Viewer")
        self.btn_view.setToolTip("Opens a new viewer window. You can open multiple windows to compare models.")
        self.btn_view.setMinimumHeight(50)
        self.btn_view.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.btn_view.setEnabled(False)
        self.btn_view.clicked.connect(self.launch_viewer)
        right_layout.addWidget(self.btn_view)
        
        # Viewer counter & Open Folder button
        viewer_bar = QHBoxLayout()
        self.lbl_viewers = QLabel("Viewers open: 0")
        self.lbl_viewers.setStyleSheet("color: #888;")
        viewer_bar.addWidget(self.lbl_viewers)
        
        btn_close_all = QPushButton("✖ Close All")
        btn_close_all.setToolTip("Close all open viewer windows")
        btn_close_all.clicked.connect(self.close_all_viewers)
        viewer_bar.addWidget(btn_close_all)
        
        viewer_bar.addStretch()
        btn_folder = QPushButton("📂 Open Meshes Folder")
        btn_folder.clicked.connect(self.open_meshes_folder)
        viewer_bar.addWidget(btn_folder)
        right_layout.addLayout(viewer_bar)
        
        # Textures & Mesh Info
        right_layout.addWidget(QLabel("📦 Textures & Mesh Info:"))
        self.txt_textures = QTextEdit()
        self.txt_textures.setReadOnly(True)
        right_layout.addWidget(self.txt_textures)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([450, 750])
        
        layout.addWidget(splitter)

    def setup_settings_tab(self):
        layout = QVBoxLayout(self.tab_settings)
        
        form_group = QGroupBox("Paths Configuration")
        grid = QGridLayout(form_group)
        
        # Mode Select (Settings only)
        mode_layout = QHBoxLayout()
        self.rb_2030 = QRadioButton("SR 2030")
        self.rb_sru = QRadioButton("SR Ultimate")
        
        self.bg_mode = QButtonGroup()
        self.bg_mode.addButton(self.rb_2030)
        self.bg_mode.addButton(self.rb_sru)
        
        # FIX: Just connect to refresh text fields, don't override check state
        self.bg_mode.buttonClicked.connect(self.refresh_settings_ui)
        
        mode_layout.addWidget(QLabel("<b>Profile to Edit:</b>"))
        mode_layout.addWidget(self.rb_2030)
        mode_layout.addWidget(self.rb_sru)
        mode_layout.addStretch()
        
        grid.addLayout(mode_layout, 0, 0, 1, 3)
        
        # Inputs
        self.path_unit = QLineEdit()
        self.path_meshes = QLineEdit()
        self.path_viewer = QLineEdit()
        
        self.add_path_row(grid, 1, "Unit File:", self.path_unit, self.browse_unit)
        self.add_path_row(grid, 2, "Meshes Dir:", self.path_meshes, self.browse_meshes)
        self.add_path_row(grid, 3, "Viewer Exe:", self.path_viewer, self.browse_viewer)
        
        layout.addWidget(form_group)
        
        # Save Button
        btn_save = QPushButton("💾 Save Settings & Load Data")
        btn_save.setMinimumHeight(45)
        btn_save.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; font-size: 13px;")
        btn_save.clicked.connect(self.save_and_load)
        
        layout.addWidget(btn_save)
        layout.addStretch()

    def add_path_row(self, layout, row, label, line_edit, browse_func):
        layout.addWidget(QLabel(label), row, 0)
        layout.addWidget(line_edit, row, 1)
        btn = QPushButton("Browse")
        btn.clicked.connect(browse_func)
        layout.addWidget(btn, row, 2)

    # =========================================================================
    # LOGIC
    # =========================================================================

    def sync_combo_box(self):
        """Ensure the browser dropdown matches self.current_mode."""
        if self.current_mode == "SRU":
            self.combo_mode.setCurrentIndex(1) # SR Ultimate
        else:
            self.combo_mode.setCurrentIndex(0) # SR 2030
        self.update_format_label()
        self.update_region_combo()

    def update_format_label(self):
        """Update the format indicator label."""
        if self.current_mode == "SRU":
            self.lbl_format.setText("📁 Format: .X (DirectX Mesh)")
        else:
            self.lbl_format.setText("📁 Format: .CMO (VS Content Mesh)")

    def update_region_combo(self):
        """Update region filter options based on current game."""
        self.region_combo.blockSignals(True)
        self.region_combo.clear()
        
        regions = self.REGIONS_SRU if self.current_mode == "SRU" else self.REGIONS_SR2030
        
        for label, code in regions:
            if label.startswith("──"):
                # Separator item (disabled)
                self.region_combo.addItem(label)
                idx = self.region_combo.count() - 1
                self.region_combo.model().item(idx).setEnabled(False)
            else:
                self.region_combo.addItem(label)
        
        self.region_combo.blockSignals(False)

    def sync_settings_radio(self):
        """Force the settings radio buttons to match self.current_mode."""
        if self.current_mode == "SRU":
            self.rb_sru.setChecked(True)
        else:
            self.rb_2030.setChecked(True)

    def on_quick_switch(self):
        """Handle quick profile switch from the browser dropdown."""
        selection = self.combo_mode.currentText()
        if selection == "SR 2030":
            new_mode = "SR2030"
        else:
            new_mode = "SRU"
        
        if new_mode != self.current_mode:
            self.current_mode = new_mode
            self.config.set_mode(new_mode)
            self.setWindowTitle(f"Supreme Ruler Unit Browser - {new_mode}")
            self.update_format_label()
            self.update_region_combo()
            
            # Sync Settings Tab to new mode
            self.sync_settings_radio()
            self.refresh_settings_ui()
            
            # Reload data for the new mode
            self.load_data(switch_tab=False)

    def refresh_settings_ui(self):
        """
        Update Settings tab text fields based on which radio button is currently CHECKED.
        Does NOT change the radio button state itself.
        """
        if self.rb_sru.isChecked():
            ui_mode = "SRU"
        else:
            ui_mode = "SR2030"
        
        data = self.config.get_game_config(ui_mode)
        self.path_unit.setText(data.get("unit_file", ""))
        self.path_meshes.setText(data.get("meshes_path", ""))
        self.path_viewer.setText(data.get("viewer_path", ""))

    def browse_unit(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Unit File", self.path_unit.text())
        if f: self.path_unit.setText(f)

    def browse_meshes(self):
        d = QFileDialog.getExistingDirectory(self, "Select Meshes Directory", self.path_meshes.text())
        if d: self.path_meshes.setText(d)

    def browse_viewer(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Viewer Exe", self.path_viewer.text(), "Exe (*.exe)")
        if f: self.path_viewer.setText(f)

    def save_and_load(self):
        """Save current inputs from Settings tab and switch to Browser."""
        ui_mode = "SRU" if self.rb_sru.isChecked() else "SR2030"
        
        # Save to config
        self.config.update_game_config(
            ui_mode,
            self.path_unit.text(),
            self.path_meshes.text(),
            self.path_viewer.text()
        )
        
        # Set as the active mode
        self.current_mode = ui_mode
        self.config.set_mode(ui_mode)
        self.sync_combo_box() # Update dropdown
        
        # Load Data and Switch Tab
        self.load_data(switch_tab=True)

    def load_data(self, switch_tab=True):
        """Load data for the ACTIVE profile."""
        data = self.config.get_game_config(self.current_mode)
        path = data.get("unit_file", "")
        
        if not os.path.exists(path):
            QMessageBox.warning(self, "File Not Found", f"Unit file not found for {self.current_mode}:\n{path}\nPlease check Settings.")
            if switch_tab:
                self.tabs.setCurrentIndex(1)
            return
            
        self.units = parse_units_robust(path)
        self.filter_list()
        
        if switch_tab:
            self.tabs.setCurrentIndex(0)

    def filter_list(self):
        txt = self.search_input.text().lower()
        cat = self.cat_combo.currentText().lower()
        sort_mode = self.sort_combo.currentText()
        region_filter = self.region_combo.currentText()
        
        # Skip if separator selected
        if region_filter.startswith("──"):
            self.region_combo.setCurrentIndex(0)
            return
        
        # Extract region code from filter
        region_code = None
        if region_filter != "All Regions":
            # Get the code from our lookup
            regions = self.REGIONS_SRU if self.current_mode == "SRU" else self.REGIONS_SR2030
            for label, code in regions:
                if label == region_filter:
                    if code == "CUSTOM":
                        # Prompt for custom region code
                        from PyQt5.QtWidgets import QInputDialog
                        hint = "Enter region code(s):"
                        if self.current_mode == "SR2030":
                            hint = "Enter region code(s) - case sensitive for SR2030:"
                        text, ok = QInputDialog.getText(self, "Custom Region", hint)
                        if ok and text:
                            region_code = text  # Keep case for SR2030
                        else:
                            self.region_combo.setCurrentIndex(0)
                            return
                    else:
                        region_code = code
                    break
        
        # Filter units
        filtered = []
        for u in self.units:
            if cat != "all" and u.category != cat: 
                continue
            if txt and (txt not in u.name.lower() and txt not in str(u.id)): 
                continue
            if region_code:
                # Check if unit has this region (or * for global)
                if region_code == "*":
                    if "*" not in u.regions and "@" not in u.regions:
                        continue
                elif region_code not in u.regions and "*" not in u.regions and "@" not in u.regions:
                    continue
            filtered.append(u)
        
        # Sort units
        if sort_mode == "ID ↑":
            filtered.sort(key=lambda u: u.id)
        elif sort_mode == "ID ↓":
            filtered.sort(key=lambda u: u.id, reverse=True)
        elif sort_mode == "Name A-Z":
            filtered.sort(key=lambda u: u.name.lower())
        elif sort_mode == "Name Z-A":
            filtered.sort(key=lambda u: u.name.lower(), reverse=True)
        elif sort_mode == "Class":
            filtered.sort(key=lambda u: (u.unit_class, u.name.lower()))
        elif sort_mode == "Picnum":
            filtered.sort(key=lambda u: u.picnum)
        
        # Populate list
        self.unit_list.clear()
        for u in filtered:
            item = QListWidgetItem(f"[{u.id}] {u.name}")
            item.setData(Qt.UserRole, u)
            self.unit_list.addItem(item)
            
        self.lbl_count.setText(f"{len(filtered)} units loaded")

    def search_by_picnum(self):
        """Find all units using a specific picnum (reverse lookup)."""
        picnum_text = self.picnum_input.text().strip()
        
        if not picnum_text:
            return
        
        try:
            target_picnum = int(picnum_text)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid picnum number.")
            return
        
        # Clear other filters
        self.search_input.clear()
        self.cat_combo.setCurrentIndex(0)  # All
        
        # Find matching units
        self.unit_list.clear()
        count = 0
        
        for u in self.units:
            if u.picnum == target_picnum:
                item = QListWidgetItem(f"[{u.id}] {u.name} (class: {u.unit_class})")
                item.setData(Qt.UserRole, u)
                item.setBackground(QColor(70, 100, 70))  # Highlight matches
                self.unit_list.addItem(item)
                count += 1
        
        if count == 0:
            self.lbl_count.setText(f"No units found with picnum {target_picnum}")
            self.txt_textures.setText(f"Picnum {target_picnum} is not used by any unit.")
        else:
            self.lbl_count.setText(f"🎯 {count} unit(s) using picnum {target_picnum}")
            
            # Also show mesh info for this picnum
            data = self.config.get_game_config(self.current_mode)
            mesh_dir = Path(data.get("meshes_path", ""))
            self.check_textures(mesh_dir, target_picnum)

    def clear_picnum_search(self):
        """Clear the picnum search and restore normal list."""
        self.picnum_input.clear()
        self.filter_list()

    def on_selection_changed(self):
        sel = self.unit_list.selectedItems()
        if not sel: return
        
        u = sel[0].data(Qt.UserRole)
        self.lbl_name.setText(u.name)
        self.lbl_id.setText(str(u.id))
        self.lbl_class.setText(f"{u.unit_class} ({u.category.title()})")
        self.lbl_picnum.setText(str(u.picnum))
        
        # Format regions display
        if not u.regions or u.regions in ["*", "@", "*@", "@*"]:
            self.lbl_regions.setText("* (Global/Export)")
        else:
            self.lbl_regions.setText(u.regions)
        
        data = self.config.get_game_config(self.current_mode)
        mesh_dir = Path(data.get("meshes_path", ""))
        
        is_sru = (self.current_mode == "SRU")
        primary_ext = ".x" if is_sru else ".cmo"
        secondary_ext = ".cmo" if is_sru else ".x"
        
        primary_path = mesh_dir / f"UNIT{u.picnum:03d}{primary_ext}"
        secondary_path = mesh_dir / f"UNIT{u.picnum:03d}{secondary_ext}"
        
        final_path = None
        
        if primary_path.exists():
            final_path = primary_path
            self.status_mesh.setText("✅ MESH FOUND")
            self.status_mesh.setStyleSheet("background: #2E7D32; color: white; font-weight: bold;")
            self.lbl_mesh_file.setText(primary_path.name)
            self.btn_view.setEnabled(True)
        elif secondary_path.exists():
            final_path = secondary_path
            self.status_mesh.setText("⚠️ ALT FORMAT FOUND")
            self.status_mesh.setStyleSheet("background: #F9A825; color: black; font-weight: bold;")
            self.lbl_mesh_file.setText(secondary_path.name)
            self.btn_view.setEnabled(True)
        else:
            self.status_mesh.setText("❌ MESH MISSING")
            self.status_mesh.setStyleSheet("background: #C62828; color: white; font-weight: bold;")
            self.lbl_mesh_file.setText(f"UNIT{u.picnum:03d}{primary_ext}")
            self.btn_view.setEnabled(False)
            
        self.selected_mesh_path = final_path
        self.check_textures(mesh_dir, u.picnum)
        
        # Show other units sharing this picnum
        self.show_shared_mesh_info(u.picnum, u.id)

    def check_textures(self, mesh_dir, picnum):
        """Find textures for a given picnum."""
        found = []
        
        # Ensure mesh_dir is a Path
        if isinstance(mesh_dir, str):
            mesh_dir = Path(mesh_dir)
        
        if not mesh_dir.exists():
            self.txt_textures.setText(f"Meshes folder not found:\n{mesh_dir}")
            return
        
        # Multiple patterns to check
        base = f"UNIT{picnum:03d}"
        patterns = [
            f"{base}.dds",           # Default texture
            f"{base}.png",           # PNG variant
        ]
        
        # Regional textures A-Z
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            patterns.append(f"{base}{c}.dds")
            patterns.append(f"{base}{c}.png")
        
        # Check each pattern
        for p in patterns:
            tex_path = mesh_dir / p
            if tex_path.exists():
                found.append(f"✅ {p}")
        
        if found:
            self.txt_textures.setText("\n".join(found))
        else:
            self.txt_textures.setText(f"No textures found for {base}.*")

    def show_shared_mesh_info(self, picnum, current_id):
        """Show info about other units sharing the same mesh."""
        shared = [u for u in self.units if u.picnum == picnum and u.id != current_id]
        
        if shared:
            # Append to texture info
            current_text = self.txt_textures.toPlainText()
            shared_names = [f"  • [{u.id}] {u.name}" for u in shared[:10]]  # Max 10
            
            shared_info = f"\n\n🔗 Shared mesh ({len(shared)} other unit{'s' if len(shared) > 1 else ''}):\n"
            shared_info += "\n".join(shared_names)
            
            if len(shared) > 10:
                shared_info += f"\n  ... and {len(shared) - 10} more"
            
            self.txt_textures.setText(current_text + shared_info)

    def launch_viewer(self):
        """Launch a NEW instance of the viewer without killing old ones."""
        if not self.selected_mesh_path: return
        
        data = self.config.get_game_config(self.current_mode)
        viewer = data.get("viewer_path", "")
        
        if not os.path.exists(viewer):
            QMessageBox.critical(self, "Error", f"Viewer executable not found:\n{viewer}")
            return
            
        try:
            # IMPORTANT: cwd must be the VIEWER's folder, not the mesh folder!
            # The viewer needs to find .spritefont and .dds files in its directory
            viewer_dir = Path(viewer).parent
            proc = subprocess.Popen([viewer, str(self.selected_mesh_path)], cwd=str(viewer_dir))
            self.active_viewers.append(proc)
            self.update_viewer_count()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not launch viewer: {e}")

    def update_viewer_count(self):
        """Update the viewer counter, removing dead processes."""
        self.active_viewers = [p for p in self.active_viewers if p.poll() is None]
        count = len(self.active_viewers)
        self.lbl_viewers.setText(f"Viewers open: {count}")
        if count > 0:
            self.lbl_viewers.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.lbl_viewers.setStyleSheet("color: #888;")

    def open_meshes_folder(self):
        """Open the meshes folder in file explorer."""
        data = self.config.get_game_config(self.current_mode)
        mesh_dir = data.get("meshes_path", "")
        if os.path.exists(mesh_dir):
            os.startfile(mesh_dir)
        else:
            QMessageBox.warning(self, "Error", f"Meshes folder not found:\n{mesh_dir}")

    def close_all_viewers(self):
        """Close all open viewer windows."""
        for proc in self.active_viewers:
            if proc.poll() is None:
                try:
                    proc.kill()
                except:
                    pass
        self.active_viewers.clear()
        self.update_viewer_count()

    def closeEvent(self, event):
        """Clean up all opened viewer windows when closing the main app."""
        for proc in self.active_viewers:
            if proc.poll() is None: # If still running
                try:
                    proc.kill()
                except:
                    pass
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Dark Theme
    p = app.palette()
    p.setColor(p.Window, QColor(53, 53, 53))
    p.setColor(p.WindowText, Qt.white)
    p.setColor(p.Base, QColor(25, 25, 25))
    p.setColor(p.Text, Qt.white)
    p.setColor(p.Button, QColor(53, 53, 53))
    p.setColor(p.ButtonText, Qt.white)
    p.setColor(p.Highlight, QColor(42, 130, 218))
    app.setPalette(p)
    
    w = UnitModelBrowser()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()