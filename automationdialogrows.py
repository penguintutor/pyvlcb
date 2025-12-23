from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget, QMessageBox,
    QListWidget, QFormLayout, QLineEdit, QSpinBox, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator

class AutomationDialogRows:
    def __init__(self, parent, layout):
        self.parent = parent
        self.layout = layout
        self.rows = []

        # Labels are created for each row
        # These are initial row labels - but changes based on type selected
        self.labels = [
                QLabel("Step Name:"),
                QLabel("Rule Type:"),
                QLabel("Node:"),
                QLabel("Event:"),
                QLabel("Value:"),
                QLabel("Value2:")
                ]

        # QComboBox are commonly used for most fields so also created as a list
        self.combos = [
                None,   # Step Name is a QLineEdit
                QComboBox(),  # Rule Type
                QComboBox(),  # Node
                QComboBox(),  # Event
                QComboBox(),  # Value
                QComboBox()   # Value2
                ]
        # Line edit is a common alternative
        self.lineedits = [
                QLineEdit(),    # Step Name
                None,           # Rule Type
                None,           # Node
                QLineEdit(),    # Event
                QLineEdit(),    # Value
                QLineEdit()     # Value2
                ]
        # Can sometimes swap out combo for spinbox - eg. loco speed
        self.row5_spinbox = QSpinBox()
        self.row5_spinbox.setRange(0,128)
        self.row5_spinbox.setValue(0)
        # Or swap for a dual spinbox & combo using a Horizontal Layout
        self.row5_inner_widget = QWidget()
        self.row5_inner_layout = QHBoxLayout(self.row5_inner_widget)
        # Set margins to 0 to make it look clean inside the QFormLayout row
        self.row5_inner_layout.setContentsMargins(0, 0, 0, 0)
        self.row5_inner_spinbox = QSpinBox()
        self.row5_inner_spinbox.setRange(1, 18)
        self.row5_inner_spinbox.setValue(1)
        self.row5_inner_combo = QComboBox()
        self.row5_inner_combo.addItems(["On", "Off"])
        # Add widgets to the QHBoxLayout
        self.row5_inner_layout.addWidget(self.row5_inner_spinbox)
        #self.row5_inner_layout.addWidget(QLabel("Units:")) # Adding a small label for context
        self.row5_inner_layout.addWidget(self.row5_inner_combo)
        # Not added to the row - that is done through add_custom_widgets method

        # Rule type list is fixed
        self.rule_types = ["Select Type", "VLCB", "Loco", "App", "User Interface"]
        self.combos[1].addItems(self.rule_types)

        # min row height applied to all the labels to keep spacing if set to ""
        min_row_height = 30

        # Create the rows in the layout
        # If combo defined then use that - else use lineedit
        for i in range(len(self.labels)):
            if self.combos[i] != None:
                self.layout.addRow(self.labels[i], self.combos[i])
            elif self.lineedits[i] != None:
                self.layout.addRow(self.labels[i], self.lineedits[i])
            # Set minimum height for label to keep spacing consistent
            self.labels[i].setMinimumHeight(min_row_height)
            self.rows.append(i)

        # Spacer
        spacer_widget = QWidget()
        spacer_widget.setFixedHeight(30) # Set a fixed height for the gap
        self.layout.addRow(spacer_widget)

        #Add signal handling - all point to update_rows which will manage changes
        for combo in self.combos:
            if combo != None:
                combo.currentIndexChanged.connect(self.parent.update_rows)
        # Todo add update_rows to parent

    def enable_combo_signals(self, enable=True):
        """Enable or disable signals for all combo boxes."""
        for combo in self.combos:
            if combo is not None:
                if enable:
                    combo.blockSignals(False)
                else:
                    combo.blockSignals(True)

    def show_hide_row (self, row, show=True, label=None):
        """Set visibility for the widgets in the specified form row.

        Keeps the label visible at all times. When hiding a row we set the
        label's text to an empty string (but keep it visible to preserve
        spacing). When restoring if label is provided then that is used
        as the text.
        
        Handles both single widgets and nested layouts in the FieldRole.
        """
        #print (f"Show/hide row {row} show={show} label={label}")

        # label item doesn't change so retrive from the labels
        label_item = self.labels[row]
        field_item = self.layout.itemAt(row, QFormLayout.FieldRole)


        #print (f"Label item: {label_item}, Field item: {field_item}")

        if field_item is None:
            print("No item in FieldRole for row", row)
        else:
            w = field_item.widget()
            if w is not None:
                # Python class name and Qt/C++ class name
                #print("Widget:", w.__class__.__name__, "/", w.metaObject().className())
                # Use isinstance checks to branch
                if isinstance(w, QComboBox):
                    #print("It's a QComboBox")
                    pass
                elif isinstance(w, QLineEdit):
                    #print("It's a QLineEdit")
                    pass
                else:
                    #print("Other widget type")
                    l = w.layout()
                    if l is not None:
                        #print("Layout:", l.__class__.__name__)
                        # You can inspect children
                        for i in range(l.count()):
                            ci = l.itemAt(i)
                            cw = ci.widget()
                            print(" child:", (cw.__class__.__name__ if cw else None))

        if show == False:
            label_item.setText("")
        elif label is not None:
            label_item.setText(label)
        
        # Handle field_item: it could be a widget or a nested layout
        if field_item is None:
            return
        
        field_widget = field_item.widget()
        if field_widget is not None:
            # It's a single widget (e.g., QComboBox, QLineEdit)
            #field_widget.setVisible(show)
            # Also check if it's a layout in which case hide / show all
            field_layout = field_widget.layout()
            if field_layout is not None:
                #print (f"Field layout for {row}, {field_layout}, {show}")
                # Hide/show all child widgets in the layout
                for idx in range(field_layout.count()):
                    child_item = field_layout.itemAt(idx)
                    #print (f"Child is {child_item}")
                    if child_item is None:
                        continue
                    child_widget = child_item.widget()
                    print (f"Child widget is {child_widget}")
                    if child_widget is not None:
                        child_widget.setVisible(show)
            # Make the widget hidden / visible
            field_widget.setVisible(show)

    def get_type_text (self):
        # Determine form type based on Rule Type combo selection
        rule_type = self.combos[1].currentText()
        if rule_type == "Select Type":
            return None
        return rule_type

    def get_combo_text (self, row):
        """Get the current text of the combo box in the specified row."""
        combo = self.combos[row]
        if combo is not None and combo.currentText() != "" and combo.currentText() != "N/A":
            return combo.currentText()
        # return empty string for blank and NA
        return ""

    def set_field_type (self, row, field_type):
        """Set the widget type in the specified row: 'combo', 'lineedit', or 'spinbox'."""
        # If already this type then ignore
        current_type = self.get_field_type(row)
        if current_type == field_type:
            return
        elif current_type == "custom":
            # If current is custom then need to remove nested layout first
            self.remove_custom_widgets (row)
        else:
            # Remove existing widget
            field_item = self.layout.itemAt(row, QFormLayout.FieldRole)
            if field_item is not None:
                existing_widget = field_item.widget()
                if existing_widget is not None:
                    self.layout.removeWidget(existing_widget)
                    existing_widget.setParent(None)  # Remove from layout

        # Add new widget based on field_type
        if field_type == 'combo':
            self.layout.addWidget(self.combos[row], row, 1)
        elif field_type == 'lineedit':
            self.layout.addWidget(self.lineedits[row], row, 1)
        elif field_type == 'spinbox':
            # currently custom - may add later
            print(f"Spinbox not defined for row {row}")
        elif field_type == 'custom':
            # custom needs to be added separately
            pass
        else:
            print(f"Unknown field type '{field_type}' for row {row}")

    def remove_custom_widgets (self, row):
        """Remove custom nested widgets from the specified row."""
        # This assumes set custom widget for the row
        # Update as requried if more flexibility require in future
        # Only the top widget is actually removed, the rest are set to hidden
        if row == 5:
            self.row5_spinbox.setVisible(False)
            self.row5_inner_combo.setVisible(False)

            self.layout.removeWidget(self.row5_inner_widget)
            self.row5_inner_widget.setParent(None)  # Remove from layout
        else:
            print(f"No custom widgets defined for row {row}")

    def add_custom_widgets (self, row):
        # Note that this is hard coded - can update in future if required
        if row == 5:
            self.layout.addWidget(self.row5_inner_widget, row, 1)
        else:
            print(f"No custom widgets defined for row {row}")

    def get_field_type (self, row):
        """Get the type of field in the specified row: 'combo', 'lineedit', or 'spinbox'."""
        field_item = self.layout.itemAt(row, QFormLayout.FieldRole)
        field_widget = field_item.widget()
        if field_widget is not None:
            if isinstance(field_widget, QComboBox):
                return 'combo'
            elif isinstance(field_widget, QLineEdit):
                return 'lineedit'
            elif isinstance(field_widget, QSpinBox):
                return 'spinbox'
            # If QWidget then nested so return custom
            elif isinstance(field_widget, QWidget):
                return 'custom'
        return None

    def combo_add_items (self, row, items, keep_existing=False):
        """Add items to the combo box in the specified row."""
        combo = self.combos[row]
        if combo is not None:
            if not keep_existing:
                combo.clear()
            combo.addItems(items)

    def set_combo_text (self, row, entry):
        """Set the current entry of the combo box in the specified row."""
        combo = self.combos[row]
        if combo is not None:
            index = combo.findText(entry)
            if index != -1:
                combo.setCurrentIndex(index)
            else:
                print(f"Entry '{entry}' not found in combo box at row {row}")

    def set_lineedit_text (self, row, text):
        """Set the text of the line edit in the specified row."""
        lineedit = self.lineedits[row]
        if lineedit is not None:
            lineedit.setText(text)

    def get_linedit_text (self, row):
        """Get the text of the line edit in the specified row."""
        lineedit = self.lineedits[row]
        if lineedit is not None:
            return lineedit.text()
        return ""

    # ToDo
    # To add to event selection for DCC ID
    # Add validator to accept only integers 1-9999
    #    self.event_edit.setValidator(QIntValidator(1, 9999, self.event_edit))
    #    # Add label if loco id selected
    #    self.event_alt_label = QLabel("Allocated when run")