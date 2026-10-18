import os
import sys
import json
import time

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QProgressBar, QTableWidget,
    QTableWidgetItem, QComboBox, QGroupBox, QTabWidget, QRadioButton,
    QMessageBox, QDialog, QHeaderView, QSpinBox
)
from PyQt5.QtCore import Qt

from data_collector import ScraperThread, DEFAULT_API_URL
import algorithms

class BenchmarkDialog(QDialog):
    def __init__(self, benchmark_results, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sorting Algorithms Benchmark")
        self.resize(650, 320)

        layout = QVBoxLayout(self)
        label = QLabel("<b>Benchmark Comparison on Selected Column:</b>")
        layout.addWidget(label)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Algorithm", "Time (ms)", "Comparisons", "Swaps"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setRowCount(len(benchmark_results))

        for row_idx, res in enumerate(benchmark_results):
            self.table.setItem(row_idx, 0, QTableWidgetItem(res["name"]))
            self.table.setItem(row_idx, 1, QTableWidgetItem(f"{res['time_ms']:.2f} ms"))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{res['comparisons']:,}"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{res['swaps']:,}"))

        layout.addWidget(self.table)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

class EarthquakeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CS200 DSA Project 1 - USGS Earthquakes Explorer")
        self.resize(1150, 750)

        self.all_data = []
        self.current_data = []
        self.columns = ["id", "place", "magnitude", "time", "depth", "latitude", "longitude", "significance", "status"]
        self.scraper_thread = None
        self.current_page = 1
        self.page_size = 1000

        self.init_ui()
        self.load_cached_data_if_exists()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        scraper_box = QGroupBox("1. Data Scraping / API Collection (15,000+ Entities)")
        scraper_layout = QVBoxLayout(scraper_box)

        url_layout = QHBoxLayout()
        url_label = QLabel("API URL:")
        self.url_input = QLineEdit(DEFAULT_API_URL)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        scraper_layout.addLayout(url_layout)

        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ Start Scraping")
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_resume = QPushButton("⏯ Resume")
        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_load_file = QPushButton("📁 Load Saved JSON")

        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(False)

        self.btn_start.clicked.connect(self.start_scraping)
        self.btn_pause.clicked.connect(self.pause_scraping)
        self.btn_resume.clicked.connect(self.resume_scraping)
        self.btn_stop.clicked.connect(self.stop_scraping)
        self.btn_load_file.clicked.connect(self.load_saved_file)

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_pause)
        btn_layout.addWidget(self.btn_resume)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_load_file)
        scraper_layout.addLayout(btn_layout)

        prog_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 15000)
        self.progress_bar.setValue(0)
        self.status_label = QLabel("Status: Ready to collect data")
        prog_layout.addWidget(self.progress_bar)
        prog_layout.addWidget(self.status_label)
        scraper_layout.addLayout(prog_layout)

        main_layout.addWidget(scraper_box)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels([col.upper() for col in self.columns])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        pagination_layout = QHBoxLayout()

        self.btn_first_page = QPushButton("⏮ First")
        self.btn_prev_page = QPushButton("◀ Prev")
        self.page_info_label = QLabel("Page 1 of 1 | Showing 0 records")
        self.page_info_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #0d47a1; padding: 0 8px;")
        self.btn_next_page = QPushButton("Next ▶")
        self.btn_last_page = QPushButton("Last ⏭")

        for btn in (self.btn_first_page, self.btn_prev_page, self.btn_next_page, self.btn_last_page):
            btn.setFixedHeight(28)
            btn.setFixedWidth(70)

        self.btn_first_page.clicked.connect(self.go_first_page)
        self.btn_prev_page.clicked.connect(self.go_prev_page)
        self.btn_next_page.clicked.connect(self.go_next_page)
        self.btn_last_page.clicked.connect(self.go_last_page)

        jump_label = QLabel("Go to Page:")
        self.page_spin = QSpinBox()
        self.page_spin.setRange(1, 1)
        self.page_spin.setValue(1)
        self.page_spin.setFixedHeight(28)
        self.page_spin.setFixedWidth(60)
        self.page_spin.valueChanged.connect(self.go_to_page)

        page_size_label = QLabel("Page Size:")
        self.page_size_cb = QComboBox()
        self.page_size_cb.addItems(["500", "1000", "2000", "5000"])
        self.page_size_cb.setCurrentText("1000")
        self.page_size_cb.setFixedHeight(28)
        self.page_size_cb.currentTextChanged.connect(self.on_page_size_changed)

        pagination_layout.addWidget(self.btn_first_page)
        pagination_layout.addWidget(self.btn_prev_page)
        pagination_layout.addWidget(self.page_info_label)
        pagination_layout.addWidget(self.btn_next_page)
        pagination_layout.addWidget(self.btn_last_page)
        pagination_layout.addSpacing(15)
        pagination_layout.addWidget(jump_label)
        pagination_layout.addWidget(self.page_spin)
        pagination_layout.addSpacing(10)
        pagination_layout.addWidget(page_size_label)
        pagination_layout.addWidget(self.page_size_cb)
        pagination_layout.addSpacing(15)

        self.instruction_label = QLabel("💡 <i>Paginated view: All 15,000 entities are stored in memory & evaluated in all DSA operations.</i>")
        self.instruction_label.setStyleSheet("color: #455a64; font-size: 11px;")
        pagination_layout.addWidget(self.instruction_label)
        pagination_layout.addStretch()

        main_layout.addLayout(pagination_layout)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_sorting_tab(), "Single Sorting")
        self.tabs.addTab(self.create_searching_tab(), "Searching & Filters")
        self.tabs.addTab(self.create_multisort_tab(), "Multi-Level Sorting")
        self.tabs.addTab(self.create_multisearch_tab(), "Multi-Column Searching")
        main_layout.addWidget(self.tabs)

    def create_sorting_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Column:"))
        self.sort_col_cb = QComboBox()
        self.sort_col_cb.addItems(self.columns)
        controls.addWidget(self.sort_col_cb)

        controls.addWidget(QLabel("Algorithm:"))
        self.sort_algo_cb = QComboBox()
        self.sort_algo_cb.addItems(list(algorithms.SORT_FUNCTIONS.keys()))
        controls.addWidget(self.sort_algo_cb)

        controls.addWidget(QLabel("Order:"))
        self.sort_order_cb = QComboBox()
        self.sort_order_cb.addItems(["Ascending", "Descending"])
        controls.addWidget(self.sort_order_cb)

        controls.addWidget(QLabel("Scope:"))
        self.sort_scope_cb = QComboBox()
        self.sort_scope_cb.addItems(["Current Filtered Data", "Full Dataset"])
        controls.addWidget(self.sort_scope_cb)

        self.btn_sort = QPushButton("Sort Now")
        self.btn_sort.clicked.connect(self.execute_sort)
        controls.addWidget(self.btn_sort)

        self.btn_benchmark = QPushButton("⚡ Benchmark All Algorithms")
        self.btn_benchmark.clicked.connect(self.execute_benchmark)
        controls.addWidget(self.btn_benchmark)

        layout.addLayout(controls)

        self.sort_metrics_label = QLabel("Time: 0.00 ms\nComparisons: 0\nSwaps: 0")
        self.sort_metrics_label.setStyleSheet("font-weight: bold; color: #1a5276;")
        layout.addWidget(self.sort_metrics_label)

        return widget

    def create_searching_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Column:"))
        self.search_col_cb = QComboBox()
        self.search_col_cb.addItems(self.columns)
        controls.addWidget(self.search_col_cb)

        controls.addWidget(QLabel("Algorithm:"))
        self.search_algo_cb = QComboBox()
        self.search_algo_cb.addItems(["Linear Search", "Binary Search"])
        controls.addWidget(self.search_algo_cb)

        controls.addWidget(QLabel("Filter:"))
        self.search_filter_cb = QComboBox()
        self.search_filter_cb.addItems(["contains", "starts_with", "ends_with", "equals", ">", "<"])
        controls.addWidget(self.search_filter_cb)

        self.search_query_input = QLineEdit()
        self.search_query_input.setPlaceholderText("Enter search query...")
        controls.addWidget(self.search_query_input)

        self.btn_search = QPushButton("Search")
        self.btn_search.clicked.connect(self.execute_search)
        controls.addWidget(self.btn_search)

        self.btn_reset_search = QPushButton("Reset / Show All")
        self.btn_reset_search.clicked.connect(self.reset_search)
        controls.addWidget(self.btn_reset_search)

        layout.addLayout(controls)

        self.search_metrics_label = QLabel("Results: All rows shown | Time: 0.00 ms | Comparisons: 0")
        self.search_metrics_label.setStyleSheet("font-weight: bold; color: #1e8449;")
        layout.addWidget(self.search_metrics_label)

        return widget

    def create_multisort_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Primary Column:"))
        self.msort_col1 = QComboBox()
        self.msort_col1.addItems(self.columns)
        self.msort_col1.setCurrentText("magnitude")
        controls.addWidget(self.msort_col1)

        self.msort_order1 = QComboBox()
        self.msort_order1.addItems(["Descending", "Ascending"])
        controls.addWidget(self.msort_order1)

        controls.addWidget(QLabel("Secondary Column:"))
        self.msort_col2 = QComboBox()
        self.msort_col2.addItems(self.columns)
        self.msort_col2.setCurrentText("depth")
        controls.addWidget(self.msort_col2)

        self.msort_order2 = QComboBox()
        self.msort_order2.addItems(["Ascending", "Descending"])
        controls.addWidget(self.msort_order2)

        self.btn_msort = QPushButton("Multi-Level Sort")
        self.btn_msort.clicked.connect(self.execute_multisort)
        controls.addWidget(self.btn_msort)

        layout.addLayout(controls)

        self.msort_metrics_label = QLabel("Time: 0.00 ms\nComparisons: 0\nSwaps: 0")
        self.msort_metrics_label.setStyleSheet("font-weight: bold; color: #7d3c98;")
        layout.addWidget(self.msort_metrics_label)

        return widget

    def create_multisearch_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Filter 1 Column:"))
        self.msearch_col1 = QComboBox()
        self.msearch_col1.addItems(self.columns)
        self.msearch_col1.setCurrentText("place")
        row1.addWidget(self.msearch_col1)

        self.msearch_ftype1 = QComboBox()
        self.msearch_ftype1.addItems(["contains", "starts_with", "ends_with", "equals", ">", "<"])
        row1.addWidget(self.msearch_ftype1)

        self.msearch_q1 = QLineEdit()
        self.msearch_q1.setPlaceholderText("Query 1 (e.g. California)")
        row1.addWidget(self.msearch_q1)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Logical Operator:"))
        self.msearch_op = QComboBox()
        self.msearch_op.addItems(["AND", "OR", "NOT"])
        row2.addWidget(self.msearch_op)

        row2.addWidget(QLabel("Filter 2 Column:"))
        self.msearch_col2 = QComboBox()
        self.msearch_col2.addItems(self.columns)
        self.msearch_col2.setCurrentText("magnitude")
        row2.addWidget(self.msearch_col2)

        self.msearch_ftype2 = QComboBox()
        self.msearch_ftype2.addItems([">", "<", "equals", "contains"])
        row2.addWidget(self.msearch_ftype2)

        self.msearch_q2 = QLineEdit()
        self.msearch_q2.setPlaceholderText("Query 2 (e.g. 2.5)")
        row2.addWidget(self.msearch_q2)

        self.btn_msearch = QPushButton("Multi Search")
        self.btn_msearch.clicked.connect(self.execute_multisearch)
        row2.addWidget(self.btn_msearch)
        layout.addLayout(row2)

        self.msearch_metrics_label = QLabel("Multi-Search Metrics: Time: 0.00 ms | Matches: 0")
        self.msearch_metrics_label.setStyleSheet("font-weight: bold; color: #b9770e;")
        layout.addWidget(self.msearch_metrics_label)

        return widget

    def start_scraping(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please provide a valid API URL.")
            return

        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(True)

        self.all_data = []
        self.current_data = []
        self.table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.current_page = 1
        self.page_info_label.setText("Live Scraping in progress...")

        self.scraper_thread = ScraperThread(base_url=url, target_count=15000)
        self.scraper_thread.progress_signal.connect(self.update_progress)
        self.scraper_thread.status_signal.connect(self.update_status)
        self.scraper_thread.batch_signal.connect(self.append_batch_to_table)
        self.scraper_thread.finished_signal.connect(self.on_scraping_finished)
        self.scraper_thread.start()

    def pause_scraping(self):
        if self.scraper_thread:
            self.scraper_thread.pause()
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(True)

    def resume_scraping(self):
        if self.scraper_thread:
            self.scraper_thread.resume()
            self.btn_pause.setEnabled(True)
            self.btn_resume.setEnabled(False)

    def stop_scraping(self):
        if self.scraper_thread:
            self.scraper_thread.stop()
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(False)
            self.btn_stop.setEnabled(False)

    def update_progress(self, current, total):
        self.progress_bar.setValue(current)

    def update_status(self, text):
        self.status_label.setText(text)

    def append_batch_to_table(self, new_batch):
        start_row = self.table.rowCount()

        if start_row < self.page_size:
            add_count = min(len(new_batch), self.page_size - start_row)
            self.table.setRowCount(start_row + add_count)
            for i in range(add_count):
                row_data = new_batch[i]
                for col_idx, col_name in enumerate(self.columns):
                    val = str(row_data.get(col_name, ""))
                    self.table.setItem(start_row + i, col_idx, QTableWidgetItem(val))

        current_fetched = self.progress_bar.value()
        self.page_info_label.setText(
            f"Live Scraping: {current_fetched:,} / 15,000 fetched | Table previewing first {self.table.rowCount():,} rows"
        )

    def on_scraping_finished(self, all_records):
        self.all_data = all_records
        self.current_data = list(self.all_data)
        self.render_table(self.current_data, reset_page=True)
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(False)
        QMessageBox.information(self, "Finished", f"Data collection complete!\nTotal items: {len(self.all_data):,}")

    def load_cached_data_if_exists(self):
        if os.path.exists("earthquakes.json"):
            self.load_saved_file()

    def load_saved_file(self):
        if not os.path.exists("earthquakes.json"):
            QMessageBox.information(self, "File Not Found", "No saved 'earthquakes.json' found yet. Please click Start Scraping.")
            return
        try:
            with open("earthquakes.json", "r", encoding="utf-8") as f:
                self.all_data = json.load(f)
            self.current_data = list(self.all_data)
            self.progress_bar.setValue(len(self.all_data))
            self.status_label.setText(f"Loaded {len(self.all_data):,} records from local earthquakes.json")
            self.render_table(self.current_data, reset_page=True)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Error loading file: {str(e)}")

    def render_table(self, data_list=None, reset_page=True):
        if data_list is not None:
            self.current_data = data_list
        if reset_page:
            self.current_page = 1

        total_records = len(self.current_data)
        page_size = self.page_size

        if total_records == 0:
            self.table.setRowCount(0)
            self.page_info_label.setText("Page 0 of 0 | Showing 0 records")
            self.btn_first_page.setEnabled(False)
            self.btn_prev_page.setEnabled(False)
            self.btn_next_page.setEnabled(False)
            self.btn_last_page.setEnabled(False)
            self.page_spin.blockSignals(True)
            self.page_spin.setRange(1, 1)
            self.page_spin.setValue(1)
            self.page_spin.setEnabled(False)
            self.page_spin.blockSignals(False)
            return

        total_pages = max(1, (total_records + page_size - 1) // page_size)
        if self.current_page > total_pages:
            self.current_page = total_pages
        if self.current_page < 1:
            self.current_page = 1

        start_idx = (self.current_page - 1) * page_size
        end_idx = min(start_idx + page_size, total_records)
        display_rows = self.current_data[start_idx:end_idx]

        self.table.setRowCount(len(display_rows))
        for row_idx, row in enumerate(display_rows):
            for col_idx, col_name in enumerate(self.columns):
                val = str(row.get(col_name, ""))
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(val))

        self.page_info_label.setText(
            f"Page {self.current_page} of {total_pages} | "
            f"Showing records {start_idx + 1:,} - {end_idx:,} of {total_records:,} (Dataset Total: {len(self.all_data):,})"
        )
        self.btn_first_page.setEnabled(self.current_page > 1)
        self.btn_prev_page.setEnabled(self.current_page > 1)
        self.btn_next_page.setEnabled(self.current_page < total_pages)
        self.btn_last_page.setEnabled(self.current_page < total_pages)

        self.page_spin.blockSignals(True)
        self.page_spin.setEnabled(True)
        self.page_spin.setRange(1, total_pages)
        self.page_spin.setValue(self.current_page)
        self.page_spin.blockSignals(False)

    def go_first_page(self):
        if self.current_page != 1:
            self.current_page = 1
            self.render_table(reset_page=False)

    def go_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.render_table(reset_page=False)

    def go_next_page(self):
        total_records = len(self.current_data)
        total_pages = max(1, (total_records + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages:
            self.current_page += 1
            self.render_table(reset_page=False)

    def go_last_page(self):
        total_records = len(self.current_data)
        total_pages = max(1, (total_records + self.page_size - 1) // self.page_size)
        if self.current_page != total_pages:
            self.current_page = total_pages
            self.render_table(reset_page=False)

    def go_to_page(self, page_num):
        if page_num != self.current_page:
            self.current_page = page_num
            self.render_table(reset_page=False)

    def on_page_size_changed(self, text):
        try:
            self.page_size = int(text)
            self.current_page = 1
            self.render_table(reset_page=False)
        except ValueError:
            pass

    def execute_sort(self):
        if not self.all_data:
            QMessageBox.warning(self, "No Data", "Please collect or load data first.")
            return

        col = self.sort_col_cb.currentText()
        algo = self.sort_algo_cb.currentText()
        ascending = (self.sort_order_cb.currentText() == "Ascending")
        scope = self.sort_scope_cb.currentText()

        source_data = self.current_data if scope == "Current Filtered Data" else self.all_data

        sorted_arr, comparisons, swaps, time_ms = algorithms.runSort(algo, source_data, col, ascending)

        self.sort_metrics_label.setText(
            f"Time: {time_ms:.2f} ms\nComparisons: {comparisons:,}\nSwaps: {swaps:,}"
        )

        self.current_data = sorted_arr
        self.render_table(self.current_data)

    def execute_benchmark(self):
        if not self.all_data:
            QMessageBox.warning(self, "No Data", "Please collect or load data first.")
            return

        col = self.sort_col_cb.currentText()

        sample_size = min(len(self.all_data), 1000)
        sample_data = self.all_data[:sample_size]

        results = []
        for algo_name in algorithms.SORT_FUNCTIONS.keys():
            sorted_arr, comparisons, swaps, time_ms = algorithms.runSort(algo_name, sample_data, col, ascending=True)
            results.append({
                "name": algo_name,
                "time_ms": time_ms,
                "comparisons": comparisons,
                "swaps": swaps
            })

        dialog = BenchmarkDialog(results, self)
        dialog.exec_()

    def execute_search(self):
        if not self.all_data:
            QMessageBox.warning(self, "No Data", "Please collect or load data first.")
            return

        col = self.search_col_cb.currentText()
        algo = self.search_algo_cb.currentText()
        filter_type = self.search_filter_cb.currentText()
        query = self.search_query_input.text().strip()

        if not query:
            QMessageBox.warning(self, "Query Empty", "Please enter a search query.")
            return

        if algo == "Linear Search":
            results, comparisons, time_ms = algorithms.linearSearch(self.all_data, col, query, filter_type)
        else:

            results, comparisons, time_ms = algorithms.binarySearch(self.all_data, col, query)

        self.current_data = results
        self.render_table(self.current_data)
        self.search_metrics_label.setText(
            f"Results: {len(results):,} found | Time: {time_ms:.2f} ms | Comparisons: {comparisons:,}"
        )

    def reset_search(self):
        self.current_data = list(self.all_data)
        self.render_table(self.current_data)
        self.search_metrics_label.setText(f"Results: Reset to all {len(self.all_data):,} records")

    def execute_multisort(self):
        if not self.all_data:
            QMessageBox.warning(self, "No Data", "Please collect or load data first.")
            return

        col1 = self.msort_col1.currentText()
        asc1 = (self.msort_order1.currentText() == "Ascending")
        col2 = self.msort_col2.currentText()
        asc2 = (self.msort_order2.currentText() == "Ascending")

        sorted_arr, comparisons, swaps, time_ms = algorithms.multiLevelSort(
            self.current_data, col1, asc1, col2, asc2
        )

        self.current_data = sorted_arr
        self.render_table(self.current_data)
        self.msort_metrics_label.setText(
            f"Time: {time_ms:.2f} ms\nComparisons: {comparisons:,}\nSwaps: {swaps:,}"
        )

    def execute_multisearch(self):
        if not self.all_data:
            QMessageBox.warning(self, "No Data", "Please collect or load data first.")
            return

        col1 = self.msearch_col1.currentText()
        ftype1 = self.msearch_ftype1.currentText()
        q1 = self.msearch_q1.text().strip()

        op = self.msearch_op.currentText()

        col2 = self.msearch_col2.currentText()
        ftype2 = self.msearch_ftype2.currentText()
        q2 = self.msearch_q2.text().strip()

        results, comparisons, time_ms = algorithms.compositeSearch(
            self.all_data, col1, ftype1, q1, op, col2, ftype2, q2
        )

        self.current_data = results
        self.render_table(self.current_data)
        self.msearch_metrics_label.setText(
            f"Multi-Search Metrics: Time: {time_ms:.2f} ms | Matches: {len(results):,}"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EarthquakeApp()
    window.show()
    sys.exit(app.exec_())
