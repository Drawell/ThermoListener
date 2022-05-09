from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QWidget, QHBoxLayout

from DB.dao import SQLiteDAO


class SessionListWidget(QTableWidget):
    def __init__(self, parent, dao: SQLiteDAO, on_show_session):
        super().__init__(parent)
        self.dao = dao
        self.on_show_session = on_show_session

        self.setColumnCount(5)
        self.setHorizontalHeaderItem(0, QTableWidgetItem('Действия'))
        self.setHorizontalHeaderItem(1, QTableWidgetItem('Название'))
        self.setHorizontalHeaderItem(2, QTableWidgetItem('Режим'))
        self.setHorizontalHeaderItem(3, QTableWidgetItem('Температура'))
        self.setHorizontalHeaderItem(4, QTableWidgetItem('Начало'))
        # self.key.connect(self.on_key_press)
        self.cellChanged.connect(self.cell_changed)
        self._refreshing = False
        self._sess_by_row = []

    def refresh(self):
        self._refreshing = True
        sessions = self.dao.get_all_sessions()

        self.setRowCount(len(sessions))
        self._sess_by_row = []
        for idx, sess in enumerate(sessions):
            self._sess_by_row.append(sess)

            self._add_action_widget(idx, sess)

            name_item = QTableWidgetItem(sess.name)
            # name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.setItem(idx, 1, name_item)

            mode_name_item = QTableWidgetItem(sess.mode_name)
            mode_name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.setItem(idx, 2, mode_name_item)

            temp_item = QTableWidgetItem(str(sess.maintaining_temperature))
            temp_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.setItem(idx, 3, temp_item)

            start_item = QTableWidgetItem(sess.start_date.strftime('%H:%M %d.%m.%Y'))
            start_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.setItem(idx, 4, start_item)

            self._refreshing = False

    def _add_action_widget(self, idx, session):
        action_widget = QWidget(self)
        layout = QHBoxLayout(action_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        action_widget.setLayout(layout)

        btn_show = QPushButton(self)
        btn_show.setText('?')
        btn_show.clicked.connect(lambda: self.on_show_session(session))
        layout.addWidget(btn_show)

        btn_delete = QPushButton(self)
        btn_delete.setText('Х')

        def remove_session():
            self.dao.remove_session(session)
            self.refresh()

        btn_delete.clicked.connect(remove_session)
        layout.addWidget(btn_delete)

        self.setCellWidget(idx, 0, action_widget)

    def cell_changed(self, row, col):
        item = self.currentItem()
        if not self._refreshing and item is not None:
            text = item.text()
            sess = self._sess_by_row[row]
            sess.name = text
            self.dao.update_session(sess)
